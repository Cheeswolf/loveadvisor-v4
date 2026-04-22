"""
Script to trigger /api/v1/image-to-text API call and collect logs.
"""
import requests
import time
import sys
import subprocess
import os
from pathlib import Path

def wait_for_server(port=8000, timeout=30):
    """Wait until server is reachable on given port."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"http://localhost:{port}/health")
            if response.status_code == 200:
                print(f"Server is up on port {port}")
                return True
        except Exception:
            pass
        time.sleep(1)
    print(f"Server did not start within {timeout} seconds")
    return False

def start_server():
    """Start uvicorn server in background."""
    # Check if already running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("Server already running")
            return None
    except Exception:
        pass

    # Start server
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        print("Virtual environment not found")
        return None

    # Run uvicorn as subprocess
    cmd = [str(venv_python), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    print(f"Starting server: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
    time.sleep(2)  # give it a moment
    return proc

def send_request():
    """Send POST request to image-to-text endpoint."""
    url = "http://localhost:8000/api/v1/image-to-text"
    # Create a dummy image file if not exists
    dummy_image = Path("dummy.png")
    if not dummy_image.exists():
        # Create a minimal PNG (1x1 black pixel)
        import struct
        with open(dummy_image, 'wb') as f:
            # PNG signature
            f.write(b'\x89PNG\r\n\x1a\n')
            # IHDR chunk
            f.write(struct.pack('>I', 13))  # length
            f.write(b'IHDR')
            f.write(struct.pack('>I', 1))   # width
            f.write(struct.pack('>I', 1))   # height
            f.write(b'\x08\x02\x00\x00\x00') # bit depth, color type, compression, filter, interlace
            f.write(struct.pack('>I', 0x0a7a6d78)) # CRC placeholder
            # IDAT chunk
            f.write(struct.pack('>I', 12))  # length
            f.write(b'IDAT')
            f.write(b'\x78\x9c\x63\x00\x00\x00\x01\x00\x01') # compressed data
            f.write(struct.pack('>I', 0x2eefb507)) # CRC placeholder
            # IEND chunk
            f.write(struct.pack('>I', 0))   # length
            f.write(b'IEND')
            f.write(struct.pack('>I', 0xae426082)) # CRC

    files = [('images', ('dummy.png', open(dummy_image, 'rb'), 'image/png'))]
    params = {'provider': 'qwen_ocr'}

    print(f"Sending POST to {url} with provider=qwen_ocr")
    try:
        response = requests.post(url, files=files, params=params, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def main():
    proc = None
    try:
        # Start server if not running
        proc = start_server()
        if proc is None:
            # Maybe already running
            pass

        # Wait for server to be ready
        if not wait_for_server():
            print("Failed to start server")
            return

        # Send request
        response = send_request()

        # Print debug logs
        print("\n=== Checking debug files ===")
        debug_files = ['debug_image_service.log', 'debug_provider.txt', 'debug_implementation.txt',
                      'debug_route_final.txt', 'debug_route_error.txt']
        for fname in debug_files:
            if Path(fname).exists():
                print(f"\n--- {fname} ---")
                with open(fname, 'r', encoding='utf-8') as f:
                    print(f.read())
            else:
                print(f"{fname} not found")

        # Also check ~/debug_endpoint.txt and ~/debug_image_to_text.txt
        home = Path.home()
        home_debug = home / 'debug_endpoint.txt'
        if home_debug.exists():
            print(f"\n--- {home_debug} ---")
            with open(home_debug, 'r', encoding='utf-8') as f:
                print(f.read())
        home_debug2 = home / 'debug_image_to_text.txt'
        if home_debug2.exists():
            print(f"\n--- {home_debug2} ---")
            with open(home_debug2, 'r', encoding='utf-8') as f:
                print(f.read())

    finally:
        # Keep server running for now
        # if proc:
        #     proc.terminate()
        #     proc.wait()
        pass

if __name__ == "__main__":
    main()