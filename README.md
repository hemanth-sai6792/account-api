# account-api

A tiny Flask service whose content comes from `data/accounts.json`.
Jenkins redeploys it whenever `app.py`, `data/`, `requirements.txt` or `Dockerfile` changes.
Changing only this README does **not** trigger a deploy.
Docs tweak.
