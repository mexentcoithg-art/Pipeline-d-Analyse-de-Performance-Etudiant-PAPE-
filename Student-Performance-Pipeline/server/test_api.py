import urllib.request
try:
    print("--- STATS ---")
    s = urllib.request.urlopen('http://localhost:5000/api/stats').read()
    print(s.decode()[:500])
except Exception as e:
    print("Error stats:", e)

try:
    print("--- STUDENTS ---")
    s = urllib.request.urlopen('http://localhost:5000/api/students?page=1').read()
    print(s.decode()[:500])
except Exception as e:
    print("Error students:", e)
