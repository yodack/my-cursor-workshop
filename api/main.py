from fastapi import FastAPI

app = FastAPI(title="商品管理API")


@app.get("/health")
async def health_check() -> dict:
    """APIのヘルスチェック"""
    return {"status": "ok"}
