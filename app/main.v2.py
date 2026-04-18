from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analyze import router as analyze_router

app = FastAPI()

# =========================
# CORS（前端联调需要）
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地开发先全开；上线后改成前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(analyze_router)