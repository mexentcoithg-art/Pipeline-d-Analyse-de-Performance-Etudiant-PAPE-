import urllib.request
import urllib.parse
import json
import os
import mimetypes

BASE_URL = 'http://localhost:5000/api'
TEST_FILE = 'test_dynamic.csv'

# Create dummy file
with open(TEST_FILE, 'w', encoding='utf-8') as f:
    f.write("Matricule,Age,Score_Partiel,Note_Finale,Absences\n")
    f.write("ETUD01,15,12,14.5,2\n")
    f.write("ETUD02,16,8,9,5\n")
    f.write("ETUD03,15,18,17,0\n")
    f.write("ETUD04,17,14,13.5,1\n")
    f.write("ETUD05,16,10,11,3\n")
    f.write("ETUD06,15,15,14,2\n")
    f.write("ETUD07,17,7,8,6\n")
    f.write("ETUD08,16,16,16.5,0\n")
    f.write("ETUD09,15,13,12.5,2\n")
    f.write("ETUD10,16,9,10.5,4\n")

def encode_multipart_formdata(fields, files):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    for key, value in fields.items():
        body.append('--' + boundary)
        body.append(f'Content-Disposition: form-data; name="{key}"')
        body.append('')
        body.append(str(value))
    for key, filename, value in files:
        body.append('--' + boundary)
        body.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
        body.append(f'Content-Type: {mimetypes.guess_type(filename)[0] or "application/octet-stream"}')
        body.append('')
        body.append(value.decode('utf-8') if isinstance(value, bytes) else str(value))
    body.append('--' + boundary + '--')
    body.append('')
    body_str = '\r\n'.join(body)
    return body_str.encode('utf-8'), boundary

print("--- Step 1: Upload ---")
with open(TEST_FILE, 'rb') as f:
    file_content = f.read()

body, boundary = encode_multipart_formdata(
    {'mode': 'add'},
    [('file', TEST_FILE, file_content)]
)
req = urllib.request.Request(f"{BASE_URL}/upload/dynamic", data=body)
req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')

try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'): print(e.read().decode())
    exit(1)

id_import = data['id_import']
temp_path = data['temp_path']
analysis = data['analysis']
print(f"Success! ID: {id_import}")
print("Suggested ID col:", analysis['suggested_id_column'])
print("Suggested Target col:", analysis['suggested_target_column'])

print("\n--- Step 2: Ingest ---")
payload = {
    'id_import': id_import,
    'temp_path': temp_path,
    'id_column': analysis['suggested_id_column'] or 'Matricule',
    'target_column': analysis['suggested_target_column'] or 'Note_Finale',
    'mode': 'add'
}
req = urllib.request.Request(f"{BASE_URL}/pipeline/ingest-dynamic", data=json.dumps(payload).encode('utf-8'))
req.add_header('Content-Type', 'application/json')
try:
    with urllib.request.urlopen(req) as res:
        print(f"Ingest Success! Rows: {json.loads(res.read().decode())['rows_ingested']}")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

print("\n--- Step 3: Train & Predict ---")
req = urllib.request.Request(f"{BASE_URL}/pipeline/run-dynamic/{id_import}", data=b'')
try:
    with urllib.request.urlopen(req) as res:
        result = json.loads(res.read().decode())
        print("Run Success!")
        print(f"R2 Score: {result['training']['r2_score']}")
        print(f"MAE: {result['training']['mae']}")
        print(f"Total Predictions: {result['predictions_count']}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'): print(e.read().decode())
    exit(1)

print("\n--- Clean up ---")
try:
    os.remove(TEST_FILE)
    req = urllib.request.Request(f"{BASE_URL}/imports/{id_import}", method='DELETE')
    with urllib.request.urlopen(req) as res:
        pass
    print("Test completed and cleaned up.")
except:
    pass
