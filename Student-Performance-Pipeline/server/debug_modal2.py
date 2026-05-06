import urllib.request
import json

def fetch_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return response.status, json.loads(response.read().decode())

def test_api():
    status, data = fetch_json("http://localhost:5000/api/students")
    massar = data['students'][0]['massar_code']
    s1, d1 = fetch_json(f"http://localhost:5000/api/students/{massar}")
    print(f"Keys in student data: {list(d1.keys())}")
    if 'error' in d1:
        print(f"Found error key: {d1['error']}")

if __name__ == '__main__':
    test_api()
