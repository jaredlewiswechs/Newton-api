import requests, json
url='http://127.0.0.1:8088/logic/evaluate'
headers={'x-api-key':'demo-key'}
payload={"expr":{"type":"add","args":[{"type":"literal","args":[1]},{"type":"literal","args":[2]}]}}
r=requests.post(url,json=payload,headers=headers)
print(r.status_code)
print(json.dumps(r.json(), indent=2))
