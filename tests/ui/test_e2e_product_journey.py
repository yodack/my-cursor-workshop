"""商品管理UIのE2Eテスト。

商品登録から検索までの一連のユーザージャーニーをテストします。
"""

import re
from time import sleep

import pytest
from playwright.sync_api import Page, expect

# --- 定数 ---
UI_URL = "http://localhost:8501"
API_URL = "http://localhost:8080"
PRODUCT_NAME = "E2Eテスト商品"
PRODUCT_PRICE = "12345"


def test_product_creation_and_search_journey(page: Page) -> None:
    """商品登録から検索までの一連のE2Eテストを実行する。"""
    # 1. Streamlitアプリにアクセス
    page.goto(UI_URL)

    # 2. 新しい商品を登録フォームに入力
    page.get_by_label("商品名").fill(PRODUCT_NAME)
    page.get_by_label("価格").fill(PRODUCT_PRICE)
    page.get_by_role("button", name="商品を登録").click()

    # 3. 登録成功のメッセージと結果が表示されることを確認
    expect(page.get_by_text("商品を登録しました！")).to_be_visible()
    response_element = page.locator('div[data-testid="stCodeBlock"]').first
    try:
        # CI環境でのレンダリング遅延を考慮し、タイムアウトを10秒に延長
        expect(response_element).to_be_visible(timeout=10000)
    except AssertionError as e:
        print("DEBUG: Page content on creation failure:")
        print(page.content())
        pytest.fail(f"Failed to find response element. Page content logged. Original error: {e}")

    # 4. 登録された商品のIDをJSONレスポンスから抽出
    json_text = response_element.inner_text()
    match = re.search(r'"id":\s*(\d+)', json_text)
    assert match, f"レスポンスから商品IDが見つかりませんでした: {json_text}"
    product_id = match.group(1)

    # 少し待機してUIの更新を確実にする
    sleep(1)

    # 5. 抽出したIDを使って商品を検索
    page.get_by_label("商品ID").fill(product_id)
    page.get_by_role("button", name="商品を検索").click()

    # 6. 検索成功のメッセージが表示されることを確認
    expect(page.get_by_text("商品が見つかりました！")).to_be_visible()

    # 7. 検索結果が正しいことを確認
    search_result_element = page.locator('div[data-testid="stCodeBlock"]').last
    try:
        # CI環境でのレンダリング遅延を考慮し、タイムアウトを10秒に延長
        expect(search_result_element).to_be_visible(timeout=10000)
    except AssertionError as e:
        print("DEBUG: Page content on search failure:")
        print(page.content())
        pytest.fail(
            f"Failed to find search result element. Page content logged. Original error: {e}"
        )

    expect(search_result_element).to_contain_text(f'"id": {product_id}')
    expect(search_result_element).to_contain_text(f'"name": "{PRODUCT_NAME}"')
    expect(search_result_element).to_contain_text(f'"price": {float(PRODUCT_PRICE)}')
