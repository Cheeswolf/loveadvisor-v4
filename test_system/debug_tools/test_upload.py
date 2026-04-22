import requests
import time
import sys

def test_upload():
    url = "http://localhost:8000/api/v1/image-to-text"
    # Use provider=qwen_ocr (default)
    files = [('images', ('test.png', open('test.png', 'rb'), 'image/png'))]
    # provider is a query parameter, not form data
    params = {'provider': 'qwen_ocr'}

    print(f"Sending POST to {url} with provider=qwen_ocr as query param")
    try:
        response = requests.post(url, files=files, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    # Wait a bit for server to start
    time.sleep(2)
    test_upload()