from fastapi import FastAPI, HTTPException

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


@app.get("/items/{item_id}", response_model=Product)
async def get_item(item_id: int) -> Product:
    """IDで商品を検索する"""
    item = storage.get_product(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
