import os
import re
import secrets
import sqlite3
import time
from datetime import datetime
from functools import wraps

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
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "change-moi-en-prod"),
    MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100 Mo par envoi
