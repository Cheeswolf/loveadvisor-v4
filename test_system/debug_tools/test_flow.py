#!/usr/bin/env python3
import base64
import json
import os
from io import BytesIO

# 1x1 pixel PNG (transparent)
png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
png_data = base64.b64decode(png_base64)

# Save to temp file
temp_file = "test_1x1.png"
with open(temp_file, "wb") as f:
    f.write(png_data)

print(f"Created test image: {temp_file}")

# Call image-to-text endpoint
import urllib.request
import urllib.parse

url = "http://127.0.0.1:8000/api/v1/image-to-text"
# Prepare multipart form data
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import io

# Build multipart request manually
boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
data = []
data.append(f"--{boundary}")
data.append('Content-Disposition: form-data; name="images"; filename="test.png"')
data.append("Content-Type: image/png")
data.append("")
data.append(png_data.decode('latin-1'))  # This is wrong, need binary
data.append(f"--{boundary}--")
data.append("")

# This is messy, use requests if available
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

if HAS_REQUESTS:
    files = {'images': ('test.png', png_data, 'image/png')}
    data = {'provider': 'qwen_ocr', 'source_type': 'image'}
    resp = requests.post(url, files=files, data=data)
    print(f"Image-to-text status: {resp.status_code}")
    print(resp.json())
    if resp.status_code == 200:
        result = resp.json()
        if result.get('success'):
            merged_text = result.get('merged_text', '')
            print(f"Extracted text: {merged_text}")
            # Now call analyze
            analyze_url = "http://127.0.0.1:8000/api/v1/analyze"
            analyze_data = {
                'chat_text': merged_text,
                'user_question': '测试分析',
                'provider_name': 'mock',
                'debug': False
            }
            analyze_resp = requests.post(analyze_url, json=analyze_data)
            print(f"Analyze status: {analyze_resp.status_code}")
            print(analyze_resp.json())
        else:
            print("Image-to-text failed")
    else:
        print("Image-to-text request failed")
else:
    print("requests library not installed, skipping API calls")

# Clean up
os.remove(temp_file)