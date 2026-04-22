import json
import subprocess
import sys

# Read merged text
with open('merged_text.txt', 'rb') as f:
    chat_text = f.read().decode('utf-8', errors='ignore').strip()

# Prepare request with empty user_question
payload = {
    "chat_text": chat_text,
    "user_question": "",
    "provider_name": "mock"
}

# Write payload to file
with open('analyze_payload.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, ensure_ascii=False)

# Call curl
cmd = ['curl', '-X', 'POST', 'http://127.0.0.1:8000/api/v1/analyze',
       '-H', 'Content-Type: application/json',
       '-d', '@analyze_payload.json']
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("Stderr:", result.stderr, file=sys.stderr)