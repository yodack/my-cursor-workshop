from fastapi import FastAPI

from api.models import Product, ProductCreate
from api.storage import InMemoryStorage

app = FastAPI(title="商品管理API")
storage = InMemoryStorage()


@app.get("/health")
async def health_check() -> dict:
    """APIのヘルスチェック"""
    return {"status": "ok"}


@app.post("/items", response_model=Product, status_code=201)
async def create_item(item: ProductCreate) -> Product:
    """商品を作成する"""
    return storage.create_product(item)
