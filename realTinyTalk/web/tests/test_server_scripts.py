import json
import pytest
from realTinyTalk.web import server

@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as c:
        yield c


def test_save_list_get_delete(client):
    name = 'test-script.tt'
    code = 'show("hello")'
    headers = {'X-User': 'testuser'}

    # save
    rv = client.post('/api/scripts', json={'name': name, 'code': code, 'message': 'initial'}, headers=headers)
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'saved' in data

    # list
    rv = client.get('/api/scripts', headers=headers)
    assert rv.status_code == 200
    arr = rv.get_json()
    assert any(s['name'] == name for s in arr)

    # get
    rv = client.get(f'/api/scripts/{name}', headers=headers)
    assert rv.status_code == 200
    payload = rv.get_json()
    assert payload['content'].strip() == code
    assert 'versions' in payload
    assert len(payload['versions']) >= 1

    # version fetch
    vid = payload['versions'][-1]['id']
    rv = client.get(f'/api/scripts/{name}/version/{vid}', headers=headers)
    assert rv.status_code == 200
    ver = rv.get_json()
    assert ver['content'].strip() == code

    # restore (should create another version)
    rv = client.post(f'/api/scripts/{name}/restore', json={'version_id': vid}, headers=headers)
    assert rv.status_code == 200
    res = rv.get_json()
    assert 'restored' in res

    # delete
    rv = client.delete(f'/api/scripts/{name}', headers=headers)
    assert rv.status_code == 200
    d = rv.get_json()
    assert d['deleted'] == name

    # ensure gone
    rv = client.get(f'/api/scripts/{name}', headers=headers)
    assert rv.status_code == 404
