import os
import re
import secrets
import sqlite3
import time
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse

from jinja2 import DictLoader
from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, send_from_directory, session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

from pages import TEMPLATES

# Sur Railway : monte un Volume sur /data et mets DATA_DIR=/data
DATA_DIR = os.environ.get("DATA_DIR", "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
DB_PATH = os.path.join(DATA_DIR, "site.db")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED = {"mp3", "wav", "ogg", "m4a", "aac", "webm", "mp4", "mov", "m4v"}
VIDEO_EXT = {"mp4", "mov", "m4v"}
THEMES = {
    "sakura": "🌸 Sakura",
    "gamer": "🎮 Gamer",
    "etoile": "⭐ Étoile",
    "gateau": "🎂 Gâteau",
}

app = Flask(__name__, static_folder=None)
app.jinja_env.loader = DictLoader(TEMPLATES)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-moi-en-prod"),
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100 Mo par envoi
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # cookie réservé au HTTPS une fois en ligne sur Railway (pas en local)
    SESSION_COOKIE_SECURE=bool(os.environ.get("RAILWAY_ENVIRONMENT")),
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL COLLATE NOCASE,
    password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT, body TEXT, media TEXT, media_kind TEXT,
    is_public INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    recipient TEXT NOT NULL, message TEXT NOT NULL,
    media TEXT, media_kind TEXT,
    theme TEXT NOT NULL DEFAULT 'sakura',
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS asks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    recipient TEXT NOT NULL, questions TEXT NOT NULL, final_msg TEXT NOT NULL,
    done_at INTEGER,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    body TEXT NOT NULL,
    created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS friendships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER NOT NULL,
    addressee_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at INTEGER NOT NULL,
    UNIQUE (requester_id, addressee_id)
);
"""

with sqlite3.connect(DB_PATH) as _c:
    _c.executescript(SCHEMA)
    # anciennes bases : ajoute la bio et la photo de profil si elles manquent
    _cols = {r[1] for r in _c.execute("PRAGMA table_info(users)")}
    for _name in ("bio", "avatar"):
        if _name not in _cols:
            _c.execute(f"ALTER TABLE users ADD COLUMN {_name} TEXT")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db:
        db.close()


@app.before_request
def load_user():
    uid = session.get("uid")
    g.user = None
    if uid:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id=?", (uid,)).fetchone()


@app.before_request
def block_cross_site_posts():
    """Refuse les envois de formulaires venant d'un autre site (protection CSRF)."""
    if request.method != "POST":
        return None
    if request.headers.get("Sec-Fetch-Site") == "cross-site":
        abort(403)
    origin = request.headers.get("Origin")
    if origin and origin != "null":
        hosts = {request.host, request.headers.get("Host"),
                 request.headers.get("X-Forwarded-Host")}
        if urlparse(origin).netloc not in hosts:
            abort(403)
    return None


@app.errorhandler(403)
def forbidden(_e):
    return "Action refusée.", 403


@app.context_processor
def inject():
    return {
        "user": g.get("user"),
        "site_name": os.environ.get("SITE_NAME", "Sakura Log"),
        "themes": THEMES,
    }


@app.template_filter("date")
def fmt_date(ts):
    return datetime.fromtimestamp(ts).strftime("%d/%m/%Y")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            flash("Connecte-toi pour continuer.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def save_media(file):
    """Enregistre un fichier audio/vidéo. Renvoie (nom, type) ou (None, None)."""
    if not file or not file.filename:
        return None, None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED:
        raise ValueError("Format non accepté. Utilise mp3, wav, ogg, m4a, aac, webm, mp4 ou mov.")
    is_video = (file.mimetype or "").startswith("video/") or ext in VIDEO_EXT
    name = f"{secrets.token_hex(16)}.{ext}"
    file.save(os.path.join(UPLOAD_DIR, name))
    return name, ("video" if is_video else "audio")


def remove_media(name):
    if name:
        try:
            os.remove(os.path.join(UPLOAD_DIR, name))
        except OSError:
            pass


@app.errorhandler(413)
def too_big(_e):
    return "Fichier trop lourd (100 Mo maximum).", 413


# ---------- Pages publiques ----------

@app.route("/")
def index():
    entries = get_db().execute(
        "SELECT entries.*, users.username FROM entries "
        "JOIN users ON users.id = entries.user_id "
        "WHERE is_public = 1 ORDER BY created_at DESC LIMIT 12").fetchall()
    return render_template("index.html", entries=entries)


@app.route("/c/<token>")
def card_view(token):
    card = get_db().execute(
        "SELECT cards.*, users.username AS author FROM cards "
        "JOIN users ON users.id = cards.user_id WHERE token = ?",
        (token,)).fetchone()
    if not card:
        abort(404)
    emoji = THEMES.get(card["theme"], THEMES["sakura"]).split()[0]
    return render_template("card_view.html", card=card, emoji=emoji)


def can_see(owner_id, level):
    """level : 0 = privé, 1 = public, 2 = amis seulement."""
    if level == 1:
        return True
    if not g.user:
        return False
    if g.user["id"] == owner_id:
        return True
    return level == 2 and relation(g.user["id"], owner_id)[0] == "friends"


@app.route("/media/<name>")
def media(name):
    db = get_db()
    e = db.execute("SELECT user_id, is_public FROM entries WHERE media = ?",
                   (name,)).fetchone()
    if e:
        if not can_see(e["user_id"], e["is_public"]):
            abort(404)
    elif not (db.execute("SELECT 1 FROM cards WHERE media = ?", (name,)).fetchone()
              or db.execute("SELECT 1 FROM users WHERE avatar = ?", (name,)).fetchone()):
        abort(404)
    return send_from_directory(UPLOAD_DIR, name, conditional=True)


# ---------- Compte ----------

@app.route("/inscription", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
            flash("Pseudo : 3 à 20 caractères, lettres, chiffres ou _.")
        elif len(password) < 6:
            flash("Mot de passe : 6 caractères minimum.")
        else:
            db = get_db()
            try:
                cur = db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)))
                db.commit()
            except sqlite3.IntegrityError:
                flash("Ce pseudo est déjà pris.")
            else:
                session.clear()
                session["uid"] = cur.lastrowid
                return redirect(url_for("journal"))
    return render_template("auth.html", mode="register")


@app.route("/connexion", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        row = get_db().execute(
            "SELECT * FROM users WHERE username = ?",
            (request.form.get("username", "").strip(),)).fetchone()
        if row and check_password_hash(row["password_hash"],
                                       request.form.get("password", "")):
            session.clear()
            session["uid"] = row["id"]
            return redirect(url_for("journal"))
        flash("Pseudo ou mot de passe incorrect.")
    return render_template("auth.html", mode="login")


@app.post("/deconnexion")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- Journal de bord ----------

@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    db = get_db()
    if request.method == "POST":
        title = request.form.get("title", "").strip()[:120]
        body = request.form.get("body", "").strip()[:5000]
        try:
            media_name, kind = save_media(request.files.get("media"))
        except ValueError as err:
            flash(str(err))
            return redirect(url_for("journal"))
        if not (title or body or media_name):
            flash("Ajoute au moins un titre, un texte ou un fichier.")
        else:
            db.execute(
                "INSERT INTO entries (user_id, title, body, media, media_kind, "
                "is_public, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (g.user["id"], title, body, media_name, kind,
                 visibility(), int(time.time())))
            db.commit()
            flash("Page ajoutée ✨")
        return redirect(url_for("journal"))
    entries = db.execute(
        "SELECT * FROM entries WHERE user_id = ? ORDER BY created_at DESC",
        (g.user["id"],)).fetchall()
    return render_template("journal.html", entries=entries)


@app.post("/journal/<int:eid>/supprimer")
@login_required
def delete_entry(eid):
    db = get_db()
    row = db.execute("SELECT media FROM entries WHERE id = ? AND user_id = ?",
                     (eid, g.user["id"])).fetchone()
    if row:
        remove_media(row["media"])
        db.execute("DELETE FROM entries WHERE id = ?", (eid,))
        db.commit()
    return redirect(url_for("journal"))


# ---------- Cartes d'anniversaire ----------

@app.route("/cartes", methods=["GET", "POST"])
@login_required
def cards():
    db = get_db()
    if request.method == "POST":
        recipient = request.form.get("recipient", "").strip()[:60]
        message = request.form.get("message", "").strip()[:3000]
        theme = request.form.get("theme", "sakura")
        if theme not in THEMES:
            theme = "sakura"
        if not recipient or not message:
            flash("Il faut un prénom et un message.")
            return redirect(url_for("cards"))
        try:
            media_name, kind = save_media(request.files.get("media"))
        except ValueError as err:
            flash(str(err))
            return redirect(url_for("cards"))
        db.execute(
            "INSERT INTO cards (user_id, token, recipient, message, media, "
            "media_kind, theme, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (g.user["id"], secrets.token_urlsafe(8), recipient, message,
             media_name, kind, theme, int(time.time())))
        db.commit()
        flash("Carte créée 🎂 Copie son lien pour l'envoyer.")
        return redirect(url_for("cards"))
    rows = db.execute(
        "SELECT * FROM cards WHERE user_id = ? ORDER BY created_at DESC",
        (g.user["id"],)).fetchall()
    return render_template("cards.html", cards=rows)


@app.post("/cartes/<int:cid>/supprimer")
@login_required
def delete_card(cid):
    db = get_db()
    row = db.execute("SELECT media FROM cards WHERE id = ? AND user_id = ?",
                     (cid, g.user["id"])).fetchone()
    if row:
        remove_media(row["media"])
        db.execute("DELETE FROM cards WHERE id = ?", (cid,))
        db.commit()
    return redirect(url_for("cards"))


# ---------- Demandes (le bouton « Non » s'enfuit) ----------

@app.route("/demandes", methods=["GET", "POST"])
@login_required
def asks():
    db = get_db()
    if request.method == "POST":
        recipient = request.form.get("recipient", "").strip()[:60]
        lines = [l.strip()[:200] for l in request.form.get("questions", "").splitlines() if l.strip()][:8]
        final = request.form.get("final", "").strip()[:200] or "Merci d'avoir dit oui 💖"
        if not recipient or not lines:
            flash("Il faut un prénom et au moins une question.")
        else:
            db.execute(
                "INSERT INTO asks (user_id, token, recipient, questions, final_msg, "
                "created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (g.user["id"], secrets.token_urlsafe(8), recipient,
                 "\n".join(lines), final, int(time.time())))
            db.commit()
            flash("Demande créée 💌 Copie son lien pour l'envoyer.")
        return redirect(url_for("asks"))
    rows = db.execute("SELECT * FROM asks WHERE user_id = ? ORDER BY created_at DESC",
                      (g.user["id"],)).fetchall()
    return render_template("asks.html", rows=rows)


@app.route("/d/<token>")
def ask_view(token):
    ask = get_db().execute(
        "SELECT asks.*, users.username AS author FROM asks "
        "JOIN users ON users.id = asks.user_id WHERE token = ?", (token,)).fetchone()
    if not ask:
        abort(404)
    return render_template("ask_view.html", ask=ask, questions=ask["questions"].split("\n"))


@app.post("/d/<token>/oui")
def ask_done(token):
    db = get_db()
    db.execute("UPDATE asks SET done_at = ? WHERE token = ? AND done_at IS NULL",
               (int(time.time()), token))
    db.commit()
    return "", 204


@app.post("/demandes/<int:aid>/supprimer")
@login_required
def delete_ask(aid):
    db = get_db()
    db.execute("DELETE FROM asks WHERE id = ? AND user_id = ?", (aid, g.user["id"]))
    db.commit()
    return redirect(url_for("asks"))


# ---------- Messages anonymes ----------

_hits = {}


def too_many(ip, limit=5, window=60):
    now = time.time()
    hits = [t for t in _hits.get(ip, []) if now - t < window]
    blocked = len(hits) >= limit
    if not blocked:
        hits.append(now)
    _hits[ip] = hits
    return blocked


@app.route("/m/<username>", methods=["GET", "POST"])
def anon(username):
    db = get_db()
    target = db.execute("SELECT id, username FROM users WHERE username = ?",
                        (username,)).fetchone()
    if not target:
        abort(404)
    if request.method == "POST":
        body = request.form.get("body", "").strip()[:500]
        if request.form.get("site"):  # champ piège pour les robots
            pass
        elif not body:
            flash("Écris un message avant d'envoyer.")
        elif too_many(request.remote_addr):
            flash("Doucement ! Réessaie dans une minute.")
        else:
            db.execute("INSERT INTO messages (user_id, body, created_at) VALUES (?, ?, ?)",
                       (target["id"], body, int(time.time())))
            db.commit()
            flash("Message envoyé en anonyme 🕊️")
        return redirect(url_for("anon", username=target["username"]))
    return render_template("anon.html", target=target)


@app.route("/messages")
@login_required
def inbox():
    rows = get_db().execute("SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC",
                            (g.user["id"],)).fetchall()
    return render_template("messages.html", rows=rows)


@app.post("/messages/<int:mid>/supprimer")
@login_required
def delete_message(mid):
    db = get_db()
    db.execute("DELETE FROM messages WHERE id = ? AND user_id = ?", (mid, g.user["id"]))
    db.commit()
    return redirect(url_for("inbox"))


# ---------- Profils et amis ----------

IMG_EXT = {"jpg", "jpeg", "png", "gif", "webp"}


def visibility():
    v = request.form.get("is_public", "0")
    return int(v) if v in ("0", "1", "2") else 0


def relation(me, other):
    """Renvoie (état, ligne) : none, sent, received ou friends."""
    row = get_db().execute(
        "SELECT * FROM friendships WHERE (requester_id = ? AND addressee_id = ?) "
        "OR (requester_id = ? AND addressee_id = ?)", (me, other, other, me)).fetchone()
    if not row:
        return "none", None
    if row["status"] == "accepted":
        return "friends", row
    return ("sent" if row["requester_id"] == me else "received"), row


def user_or_404(username):
    u = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not u:
        abort(404)
    return u


def save_avatar(file):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in IMG_EXT:
        raise ValueError("Photo : jpg, png, gif ou webp.")
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 3 * 1024 * 1024:
        raise ValueError("Photo trop lourde (3 Mo maximum).")
    name = f"{secrets.token_hex(16)}.{ext}"
    file.save(os.path.join(UPLOAD_DIR, name))
    return name


def back(username):
    if request.form.get("back") == "friends":
        return redirect(url_for("friends"))
    return redirect(url_for("profile", username=username))


@app.route("/u/<username>")
def profile(username):
    owner = user_or_404(username)
    db = get_db()
    me = g.user["id"] if g.user else None
    if me is None:
        rel = "anon"
    elif me == owner["id"]:
        rel = "self"
    else:
        rel = relation(me, owner["id"])[0]
    levels = {"self": (0, 1, 2), "friends": (1, 2)}.get(rel, (1,))
    marks = ",".join("?" * len(levels))
    entries = db.execute(
        f"SELECT * FROM entries WHERE user_id = ? AND is_public IN ({marks}) "
        "ORDER BY created_at DESC LIMIT 30", (owner["id"], *levels)).fetchall()
    nfriends = db.execute(
        "SELECT COUNT(*) FROM friendships WHERE status = 'accepted' "
        "AND (requester_id = ? OR addressee_id = ?)", (owner["id"], owner["id"])).fetchone()[0]
    return render_template("profile.html", owner=owner, rel=rel,
                           entries=entries, nfriends=nfriends)


@app.route("/profil", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        bio = request.form.get("bio", "").strip()[:200]
        try:
            avatar = save_avatar(request.files.get("avatar"))
        except ValueError as err:
            flash(str(err))
            return redirect(url_for("edit_profile"))
        db = get_db()
        if avatar:
            remove_media(g.user["avatar"])
            db.execute("UPDATE users SET bio = ?, avatar = ? WHERE id = ?",
                       (bio, avatar, g.user["id"]))
        else:
            db.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, g.user["id"]))
        db.commit()
        flash("Profil mis à jour ✨")
        return redirect(url_for("profile", username=g.user["username"]))
    return render_template("edit_profile.html")


@app.route("/amis")
@login_required
def friends():
    db = get_db()
    me = g.user["id"]
    q = request.args.get("q", "").strip()[:20]
    found = []
    if q:
        found = db.execute(
            "SELECT username, avatar FROM users WHERE username LIKE ? AND id != ? "
            "ORDER BY username LIMIT 20", (f"%{q}%", me)).fetchall()
    received = db.execute(
        "SELECT u.username, u.avatar FROM friendships f JOIN users u ON u.id = f.requester_id "
        "WHERE f.addressee_id = ? AND f.status = 'pending' ORDER BY f.created_at DESC",
        (me,)).fetchall()
    sent = db.execute(
        "SELECT u.username, u.avatar FROM friendships f JOIN users u ON u.id = f.addressee_id "
        "WHERE f.requester_id = ? AND f.status = 'pending' ORDER BY f.created_at DESC",
        (me,)).fetchall()
    friends_list = db.execute(
        "SELECT u.username, u.avatar FROM friendships f JOIN users u ON u.id = "
        "CASE WHEN f.requester_id = ? THEN f.addressee_id ELSE f.requester_id END "
        "WHERE f.status = 'accepted' AND (f.requester_id = ? OR f.addressee_id = ?) "
        "ORDER BY u.username", (me, me, me)).fetchall()
    return render_template("friends.html", q=q, found=found, received=received,
                           sent=sent, friends_list=friends_list)


@app.post("/amis/ajouter/<username>")
@login_required
def friend_add(username):
    other = user_or_404(username)
    me = g.user["id"]
    if other["id"] != me:
        db = get_db()
        rel, row = relation(me, other["id"])
        if rel == "none":
            if too_many(f"ami{me}", limit=20, window=3600):
                flash("Trop de demandes d'un coup, réessaie plus tard.")
            else:
                db.execute(
                    "INSERT INTO friendships (requester_id, addressee_id, status, created_at) "
                    "VALUES (?, ?, 'pending', ?)", (me, other["id"], int(time.time())))
                flash("Demande envoyée 💌")
        elif rel == "received":
            db.execute("UPDATE friendships SET status = 'accepted' WHERE id = ?", (row["id"],))
            flash("Vous êtes amis 🎉")
        db.commit()
    return back(other["username"])


@app.post("/amis/retirer/<username>")
@login_required
def friend_remove(username):
    """Refuse, annule une demande ou retire un ami."""
    other = user_or_404(username)
    rel, row = relation(g.user["id"], other["id"])
    if row:
        db = get_db()
        db.execute("DELETE FROM friendships WHERE id = ?", (row["id"],))
        db.commit()
    return back(other["username"])


if __name__ == "__main__":
    app.run(debug=True)
