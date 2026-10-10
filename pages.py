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
