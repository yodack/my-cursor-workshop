import httpx
import streamlit as st

# APIのベースURL
API_BASE_URL = "http://localhost:8000"

st.title("商品管理アプリ")

# --- サイドバー ---
st.sidebar.header("商品登録")
with st.sidebar.form(key="product_form"):
    name: str = st.text_input("商品名", key="product_name")
    price: float = st.number_input("価格", min_value=0.0, step=0.01, key="product_price")
    create_button = st.form_submit_button(label="商品を登録")

st.sidebar.header("商品検索")
with st.sidebar.form(key="search_form"):
    search_id: int = st.number_input("商品ID", min_value=1, step=1, key="search_id")
    search_button = st.form_submit_button(label="商品を検索")

# --- メイン画面 ---
if create_button:
    # APIに送信するデータを作成
    item_data = {"name": name, "price": price}

    with st.spinner("商品を登録しています..."):
        try:
            response = httpx.post(f"{API_BASE_URL}/items", json=item_data)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生させる

            # 成功した場合
            st.success("商品を登録しました！")
            created_item = response.json()
            st.json(created_item)

        except httpx.HTTPStatusError as e:
            # HTTPエラー（4xx, 5xx）の場合
            if e.response.status_code == 422:
                st.error("入力内容に誤りがあります。")
                st.json(e.response.json())
            else:
                st.error(f"サーバーエラーが発生しました: {e.response.status_code}")
                st.text(e.response.text)
        except httpx.RequestError as e:
            # 接続エラーなどの場合
            st.error(f"APIへの接続に失敗しました: {e}")

# 検索ボタンが押された場合
if search_button:
    with st.spinner(f"商品ID: {search_id} を検索しています..."):
        try:
            response = httpx.get(f"{API_BASE_URL}/items/{search_id}")
            response.raise_for_status()

            st.success("商品が見つかりました！")
            found_item = response.json()
            st.json(found_item)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                st.warning("指定された商品IDは見つかりませんでした。")
            else:
                st.error(f"サーバーエラーが発生しました: {e.response.status_code}")
                st.text(e.response.text)
        except httpx.RequestError as e:
            st.error(f"APIへの接続に失敗しました: {e}")
