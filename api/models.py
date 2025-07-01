from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """商品作成時のデータモデル"""

    name: str = Field(..., min_length=1, description="商品名")
    price: float = Field(..., gt=0, description="価格")


class Product(ProductCreate):
    """商品データモデル（レスポンス用）"""

    id: int = Field(..., description="商品ID")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
