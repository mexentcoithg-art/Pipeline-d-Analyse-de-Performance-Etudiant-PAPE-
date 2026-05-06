import urllib.request
import json
import sys

def fetch_json(url):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

def test_api():
    print("Fetching students list...")
    status, data = fetch_json("http://localhost:5000/api/students")
    if status != 200:
        print(f"Failed: {status} - {data}")
        return
        
    if not isinstance(data, dict) or not data.get('students'):
        print("No students found.")
        return
        
    massar = data['students'][0]['massar_code']
    print(f"\n--- Testing student: {massar} ---")
    
    print("\n1. /api/students/")
    s1, d1 = fetch_json(f"http://localhost:5000/api/students/{massar}")
    print(f"Status: {s1}")
    if s1 != 200: print(f"Response: {d1[:200]}")
        
    print("\n2. /api/interventions/")
    s2, d2 = fetch_json(f"http://localhost:5000/api/interventions/{massar}")
    print(f"Status: {s2}")
    if s2 != 200: print(f"Response: {d2[:200]}")
        
    print("\n3. /api/analytics/orientation/")
    s3, d3 = fetch_json(f"http://localhost:5000/api/analytics/orientation/{massar}")
    print(f"Status: {s3}")
    if s3 != 200: print(f"Response: {d3[:200]}")

if __name__ == '__main__':
    test_api()
