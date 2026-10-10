import os
import re
import secrets
import sqlite3
import time
from datetime import datetime
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, send_from_directory, session, url_for)
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

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

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-moi-en-prod"),
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100 Mo par envoi
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
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
"""

with sqlite3.connect(DB_PATH) as _c:
    _c.executescript(SCHEMA)


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


@app.route("/media/<name>")
def media(name):
    db = get_db()
    e = db.execute("SELECT user_id, is_public FROM entries WHERE media = ?",
                   (name,)).fetchone()
    if e:
        if not e["is_public"] and not (g.user and g.user["id"] == e["user_id"]):
            abort(404)
    elif not db.execute("SELECT 1 FROM cards WHERE media = ?", (name,)).fetchone():
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
                 1 if request.form.get("is_public") else 0, int(time.time())))
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


if __name__ == "__main__":
    app.run(debug=True)
