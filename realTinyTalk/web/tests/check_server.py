import requests
r = requests.get('http://localhost:5555/')
print(r.status_code)
print(r.text[:400])
