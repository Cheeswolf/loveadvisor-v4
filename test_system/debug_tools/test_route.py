"""
Test route using FastAPI TestClient to trigger route logging.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_image_to_text():
    # Create a dummy image file in memory
    dummy_image = io.BytesIO()
    # Write a minimal PNG (1x1 black pixel)
    dummy_image.write(b'\x89PNG\r\n\x1a\n')
    dummy_image.write(b'\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde')
    dummy_image.write(b'\x00\x00\x00\x0cIDATx\x9cc\x00\x00\x00\x01\x00\x01\xee\xef\xb5\x07\x00\x00\x00\x00IEND\xaeB`\x82')
    dummy_image.seek(0)

    files = [('images', ('test.png', dummy_image, 'image/png'))]
    params = {'provider': 'qwen_ocr'}

    print("Sending POST to /api/v1/image-to-text via TestClient")
    response = client.post("/api/v1/image-to-text", files=files, params=params)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    return response

if __name__ == "__main__":
    test_image_to_text()