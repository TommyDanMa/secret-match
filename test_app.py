"""Fictional, isolated regression scenarios; no production database access."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import re
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Query, sessionmaker

import app as application
from database import Base, get_db
from models import Challenge


@pytest.fixture
def client(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}",
                           connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    def session():
        with factory() as db:
            yield db
    application.app.dependency_overrides[get_db] = session
    with TestClient(application.app) as client:
        yield client, factory
    application.app.dependency_overrides.clear()
    engine.dispose()


def create(client):
    response = client.post('/create', data={
        'names': 'Alice\nBob\nCharlie', 'selected_name': 'Alice'})
    assert response.status_code == 200
    return re.search(r'/c/([\w-]+)', response.text).group(0)


@pytest.mark.parametrize('guess,result', [('Alice', 'Match'), ('Bob', 'No match')])
def test_match_and_no_replay(client, guess, result):
    http, _ = client
    assert http.get('/').status_code == 200
    path = create(http)
    assert http.get(path).status_code == 200
    response = http.post(path, data={'guess': guess})
    assert response.status_code == 200
    assert f'{result}\n' in response.text
    assert http.post(path, data={'guess': 'Alice'}).status_code == 400
    assert http.get(path).status_code == 410


def test_expired_and_unknown(client):
    http, factory = client
    path = create(http)
    with factory() as db:
        row = db.query(Challenge).one()
        row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert http.get(path).status_code == 410
    assert http.post(path, data={'guess': 'Alice'}).status_code == 400
    with factory() as db:
        assert not db.query(Challenge).one().is_used
    assert http.get('/c/nonexistent').status_code == 404
    assert http.post('/c/nonexistent', data={'guess': 'Alice'}).status_code == 404


def test_creation_validation(client):
    http, _ = client
    for names, choice in [('Alice', 'Alice'), ('Alice\nBob', 'Charlie')]:
        assert http.post('/create', data={
            'names': names, 'selected_name': choice}).status_code == 400


def test_concurrent_single_use(client, monkeypatch):
    http, _ = client
    path = create(http)
    barrier = Barrier(8)
    original_first = Query.first
    def read_before_any_claim(query):
        row = original_first(query)
        if isinstance(row, Challenge):
            # Force all requests to observe the same unused state before writing.
            assert not row.is_used
            barrier.wait(timeout=10)
        return row
    monkeypatch.setattr(Query, 'first', read_before_any_claim)
    def attempt(_):
        return http.post(path, data={'guess': 'Alice'}).status_code
    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(attempt, range(8)))
    assert codes.count(200) == 1
    assert codes.count(400) == 7
