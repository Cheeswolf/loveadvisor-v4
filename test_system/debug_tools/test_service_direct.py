import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import UploadFile
from app.services.image_to_text_service import image_to_text

async def test():
    # Create a mock UploadFile from test.png
    with open('test.png', 'rb') as f:
        # UploadFile expects async read, so we need to wrap
        # Instead, we can use a simple mock
        from io import BytesIO
        content = f.read()
        file_like = BytesIO(content)
        upload_file = UploadFile(filename='test.png', file=file_like)
        # Call service with provider=qwen_ocr
        response = await image_to_text([upload_file], provider='qwen_ocr')
        print(f"Response: {response}")
        print(f"Provider: {response.provider}")
        print(f"Metadata: {response.metadata}")

if __name__ == '__main__':
    asyncio.run(test())