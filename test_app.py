from app import app, load_accounts

client = app.test_client()


# --- code tests ---------------------------------------------------------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_accounts_endpoint():
    r = client.get("/accounts")
    assert r.status_code == 200
    assert len(r.get_json()) > 0


def test_missing_account_is_404():
    assert client.get("/accounts/99999").status_code == 404


# --- data tests: the gate for data pushes ------------------------------
# If someone pushes broken data, these fail, the pipeline stops,
# and production keeps serving the last good version.

def test_every_account_has_valid_fields():
    for acc in load_accounts():
        assert isinstance(acc["id"], int)
        assert isinstance(acc["owner"], str) and acc["owner"].strip()
        assert isinstance(acc["balance"], (int, float))
        assert acc["balance"] >= 0


def test_account_ids_are_unique():
    ids = [acc["id"] for acc in load_accounts()]
    assert len(ids) == len(set(ids))
