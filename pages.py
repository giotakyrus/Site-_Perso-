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

{% macro recorder() %}
<div class="rec">
  <div class="rec-btns">
    <button type="button" class="btn small rec-audio">🎙️ Enregistrer un vocal</button>
    <button type="button" class="btn small rec-video">🎥 Enregistrer une vidéo</button>
    <button type="button" class="btn small stop" hidden>⏹️ Arrêter</button>
  </div>
  <video class="live" muted playsinline hidden></video>
  <div class="preview"></div>
  <p class="status" aria-live="polite"></p>
</div>
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
  --milk:#FFF4F8; --bg:#E7EEFF; --dot:#FFD9E6; --sakura:#FFC2D6; --berry:#C2306A;
  --plum:#3F1D38; --mint:#C9F0E1; --white:#fff;
}
.theme-gamer{--bg:#E4DCFF; --dot:#E4D9FF; --sakura:#CDB8FF}
.theme-etoile{--bg:#FFF3C9; --dot:#FFF0BF; --sakura:#FFE08A}
.theme-gateau{--bg:#D9F5E8; --dot:#D8F5E9; --sakura:#9EE3C8}
*{box-sizing:border-box}
body{
  margin:0; font-family:Nunito,system-ui,sans-serif; font-size:1.05rem; line-height:1.6;
  color:var(--plum); background-color:var(--bg);
  background-image:url('data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22420%22%20height%3D%22420%22%20viewBox%3D%220%200%20420%20420%22%3E%3Cg%20transform%3D%22translate%2895%2C100%29%20scale%28.9%29%22%20stroke%3D%22%233F1D38%22%20stroke-width%3D%222.2%22%20stroke-linejoin%3D%22round%22%20stroke-linecap%3D%22round%22%3E%3Cpath%20d%3D%22M-20%2032Q-22%2062%20-14%2068L14%2068Q22%2062%2020%2032Z%22%20fill%3D%22%23FFD166%22%2F%3E%3Ccircle%20cx%3D%22-25%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Ccircle%20cx%3D%2225%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cpath%20d%3D%22M-31%20-18L-27%20-52L-6%20-34Z%22%20fill%3D%22%238FD3C1%22%2F%3E%3Cpath%20d%3D%22M31%20-18L27%20-52L6%20-34Z%22%20fill%3D%22%238FD3C1%22%2F%3E%3Cpath%20d%3D%22M-27%20-26L-25%20-42L-14%20-33Z%22%20fill%3D%22%23FFB6C8%22%20stroke%3D%22none%22%2F%3E%3Cpath%20d%3D%22M27%20-26L25%20-42L14%20-33Z%22%20fill%3D%22%23FFB6C8%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%220%22%20cy%3D%22-2%22%20rx%3D%2240%22%20ry%3D%2238%22%20fill%3D%22%238FD3C1%22%2F%3E%3Cpath%20d%3D%22M-38%206Q-47%2052%20-30%2060L-24%2014Z%22%20fill%3D%22%238FD3C1%22%2F%3E%3Cpath%20d%3D%22M38%206Q47%2052%2030%2060L24%2014Z%22%20fill%3D%22%238FD3C1%22%2F%3E%3Ccircle%20cx%3D%220%22%20cy%3D%224%22%20r%3D%2232%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cpath%20d%3D%22M-32%202Q-30%20-34%200%20-34Q30%20-34%2032%202Q20%20-12%208%20-14Q-2%20-6%20-14%20-12Q-24%20-8%20-32%202Z%22%20fill%3D%22%238FD3C1%22%2F%3E%3Cellipse%20cx%3D%22-12%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%234A6CF7%22%2F%3E%3Ccircle%20cx%3D%22-10%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%22-14%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2212%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%234A6CF7%22%2F%3E%3Ccircle%20cx%3D%2214%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2210%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%22-22%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2222%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cpath%20d%3D%22M-3%2021Q0%2025%203%2021%22%20fill%3D%22none%22%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%22translate%28305%2C205%29%20scale%28.9%29%22%20stroke%3D%22%233F1D38%22%20stroke-width%3D%222.2%22%20stroke-linejoin%3D%22round%22%20stroke-linecap%3D%22round%22%3E%3Cpath%20d%3D%22M-20%2032Q-22%2062%20-14%2068L14%2068Q22%2062%2020%2032Z%22%20fill%3D%22%236EC1FF%22%2F%3E%3Ccircle%20cx%3D%22-25%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Ccircle%20cx%3D%2225%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cellipse%20cx%3D%220%22%20cy%3D%22-2%22%20rx%3D%2240%22%20ry%3D%2238%22%20fill%3D%22%23B79CFF%22%2F%3E%3Ccircle%20cx%3D%220%22%20cy%3D%224%22%20r%3D%2232%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cpath%20d%3D%22M-32%202Q-30%20-34%200%20-34Q30%20-34%2032%202Q20%20-12%208%20-14Q-2%20-6%20-14%20-12Q-24%20-8%20-32%202Z%22%20fill%3D%22%23B79CFF%22%2F%3E%3Cellipse%20cx%3D%22-12%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%237A3FBF%22%2F%3E%3Ccircle%20cx%3D%22-10%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%22-14%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2212%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%237A3FBF%22%2F%3E%3Ccircle%20cx%3D%2214%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2210%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%22-22%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2222%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cpath%20d%3D%22M-3%2021Q0%2025%203%2021%22%20fill%3D%22none%22%2F%3E%3Cpath%20d%3D%22M-37%204Q-38%20-44%200%20-44Q38%20-44%2037%204%22%20fill%3D%22none%22%20stroke-width%3D%225%22%2F%3E%3Crect%20x%3D%22-45%22%20y%3D%22-4%22%20width%3D%2212%22%20height%3D%2224%22%20rx%3D%226%22%20fill%3D%22%238E7CFF%22%2F%3E%3Crect%20x%3D%2233%22%20y%3D%22-4%22%20width%3D%2212%22%20height%3D%2224%22%20rx%3D%226%22%20fill%3D%22%238E7CFF%22%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%22translate%28130%2C335%29%20scale%28.9%29%22%20stroke%3D%22%233F1D38%22%20stroke-width%3D%222.2%22%20stroke-linejoin%3D%22round%22%20stroke-linecap%3D%22round%22%3E%3Cpath%20d%3D%22M-20%2032Q-22%2062%20-14%2068L14%2068Q22%2062%2020%2032Z%22%20fill%3D%22%23FF8FB1%22%2F%3E%3Ccircle%20cx%3D%22-25%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Ccircle%20cx%3D%2225%22%20cy%3D%2248%22%20r%3D%226%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cellipse%20cx%3D%220%22%20cy%3D%22-2%22%20rx%3D%2240%22%20ry%3D%2238%22%20fill%3D%22%23FFB38A%22%2F%3E%3Cpath%20d%3D%22M-38%206Q-47%2052%20-30%2060L-24%2014Z%22%20fill%3D%22%23FFB38A%22%2F%3E%3Cpath%20d%3D%22M38%206Q47%2052%2030%2060L24%2014Z%22%20fill%3D%22%23FFB38A%22%2F%3E%3Ccircle%20cx%3D%220%22%20cy%3D%224%22%20r%3D%2232%22%20fill%3D%22%23FFE6D8%22%2F%3E%3Cpath%20d%3D%22M-32%202Q-30%20-34%200%20-34Q30%20-34%2032%202Q20%20-12%208%20-14Q-2%20-6%20-14%20-12Q-24%20-8%20-32%202Z%22%20fill%3D%22%23FFB38A%22%2F%3E%3Cellipse%20cx%3D%22-12%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%232E8B6B%22%2F%3E%3Ccircle%20cx%3D%22-10%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%22-14%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2212%22%20cy%3D%229%22%20rx%3D%226%22%20ry%3D%228%22%20fill%3D%22%232E8B6B%22%2F%3E%3Ccircle%20cx%3D%2214%22%20cy%3D%226%22%20r%3D%222.5%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2210%22%20cy%3D%2212%22%20r%3D%221.2%22%20fill%3D%22%23fff%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%22-22%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cellipse%20cx%3D%2222%22%20cy%3D%2219%22%20rx%3D%225%22%20ry%3D%223%22%20fill%3D%22%23FF9DB8%22%20stroke%3D%22none%22%2F%3E%3Cpath%20d%3D%22M-3%2021Q0%2025%203%2021%22%20fill%3D%22none%22%2F%3E%3Cpath%20d%3D%22M20%20-28L40%20-40L40%20-16Z%22%20fill%3D%22%23FF5C8A%22%2F%3E%3Cpath%20d%3D%22M20%20-28L0%20-40L0%20-16Z%22%20fill%3D%22%23FF5C8A%22%2F%3E%3Ccircle%20cx%3D%2220%22%20cy%3D%22-28%22%20r%3D%225%22%20fill%3D%22%23FF8FB1%22%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%22translate%28335%2C60%29%22%20stroke%3D%22%233F1D38%22%20stroke-width%3D%222.2%22%20stroke-linecap%3D%22round%22%3E%3Crect%20x%3D%22-24%22%20y%3D%22-13%22%20width%3D%2248%22%20height%3D%2226%22%20rx%3D%2213%22%20fill%3D%22%23fff%22%2F%3E%3Cpath%20d%3D%22M-14%20-4v8M-18%200h8%22%20fill%3D%22none%22%2F%3E%3Ccircle%20cx%3D%2210%22%20cy%3D%22-3%22%20r%3D%222.6%22%20fill%3D%22%23FF8FB1%22%2F%3E%3Ccircle%20cx%3D%2217%22%20cy%3D%223%22%20r%3D%222.6%22%20fill%3D%22%236EC1FF%22%2F%3E%3C%2Fg%3E%3Cpath%20transform%3D%22translate%28235%2C40%29%20scale%281.2%29%22%20d%3D%22M0%20-9L2.5%20-2.5L9%200L2.5%202.5L0%209L-2.5%202.5L-9%200L-2.5%20-2.5Z%22%20fill%3D%22%23fff%22%20opacity%3D%220.9%22%2F%3E%3Cpath%20transform%3D%22translate%2830%2C250%29%20scale%281%29%22%20d%3D%22M0%20-9L2.5%20-2.5L9%200L2.5%202.5L0%209L-2.5%202.5L-9%200L-2.5%20-2.5Z%22%20fill%3D%22%23fff%22%20opacity%3D%220.9%22%2F%3E%3Cpath%20transform%3D%22translate%28380%2C330%29%20scale%281.3%29%22%20d%3D%22M0%20-9L2.5%20-2.5L9%200L2.5%202.5L0%209L-2.5%202.5L-9%200L-2.5%20-2.5Z%22%20fill%3D%22%23fff%22%20opacity%3D%220.9%22%2F%3E%3Cpath%20transform%3D%22translate%28240%2C300%29%20scale%280.8%29%22%20d%3D%22M0%20-9L2.5%20-2.5L9%200L2.5%202.5L0%209L-2.5%202.5L-9%200L-2.5%20-2.5Z%22%20fill%3D%22%23fff%22%20opacity%3D%220.9%22%2F%3E%3Cpath%20transform%3D%22translate%2820%2C30%29%20scale%280.9%29%22%20d%3D%22M0%20-9L2.5%20-2.5L9%200L2.5%202.5L0%209L-2.5%202.5L-9%200L-2.5%20-2.5Z%22%20fill%3D%22%23fff%22%20opacity%3D%220.9%22%2F%3E%3Cpath%20transform%3D%22translate%28215%2C120%29%20scale%281.1%29%22%20d%3D%22M0%206C-10%20-2%20-8%20-10%20-3%20-10C-1%20-10%200%20-8%200%20-7C0%20-8%201%20-10%203%20-10C8%20-10%2010%20-2%200%206Z%22%20fill%3D%22%23FF8FB1%22%2F%3E%3Cpath%20transform%3D%22translate%28385%2C140%29%20scale%280.9%29%22%20d%3D%22M0%206C-10%20-2%20-8%20-10%20-3%20-10C-1%20-10%200%20-8%200%20-7C0%20-8%201%20-10%203%20-10C8%20-10%2010%20-2%200%206Z%22%20fill%3D%22%23B79CFF%22%2F%3E%3Cpath%20transform%3D%22translate%28300%2C380%29%20scale%281%29%22%20d%3D%22M0%206C-10%20-2%20-8%20-10%20-3%20-10C-1%20-10%200%20-8%200%20-7C0%20-8%201%20-10%203%20-10C8%20-10%2010%20-2%200%206Z%22%20fill%3D%22%23FF8FB1%22%2F%3E%3Cpath%20transform%3D%22translate%2820%2C370%29%20scale%280.8%29%22%20d%3D%22M0%206C-10%20-2%20-8%20-10%20-3%20-10C-1%20-10%200%20-8%200%20-7C0%20-8%201%20-10%203%20-10C8%20-10%2010%20-2%200%206Z%22%20fill%3D%22%236EC1FF%22%2F%3E%3C%2Fsvg%3E'); background-size:360px 360px;
}
h1,h2,h3,.logo,.btn{font-family:Fredoka,Nunito,sans-serif}
h1{font-size:clamp(1.7rem,6vw,2.4rem);line-height:1.15;margin:0 0 .6rem}
h2{font-size:1.4rem;margin:0}
h3{font-size:1.2rem;margin:0}
a{color:var(--berry);font-weight:700}
:focus-visible{outline:3px solid var(--plum);outline-offset:2px}
.top{display:flex;flex-wrap:wrap;gap:.6rem 1rem;align-items:center;justify-content:space-between;background:#fff;border-bottom:2.5px solid var(--plum);margin:0 0 1.2rem;padding:.8rem max(1rem,calc((100% - 760px)/2))}
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

[hidden]{display:none!important}
.theme-sakura{--bg:#FFE6EF}
main>h1,main>h2{display:inline-block;background:#fff;border:2.5px solid var(--plum);border-radius:16px;padding:.1em .6em;box-shadow:4px 4px 0 var(--sakura)}
.feats{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin-bottom:1.5rem}
.feat{display:flex;flex-direction:column;gap:.2rem;text-decoration:none;color:var(--plum);font-weight:400;margin:0}
.feat b{font-family:Fredoka,sans-serif;font-size:1.15rem}
.rec{margin:0 0 1rem}
.rec-btns{display:flex;flex-wrap:wrap;gap:.5rem}
.rec.on .rec-audio,.rec.on .rec-video{display:none}
.stop{background:var(--plum)}
.live{width:100%;max-height:50vh;border-radius:14px;background:#000;margin-top:.6rem}
.status{font-size:.95rem;margin:.4rem 0 0}
.hp{position:absolute;left:-9999px}
.ask-q{font-size:1.6rem;font-family:Fredoka,sans-serif;margin:.5rem 0}
.ask-btns{display:flex;gap:1rem;justify-content:center;align-items:center;min-height:5rem;margin-top:1.5rem}
.btn.no{background:#fff;color:var(--plum)}
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
      <a href="{{ url_for('asks') }}">Demandes</a>
      <a href="{{ url_for('inbox') }}">Messages</a>
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
<script>
{% raw %}
document.querySelectorAll('.rec').forEach(function (box) {
  var form = box.closest('form');
  var input = form.querySelector('input[type=file]');
  var live = box.querySelector('.live');
  var preview = box.querySelector('.preview');
  var status = box.querySelector('.status');
  var stopBtn = box.querySelector('.stop');
  var rec = null, stream = null, chunks = [];
  function pickMime(video) {
    var list = video ? ['video/webm;codecs=vp8,opus', 'video/webm', 'video/mp4'] : ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'];
    return list.find(function (m) { return window.MediaRecorder && MediaRecorder.isTypeSupported(m); }) || '';
  }
  async function start(video) {
    if (!window.MediaRecorder || !navigator.mediaDevices) { status.textContent = "Ton navigateur ne sait pas enregistrer ici."; return; }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: video ? { facingMode: 'user' } : false });
    } catch (e) {
      status.textContent = "Autorise le micro" + (video ? " et la caméra" : "") + " pour enregistrer.";
      return;
    }
    var mime = pickMime(video);
    rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    chunks = [];
    rec.ondataavailable = function (e) { if (e.data.size) chunks.push(e.data); };
    rec.onstop = function () {
      stream.getTracks().forEach(function (t) { t.stop(); });
      live.hidden = true; live.srcObject = null; stopBtn.hidden = true; box.classList.remove('on');
      var type = (rec.mimeType || mime || (video ? 'video/webm' : 'audio/webm')).split(';')[0];
      var ext = type.indexOf('mp4') > -1 ? (video ? 'mp4' : 'm4a') : 'webm';
      var file = new File([new Blob(chunks, { type: type })], 'enregistrement.' + ext, { type: type });
      var dt = new DataTransfer(); dt.items.add(file); input.files = dt.files;
      preview.innerHTML = '';
      var el = document.createElement(video ? 'video' : 'audio');
      el.controls = true; el.playsInline = true; el.src = URL.createObjectURL(file);
      preview.appendChild(el);
      status.textContent = "Enregistrement prêt. Il sera envoyé avec la page.";
    };
    if (video) { live.srcObject = stream; live.hidden = false; live.play(); }
    rec.start(); box.classList.add('on'); stopBtn.hidden = false;
    status.textContent = "Enregistrement en cours…";
  }
  box.querySelector('.rec-audio').onclick = function () { start(false); };
  box.querySelector('.rec-video').onclick = function () { start(true); };
  stopBtn.onclick = function () { if (rec && rec.state !== 'inactive') rec.stop(); };
});
{% endraw %}
</script>
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
{% from "_macros.html" import player, recorder %}
{% block title %}Mes cartes{% endblock %}
{% block content %}
<h1>Cartes d'anniversaire</h1>
<form class="panel" method="post" enctype="multipart/form-data">
  <label>Pour qui ? <input name="recipient" required maxlength="60" placeholder="Prénom ou pseudo"></label>
  <label>Thème
    <select name="theme">{% for k, v in themes.items() %}<option value="{{ k }}">{{ v }}</option>{% endfor %}</select>
  </label>
  <label>Ton message <textarea name="message" required rows="5" maxlength="3000"></textarea></label>
  {{ recorder() }}
  <label>Ou choisis un fichier (facultatif) <input type="file" name="media" accept="audio/*,video/*"></label>
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
<div class="feats">
  <a class="panel feat" href="{{ url_for('journal') }}"><b>📓 Journal</b>Texte, vocal et vidéo enregistrés sur le site.</a>
  <a class="panel feat" href="{{ url_for('cards') }}"><b>🎂 Cartes d'anniversaire</b>Un lien, un cadeau à ouvrir.</a>
  <a class="panel feat" href="{{ url_for('asks') }}"><b>💌 Demandes</b>Des questions où le bouton « Non » s'enfuit.</a>
  <a class="panel feat" href="{{ url_for('inbox') }}"><b>🕊️ Messages anonymes</b>Ta boîte à messages secrets.</a>
</div>
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
{% from "_macros.html" import player, recorder %}
{% block title %}Mon journal{% endblock %}
{% block content %}
<h1>Mon journal de bord</h1>
<form class="panel" method="post" enctype="multipart/form-data">
  <label>Titre <input name="title" maxlength="120" placeholder="Ex : Nuit blanche sur mon jeu du moment"></label>
  <label>Ton message <textarea name="body" rows="5" maxlength="5000"></textarea></label>
  {{ recorder() }}
  <label>Ou choisis un fichier <input type="file" name="media" accept="audio/*,video/*"></label>
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
    "asks.html": r"""{% extends "base.html" %}
{% block title %}Mes demandes{% endblock %}
{% block content %}
<h1>Demandes 💌</h1>
<form class="panel" method="post">
  <label>Pour qui ? <input name="recipient" required maxlength="60" placeholder="Prénom ou pseudo"></label>
  <label>Tes questions (une par ligne, 8 maximum)
    <textarea name="questions" required rows="6" maxlength="1200" placeholder="Tu aimes les animes ?&#10;Tu veux jouer avec moi ce soir ?&#10;Tu veux sortir avec moi ?"></textarea></label>
  <label>Message final (facultatif) <input name="final" maxlength="200" placeholder="Merci d'avoir dit oui 💖"></label>
  <button class="btn">Créer la demande</button>
</form>
{% for a in rows %}
{% set link = url_for('ask_view', token=a.token, _external=True) %}
<article class="panel entry">
  <header><h2>Pour {{ a.recipient }}</h2><span class="date">{{ a.created_at|date }}</span></header>
  <p>{% if a.done_at %}✅ A dit oui le {{ a.done_at|date }} !{% else %}⏳ Pas encore de réponse.{% endif %}</p>
  <input class="linkbox" readonly value="{{ link }}" onfocus="this.select()">
  <footer>
    <button class="btn small" data-url="{{ link }}" onclick="navigator.clipboard.writeText(this.dataset.url);this.textContent='Lien copié !'">Copier le lien</button>
    <a href="{{ url_for('ask_view', token=a.token) }}">Voir</a>
    <form method="post" action="{{ url_for('delete_ask', aid=a.id) }}" onsubmit="return confirm('Supprimer cette demande ?')"><button class="linkbtn">Supprimer</button></form>
  </footer>
</article>
{% else %}
<p class="empty">Aucune demande pour l'instant. Écris tes questions ci-dessus.</p>
{% endfor %}
{% endblock %}
""",
    "ask_view.html": r"""{% extends "base.html" %}
{% block title %}Une demande pour {{ ask.recipient }}{% endblock %}
{% block body_class %}cardpage theme-sakura{% endblock %}
{% block header %}{% endblock %}
{% block content %}
<section class="panel center" id="intro">
  <div class="gift-emoji">💌</div>
  <h1>Coucou {{ ask.recipient }}</h1>
  <p>{{ ask.author }} a quelques questions pour toi.</p>
  <button class="btn big" id="start">C'est parti</button>
</section>
<section class="panel center" id="quiz" hidden>
  <p class="date" id="count"></p>
  <p class="ask-q" id="q"></p>
  <div class="ask-btns"><button class="btn big" id="yes">Oui 💖</button><button class="btn big no" id="no">Non</button></div>
</section>
<section class="panel center reveal" id="end" hidden>
  <div class="gift-emoji">💖</div>
  <h1>{{ ask.final_msg }}</h1>
  <p class="from">De la part de {{ ask.author }}</p>
</section>
<p class="promo"><a href="{{ url_for('index') }}">Crée ta propre demande sur {{ site_name }}</a></p>
<script>
(function () {
  var qs = {{ questions|tojson }}, i = 0;
  var $ = function (id) { return document.getElementById(id); };
  var no = $('no');
  function show() {
    $('q').textContent = qs[i];
    $('count').textContent = 'Question ' + (i + 1) + ' sur ' + qs.length;
    no.style.position = ''; no.style.left = ''; no.style.top = '';
  }
  function flee(e) {
    e.preventDefault();
    var pad = 12;
    no.style.position = 'fixed';
    no.style.left = (pad + Math.random() * Math.max(0, innerWidth - no.offsetWidth - 2 * pad)) + 'px';
    no.style.top = (pad + Math.random() * Math.max(0, innerHeight - no.offsetHeight - 2 * pad)) + 'px';
  }
  ['pointerenter', 'pointerdown', 'focus', 'click'].forEach(function (ev) { no.addEventListener(ev, flee); });
  $('start').onclick = function () { $('intro').hidden = true; $('quiz').hidden = false; show(); };
  $('yes').onclick = function () {
    i++;
    if (i < qs.length) { show(); return; }
    $('quiz').hidden = true; $('end').hidden = false;
    fetch({{ url_for('ask_done', token=ask.token)|tojson }}, { method: 'POST' });
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    for (var k = 0; k < 28; k++) {
      var s = document.createElement('span');
      s.className = 'fall'; s.textContent = '💖';
      s.style.left = Math.random() * 100 + 'vw';
      s.style.animationDelay = Math.random() * 2 + 's';
      s.style.fontSize = (18 + Math.random() * 22) + 'px';
      document.body.appendChild(s);
      setTimeout(function (el) { el.remove(); }, 6500, s);
    }
  };
})();
</script>
{% endblock %}
""",
    "messages.html": r"""{% extends "base.html" %}
{% block title %}Mes messages{% endblock %}
{% block content %}
<h1>Messages anonymes 🕊️</h1>
{% set link = url_for('anon', username=user['username'], _external=True) %}
<div class="panel">
  <p>Partage ce lien : tout le monde peut t'écrire sans que tu saches qui.</p>
  <input class="linkbox" readonly value="{{ link }}" onfocus="this.select()">
  <p><button class="btn small" data-url="{{ link }}" onclick="navigator.clipboard.writeText(this.dataset.url);this.textContent='Lien copié !'">Copier mon lien</button></p>
</div>
{% for m in rows %}
<article class="panel entry">
  <header><h3>Message anonyme</h3><span class="date">{{ m.created_at|date }}</span></header>
  <p class="text">{{ m.body }}</p>
  <footer><span></span>
    <form method="post" action="{{ url_for('delete_message', mid=m.id) }}"><button class="linkbtn">Supprimer</button></form>
  </footer>
</article>
{% else %}
<p class="empty">Aucun message pour l'instant. Partage ton lien pour en recevoir.</p>
{% endfor %}
{% endblock %}
""",
    "anon.html": r"""{% extends "base.html" %}
{% block title %}Message anonyme pour {{ target.username }}{% endblock %}
{% block content %}
<form class="panel narrow" method="post">
  <h1>Un message pour {{ target.username }}</h1>
  <p>Ton nom n'est pas enregistré : {{ target.username }} ne saura pas que c'est toi.</p>
  <label>Ton message <textarea name="body" required rows="5" maxlength="500"></textarea></label>
  <input class="hp" name="site" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn">Envoyer en anonyme</button>
</form>
{% endblock %}
""",
}
