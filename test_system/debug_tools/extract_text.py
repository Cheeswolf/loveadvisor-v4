import json
with open('i1_response.json', 'rb') as f:
    data = f.read().decode('utf-8')
d = json.loads(data)
print(d.get('merged_text', ''))