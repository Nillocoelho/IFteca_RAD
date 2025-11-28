import json
import urllib.request

url = 'http://127.0.0.1:8000/api/salas/'
payload = {'nome': 'TEST-POST-XYZ2', 'capacidade': 12, 'tipo': 'Individual'}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print('STATUS', r.status)
        print(r.read().decode('utf-8'))
except Exception as e:
    print('EXC', repr(e))
