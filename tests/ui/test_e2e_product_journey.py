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

    # 3. 登録成功のメッセージと、レスポンスのテキストが表示されることを確認
    expect(page.get_by_text("商品を登録しました！")).to_be_visible()

    try:
        # JSONの空白差異を許容するため、正規表現でテキストを検証
        name_pattern = re.compile(rf'"name"\s*:\s*"{PRODUCT_NAME}"')
        price_pattern = re.compile(rf'"price"\s*:\s*{float(PRODUCT_PRICE)}')
        expect(page.get_by_text(name_pattern)).to_be_visible(timeout=10000)
        expect(page.get_by_text(price_pattern)).to_be_visible(timeout=10000)
    except AssertionError as e:
        print("DEBUG: Page content on creation failure:")
        print(page.content())
        pytest.fail(f"Failed to find response text. Page content logged. Original error: {e}")

    # 4. 登録された商品のIDをページ全体のテキストから抽出
    page_text = page.locator("body").inner_text()
    match = re.search(r'"id"\s*:\s*(\d+)', page_text)
    assert match, f"レスポンスから商品IDが見つかりませんでした: {page_text}"
    product_id = match.group(1)

    # 少し待機してUIの更新を確実にする
    sleep(1)

    # 5. 抽出したIDを使って商品を検索
    page.get_by_label("商品ID").fill(product_id)
    page.get_by_role("button", name="商品を検索").click()

    # 6. 検索成功のメッセージが表示されることを確認
    expect(page.get_by_text("商品が見つかりました！")).to_be_visible()

    # 7. 検索結果が正しいことを確認 (正規表現使用)
    try:
        id_pattern = re.compile(rf'"id"\s*:\s*{product_id}')
        name_pattern = re.compile(rf'"name"\s*:\s*"{PRODUCT_NAME}"')
        price_pattern = re.compile(rf'"price"\s*:\s*{float(PRODUCT_PRICE)}')
        expect(page.get_by_text(id_pattern)).to_be_visible(timeout=10000)
        expect(page.get_by_text(name_pattern)).to_be_visible(timeout=10000)
        expect(page.get_by_text(price_pattern)).to_be_visible(timeout=10000)
    except AssertionError as e:
        print("DEBUG: Page content on search failure:")
        print(page.content())
        pytest.fail(f"Failed to find search result text. Page content logged. Original error: {e}")
