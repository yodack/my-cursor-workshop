from api.models import Product, ProductCreate
from api.storage import InMemoryStorage


def test_create_product_assigns_id_and_stores_it() -> None:
    """商品を作成すると、IDが採番され、保存されることをテストする"""
    storage = InMemoryStorage()
    product_data = ProductCreate(name="テスト商品", price=100.0)

    # 商品を作成
    created_product = storage.create_product(product_data)

    # 検証
    assert isinstance(created_product, Product)
    assert created_product.id == 1
    assert created_product.name == "テスト商品"
    assert storage.get_product(1) == created_product


def test_get_nonexistent_product_returns_none() -> None:
    """存在しない商品IDを取得しようとするとNoneが返ることをテストする"""
    storage = InMemoryStorage()
    assert storage.get_product(999) is None
