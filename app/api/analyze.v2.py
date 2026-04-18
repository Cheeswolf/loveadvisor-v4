from typing import Any, Dict

from fastapi import APIRouter

from app.services.pipeline_service import run_pipeline

router = APIRouter()


@router.get("/")
def root():
    return {"message": "LoveAdvisor V2 backend is running."}


print("=== ANALYZE ROUTE HIT ===")

@router.post("/analyze")
def analyze(request: dict):
    print("=== ANALYZE ROUTE HIT ===")

    text = request.get("text", "")
    print("=== INPUT TEXT ===", text)

    print("=== BEFORE PIPELINE CALL ===")

    result = run_pipeline(text)   # ← 关键：你要确认这一行

    print("=== AFTER PIPELINE CALL ===", result)

    return result