# Sakura Log

Journal de bord (texte, vocaux, vidéos) + cartes d'anniversaire partageables par lien. Flask + SQLite.

## Lancer sur ton ordinateur
```
pip install -r requirements.txt
python app.py
```
Puis ouvre http://127.0.0.1:5000

## Déployer sur Railway
1. Mets le dossier sur GitHub, puis sur Railway : New Project > Deploy from GitHub repo.
2. Ajoute un **Volume** au service, monté sur `/data` (sans lui, les fichiers et comptes disparaissent à chaque déploiement).
3. Variables du service :
   - `DATA_DIR=/data`
   - `SECRET_KEY=` une longue chaîne aléatoire
   - `SITE_NAME=` le nom de ton site (facultatif)
4. Génère un domaine dans Settings > Networking.
