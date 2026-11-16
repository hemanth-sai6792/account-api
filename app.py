import json
import os
from pathlib import Path

from flask import Flask, abort

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "dev")

# The app's content lives in a data file, not in code.
# Push a change to data/accounts.json -> Jenkins rebuilds and redeploys.
DATA_FILE = Path(__file__).parent / "data" / "accounts.json"


def load_accounts():
    return json.loads(DATA_FILE.read_text())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": VERSION}


@app.get("/accounts")
def accounts():
    return load_accounts()


@app.get("/accounts/<int:account_id>")
def account(account_id):
    for acc in load_accounts():
        if acc["id"] == account_id:
            return acc
    abort(404)
