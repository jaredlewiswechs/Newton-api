import urllib.request
url = 'http://127.0.0.1:9009/kernel/demo/html'
print('Fetching', url)
with urllib.request.urlopen(url) as r:
    print('Status code:', r.getcode())
    data = r.read(1000).decode('utf-8', errors='replace')
    print('Snippet:\n', data[:400])
