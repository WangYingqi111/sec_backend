from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import screener_api

app = FastAPI(title="Stock Screener API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
# prefix意思是所有该文件下的接口都以 /api/stock_screener 开头
app.include_router(screener_api.router, prefix="/api/stock_screener", tags=["Screener"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI backend is running"}