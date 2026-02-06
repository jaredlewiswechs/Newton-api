import requests
import time

BASE = 'http://localhost:5555'

s = requests.Session()

def try_register_login(user='intuser', pw='pass123'):
    r = s.post(BASE + '/api/register', json={'username': user, 'password': pw})
    print('register', r.status_code, r.text)
    r = s.post(BASE + '/api/login', json={'username': user, 'password': pw})
    print('login', r.status_code, r.text)

def save_script(name, code):
    r = s.post(BASE + '/api/scripts', json={'name': name, 'code': code, 'message': 'integration save'})
    print('save', r.status_code, r.json())
    return r

def list_scripts():
    r = s.get(BASE + '/api/scripts')
    print('list', r.status_code, r.json())
    return r

def get_script(name):
    r = s.get(BASE + f'/api/scripts/{name}')
    print('get', r.status_code, r.json())
    return r

def merge_script(name, merged):
    r = s.post(BASE + f'/api/scripts/{name}/merge', json={'merged': merged, 'message': 'merged by test'})
    print('merge', r.status_code, r.text)
    return r

def project_flow():
    r = s.post(BASE + '/api/projects', json={'name': 'itest-project'})
    print('create project', r.status_code, r.text)
    r = s.get(BASE + '/api/projects')
    print('projects', r.status_code, r.json())
    r = s.post(BASE + '/api/projects/itest-project/add', json={'script': 'itest.tt'})
    print('add script to project', r.status_code, r.text)

if __name__ == '__main__':
    time.sleep(0.5)
    try_register_login()
    save_script('itest.tt', 'show("hello from local")')
    list_scripts()
    # create another version remotely to simulate divergence
    save_script('itest.tt', 'show("hello from remote")')
    get_script('itest.tt')
    # perform a merge action
    merge_script('itest.tt', 'show("merged content")')
    get_script('itest.tt')
    project_flow()
    print('Integration test complete')
