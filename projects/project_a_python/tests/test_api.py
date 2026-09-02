from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health_and_crud_contract():
    assert client.get('/health').json() == {'status': 'ok'}
    created = client.post('/tasks', json={'title': 'write tests'}).json()
    assert created['id'] == 1
    assert client.get('/tasks/1').json()['title'] == 'write tests'
    updated = client.put('/tasks/1', json={'title': 'write better tests'}).json()
    assert updated['title'] == 'write better tests'
    assert client.delete('/tasks/1').status_code == 204
    assert client.get('/tasks/1').status_code == 404


def test_multiple_ids_are_distinct():
    first = client.post('/tasks', json={'title': 'first'}).json()
    second = client.post('/tasks', json={'title': 'second'}).json()
    assert client.get(f"/tasks/{second['id']}").json()['id'] == second['id']


def test_empty_title_rejected():
    assert client.post('/tasks', json={'title': ''}).status_code == 422
