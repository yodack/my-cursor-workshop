import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.anyio
async def test_health_check() -> None:
    """/healthエンドポイントが正常に動作することを確認するテスト"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_create_item_returns_201() -> None:
    """商品作成エンドポイントが201を返すことをテストする"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/items", json={"name": "テスト商品", "price": 1000})
    assert response.status_code == 201
    created_item = response.json()
    assert created_item["name"] == "テスト商品"
    assert created_item["price"] == 1000
    assert "id" in created_item
    assert "created_at" in created_item


@pytest.mark.anyio
async def test_create_item_with_invalid_price_returns_422() -> None:
    """不正な価格で商品を作成しようとすると422エラーが返ることをテストする"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/items", json={"name": "テスト商品", "price": 0})
    assert response.status_code == 422
