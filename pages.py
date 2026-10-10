"""Toutes les pages HTML du site, dans un seul fichier (pas de sous-dossier à créer)."""

TEMPLATES = {
    "_macros.html": r"""{% macro player(kind, name) %}
{% if name %}
  {% if kind == 'video' %}
    <video controls playsinline preload="metadata" src="{{ url_for('media', name=name) }}"></video>
  {% else %}
    <audio controls preload="metadata" src="{{ url_for('media', name=name) }}"></audio>
  {% endif %}
{% endif %}
{% endmacro %}
""",
    "auth.html": r"""{% extends "base.html" %}
{% block title %}{{ "Créer un compte" if mode == "register" else "Connexion" }}{% endblock %}
{% block content %}
<form class="panel narrow" method="post">
  <h1>{{ "Créer un compte" if mode == "register" else "Connexion" }}</h1>
  <label>Pseudo <input name="username" required minlength="3" maxlength="20" autocomplete="username"></label>
  <label>Mot de passe <input name="password" type="password" required minlength="6" autocomplete="{{ 'new-password' if mode == 'register' else 'current-password' }}"></label>
  <button class="btn">{{ "Créer mon compte" if mode == "register" else "Me connecter" }}</button>
  <p class="alt">
    {% if mode == "register" %}Déjà un compte ? <a href="{{ url_for('login') }}">Connexion</a>
    {% else %}Pas de compte ? <a href="{{ url_for('register') }}">Inscription</a>{% endif %}
  </p>
</form>
{% endblock %}
""",
    "base.html": r"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{{ site_name }}{% endblock %}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
{% raw %}
:root{
  --milk:#FFF4F8; --dot:#FFD9E6; --sakura:#FFC2D6; --berry:#C2306A;
  --plum:#3F1D38; --mint:#C9F0E1; --white:#fff;
}
.theme-gamer{--dot:#E4D9FF; --sakura:#CDB8FF}
.theme-etoile{--dot:#FFF0BF; --sakura:#FFE08A}
.theme-gateau{--dot:#D8F5E9; --sakura:#9EE3C8}
*{box-sizing:border-box}
body{
  margin:0; font-family:Nunito,system-ui,sans-serif; font-size:1.05rem; line-height:1.6;
  color:var(--plum); background-color:var(--milk);
  background-image:radial-gradient(var(--dot) 2px,transparent 2px); background-size:26px 26px;
}
h1,h2,h3,.logo,.btn{font-family:Fredoka,Nunito,sans-serif}
h1{font-size:clamp(1.7rem,6vw,2.4rem);line-height:1.15;margin:0 0 .6rem}
h2{font-size:1.4rem;margin:0}
h3{font-size:1.2rem;margin:0}
a{color:var(--berry);font-weight:700}
:focus-visible{outline:3px solid var(--plum);outline-offset:2px}
.top{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:center;justify-content:space-between;max-width:760px;margin:0 auto;padding:1rem}
.logo{font-size:1.5rem;font-weight:700;text-decoration:none;color:var(--plum)}
nav{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center}
nav form{margin:0}
main{max-width:760px;margin:0 auto;padding:0 1rem 3rem}
.panel{background:var(--white);border:2.5px solid var(--plum);border-radius:22px;box-shadow:6px 6px 0 var(--sakura);padding:1.25rem;margin:0 0 1.5rem}
.narrow{max-width:420px;margin:1rem auto}
.hero p{max-width:60ch}
label{display:block;font-weight:700;margin-bottom:1rem}
input:not([type=checkbox]):not([type=file]),textarea,select{
  display:block;width:100%;margin-top:.3rem;padding:.6rem .8rem;font:inherit;font-weight:400;
  color:var(--plum);background:#fff;border:2px solid var(--plum);border-radius:14px}
input[type=file]{display:block;margin-top:.4rem;font:inherit;font-weight:400;max-width:100%}
.check{display:flex;gap:.5rem;align-items:center}
.btn{display:inline-block;padding:.6rem 1.2rem;font-size:1.05rem;font-weight:600;text-decoration:none;cursor:pointer;
  color:#fff;background:var(--berry);border:2.5px solid var(--plum);border-radius:999px;box-shadow:3px 3px 0 var(--plum)}
.btn:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--plum)}
.btn.small{padding:.3rem .9rem;font-size:.95rem}
.btn.big{font-size:1.3rem;padding:.8rem 1.8rem}
.linkbtn{background:none;border:0;padding:0;font:inherit;font-weight:700;color:var(--berry);text-decoration:underline;cursor:pointer}
.flash{background:var(--mint);border:2px solid var(--plum);border-radius:14px;padding:.6rem 1rem}
.entry header{display:flex;flex-wrap:wrap;gap:.2rem 1rem;justify-content:space-between;align-items:baseline}
.date{font-size:.9rem;opacity:.75}
.text{white-space:pre-wrap;overflow-wrap:anywhere}
.entry footer{display:flex;flex-wrap:wrap;gap:.8rem 1.2rem;align-items:center;justify-content:space-between;margin-top:1rem}
.entry footer form{margin:0}
.tag{background:var(--mint);border:2px solid var(--plum);border-radius:999px;padding:0 .7rem;font-size:.9rem;font-weight:700}
.linkbox{margin-top:.8rem;font-size:.9rem}
video,audio{display:block;width:100%;margin-top:.8rem;border-radius:14px}
video{max-height:70vh;background:#000}
.empty{opacity:.8}
.alt{margin:1rem 0 0}
.cardpage main{padding-top:2rem}
.center{text-align:center}
.center .text{font-size:1.25rem}
.gift-emoji{font-size:5rem;line-height:1;animation:wobble 1.6s ease-in-out infinite}
.reveal{animation:pop .45s ease-out}
.from{font-weight:700;margin-bottom:0}
.promo{text-align:center;font-size:.95rem}
.fall{position:fixed;top:-48px;z-index:10;pointer-events:none;animation:fall 4.5s linear forwards}
@keyframes wobble{0%,100%{transform:rotate(-6deg)}50%{transform:rotate(6deg)}}
@keyframes pop{from{transform:scale(.85);opacity:0}}
@keyframes fall{to{transform:translateY(115vh) rotate(360deg)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
{% endraw %}
</style>
</head>
<body class="{% block body_class %}{% endblock %}">
{% block header %}
<header class="top">
  <a class="logo" href="{{ url_for('index') }}">🌸 {{ site_name }}</a>
  <nav>
    {% if user %}
      <a href="{{ url_for('journal') }}">Journal</a>
      <a href="{{ url_for('cards') }}">Cartes</a>
      <form method="post" action="{{ url_for('logout') }}"><button class="linkbtn">Sortir ({{ user['username'] }})</button></form>
    {% else %}
      <a href="{{ url_for('login') }}">Connexion</a>
      <a class="btn small" href="{{ url_for('register') }}">Créer un compte</a>
    {% endif %}
  </nav>
</header>
{% endblock %}
<main>
  {% for m in get_flashed_messages() %}<p class="flash">{{ m }}</p>{% endfor %}
  {% block content %}{% endblock %}
</main>
</body>
</html>
""",
    "card_view.html": r"""{% extends "base.html" %}
{% from "_macros.html" import player %}
{% block title %}Une carte pour {{ card.recipient }}{% endblock %}
{% block body_class %}cardpage theme-{{ card.theme }}{% endblock %}
{% block header %}{% endblock %}
{% block content %}
<section class="panel center" id="gift">
  <div class="gift-emoji">🎁</div>
  <h1>Une carte pour {{ card.recipient }}</h1>
  <p>{{ card.author }} t'a préparé quelque chose.</p>
  <button class="btn big" id="open">Ouvrir la carte</button>
</section>
<section class="panel center reveal" id="reveal" hidden>
  <h1>Joyeux anniversaire, {{ card.recipient }} !</h1>
  <p class="text">{{ card.message }}</p>
  {{ player(card.media_kind, card.media) }}
  <p class="from">De la part de {{ card.author }}</p>
</section>
<p class="promo"><a href="{{ url_for('index') }}">Crée ta propre carte sur {{ site_name }}</a></p>
<script>
document.getElementById('open').addEventListener('click', function () {
  document.getElementById('gift').hidden = true;
  document.getElementById('reveal').hidden = false;
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var emoji = {{ emoji|tojson }};
  for (var i = 0; i < 28; i++) {
    var s = document.createElement('span');
    s.className = 'fall';
    s.textContent = emoji;
    s.style.left = Math.random() * 100 + 'vw';
    s.style.animationDelay = Math.random() * 2 + 's';
    s.style.fontSize = (18 + Math.random() * 22) + 'px';
    document.body.appendChild(s);
    setTimeout(function (el) { el.remove(); }, 6500, s);
  }
});
</script>
{% endblock %}
""",
    "cards.html": r"""{% extends "base.html" %}
{% from "_macros.html" import player %}
{% block title %}Mes cartes{% endblock %}
{% block content %}
<h1>Cartes d'anniversaire</h1>
<form class="panel" method="post" enctype="multipart/form-data">
  <label>Pour qui ? <input name="recipient" required maxlength="60" placeholder="Prénom ou pseudo"></label>
  <label>Thème
    <select name="theme">{% for k, v in themes.items() %}<option value="{{ k }}">{{ v }}</option>{% endfor %}</select>
  </label>
  <label>Ton message <textarea name="message" required rows="5" maxlength="3000"></textarea></label>
  <label>Vocal ou vidéo (facultatif) <input type="file" name="media" accept="audio/*,video/*"></label>
  <button class="btn">Créer la carte</button>
</form>
{% for c in cards %}
{% set link = url_for('card_view', token=c.token, _external=True) %}
<article class="panel entry">
  <header><h2>Pour {{ c.recipient }}</h2><span class="date">{{ themes[c.theme] }} · {{ c.created_at|date }}</span></header>
  <input class="linkbox" readonly value="{{ link }}" onfocus="this.select()">
  <footer>
    <button class="btn small" data-url="{{ link }}" onclick="navigator.clipboard.writeText(this.dataset.url);this.textContent='Lien copié !'">Copier le lien</button>
    <a href="{{ url_for('card_view', token=c.token) }}">Voir la carte</a>
    <form method="post" action="{{ url_for('delete_card', cid=c.id) }}" onsubmit="return confirm('Supprimer cette carte ? Le lien ne marchera plus.')"><button class="linkbtn">Supprimer</button></form>
  </footer>
</article>
{% else %}
<p class="empty">Aucune carte pour l'instant. Crée la première ci-dessus.</p>
{% endfor %}
{% endblock %}
""",
    "index.html": r"""{% extends "base.html" %}
{% from "_macros.html" import player %}
{% block content %}
<section class="hero panel">
  <h1>Ton carnet de bord, tes cartes d'anniversaire.</h1>
  <p>Écris, enregistre un vocal ou ajoute une vidéo. Crée une carte pour un ami et envoie-lui un lien : il l'ouvre comme un cadeau.</p>
  {% if user %}
    <a class="btn" href="{{ url_for('journal') }}">Ouvrir mon journal</a>
  {% else %}
    <a class="btn" href="{{ url_for('register') }}">Créer mon compte</a>
  {% endif %}
</section>
<h2>Pages publiques</h2>
{% for e in entries %}
<article class="panel entry">
  <header><h3>{{ e.title or "Sans titre" }}</h3><span class="date">{{ e.username }} · {{ e.created_at|date }}</span></header>
  {% if e.body %}<p class="text">{{ e.body }}</p>{% endif %}
  {{ player(e.media_kind, e.media) }}
</article>
{% else %}
<p class="empty">Aucune page publique pour l'instant.</p>
{% endfor %}
{% endblock %}
""",
    "journal.html": r"""{% extends "base.html" %}
{% from "_macros.html" import player %}
{% block title %}Mon journal{% endblock %}
{% block content %}
<h1>Mon journal de bord</h1>
<form class="panel" method="post" enctype="multipart/form-data">
  <label>Titre <input name="title" maxlength="120" placeholder="Ex : Nuit blanche sur mon jeu du moment"></label>
  <label>Ton message <textarea name="body" rows="5" maxlength="5000"></textarea></label>
  <label>Vidéo ou message vocal <input type="file" name="media" accept="audio/*,video/*"></label>
  <label class="check"><input type="checkbox" name="is_public" value="1"> Visible par tout le monde</label>
  <button class="btn">Publier la page</button>
</form>
{% for e in entries %}
<article class="panel entry">
  <header><h2>{{ e.title or "Sans titre" }}</h2><span class="date">{{ e.created_at|date }}</span></header>
  {% if e.body %}<p class="text">{{ e.body }}</p>{% endif %}
  {{ player(e.media_kind, e.media) }}
  <footer>
    <span class="tag">{{ "Public" if e.is_public else "Privé" }}</span>
    <form method="post" action="{{ url_for('delete_entry', eid=e.id) }}" onsubmit="return confirm('Supprimer cette page ?')"><button class="linkbtn">Supprimer</button></form>
  </footer>
</article>
{% else %}
<p class="empty">Ton journal est vide. Écris ta première page ci-dessus.</p>
{% endfor %}
{% endblock %}
""",
}
