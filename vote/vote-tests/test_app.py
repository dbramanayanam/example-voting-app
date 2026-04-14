import json
from unittest.mock import Mock, patch

import pytest

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_homepage_returns_200(client):
    response = client.get('/')
    assert response.status_code == 200


def test_homepage_contains_default_options(client):
    response = client.get('/')
    body = response.get_data(as_text=True)
    assert 'Cats' in body
    assert 'Dogs' in body


def test_get_sets_voter_cookie(client):
    response = client.get('/')
    cookie_headers = response.headers.getlist('Set-Cookie')
    assert any('voter_id=' in header for header in cookie_headers)


@patch('app.get_redis')
def test_post_pushes_vote_to_redis(mock_get_redis, client):
    redis_mock = Mock()
    mock_get_redis.return_value = redis_mock

    response = client.post('/', data={'vote': 'Cats'})

    assert response.status_code == 200
    redis_mock.rpush.assert_called_once()
    queue_name, payload = redis_mock.rpush.call_args[0]
    assert queue_name == 'votes'
    message = json.loads(payload)
    assert message['vote'] == 'Cats'
    assert 'voter_id' in message


@patch('app.get_redis')
def test_post_reuses_existing_voter_cookie(mock_get_redis, client):
    redis_mock = Mock()
    mock_get_redis.return_value = redis_mock

    client.set_cookie('voter_id', 'existing-voter-id')
    client.post('/', data={'vote': 'Dogs'})

    _, payload = redis_mock.rpush.call_args[0]
    message = json.loads(payload)
    assert message['voter_id'] == 'existing-voter-id'
    assert message['vote'] == 'Dogs'


def test_post_without_vote_field_returns_bad_request(client):
    response = client.post('/', data={})
    assert response.status_code == 400
