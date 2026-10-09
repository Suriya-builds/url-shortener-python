import os
import secrets

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.codes import ALPHABET


@pytest.fixture
def client():
    if not os.environ.get("DATABASE_URL") or not os.environ.get("REDIS_URL"):
        pytest.skip("DATABASE_URL and REDIS_URL must be set")

    with TestClient(app) as test_client:
        yield test_client


def test_health_checks_postgres_and_redis(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["postgres"] is True
    assert data["redis"] is True


def test_shorten_and_redirect_records_click(client):
    original_url = f"https://example.com/{secrets.token_hex(8)}"

    response = client.post("/shorten", json={"url": original_url})
    assert response.status_code == 201

    code = response.json()["code"]

    redirect = client.get(f"/{code}", follow_redirects=False)
    assert redirect.status_code == 302
    assert redirect.headers["location"] == original_url

    stats = client.get(f"/api/links/{code}/stats")
    assert stats.status_code == 200
    assert sum(item["clicks"] for item in stats.json()["per_day"]) >= 1


def test_custom_code_and_duplicate_conflict(client):
    code = "t" + "".join(
        secrets.choice(ALPHABET) for _ in range(8)
    )
    payload = {
        "url": "https://example.com/custom",
        "custom": code,
    }

    first = client.post("/shorten", json=payload)
    assert first.status_code == 201
    assert first.json()["code"] == code

    second = client.post("/shorten", json=payload)
    assert second.status_code == 409


def test_unknown_code_returns_404(client):
    code = "missing" + secrets.token_hex(8)

    response = client.get(f"/{code}")

    assert response.status_code == 404
