import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "race_results_v2.json"

# カテゴリーとクラスの定義
CATEGORY_CONFIG = {
    "SUPER GT": ["GT500", "GT300"],
    "Super Formula": ["総合"],
    "WEC": ["Hypercar", "LMGT3"],
    "F1": ["総合"],
    "F2": ["総合"],
    "F3": ["総合"],
    "GTWC Asia": ["GT3", "GT4"],
    "Japan Cup": ["GT3", "GT4"],
}


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


st.set_page_config(
    page_title="モータースポーツ総合結果",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🏎️ モータースポーツ レース結果ダッシュボード")

data = load_data()

# --- サイドバー：データ入力・登録 ---
st.sidebar.header("📝 レース結果の登録")

selected_cat = st.sidebar.selectbox(
    "カテゴリー選択", list(CATEGORY_CONFIG.keys())
)
available_classes = CATEGORY_CONFIG[selected_cat]
selected_class = st.sidebar.selectbox("クラス選択", available_classes)

with st.sidebar.form("input_form"):
  race_name = st.text_input(
      "レース名 / ラウンド",
      placeholder="例: Rd.1 岡山 / 24 Hours of Le Mans",
  )
  st.caption("順位一覧（1行に1チーム・ドライバーを入力してください）")
  results_text = st.text_area(
      "全順位（改行で入力）",
      height=200,
      placeholder="1位のチーム\n2位のチーム\n3位のチーム\n4位のチーム...",
  )

  submitted = st.form_submit_button("レース結果を保存する")

  if submitted and race_name and results_text:
    # データを整形
    drivers_list = [
        line.strip() for line in results_text.split("\n") if line.strip()
    ]

    if selected_cat not in data:
      data[selected_cat] = {}
    if selected_class not in data[selected_cat]:
      data[selected_cat][selected_class] = []

    # 重複チェック＆上書き/新規追加
    existing_races = data[selected_cat][selected_class]
    updated = False
    for r in existing_races:
      if r["race_name"] == race_name:
        r["results"] = drivers_list
        updated = True
        break

    if not updated:
      data[selected_cat][selected_class].append(
          {"race_name": race_name, "results": drivers_list}
      )

    save_data(data)
    st.sidebar.success(
        f"【{selected_cat} / {selected_class}】{race_name} を保存しました！"
    )
    st.rerun()

# --- メイン画面：閲覧表示 ---
st.subheader("🏁 レース結果閲覧")

col_cat, col_cls = st.columns(2)
with col_cat:
  view_cat = st.selectbox("閲覧したいカテゴリー", list(CATEGORY_CONFIG.keys()))
with col_cls:
  view_cls = st.selectbox("クラス", CATEGORY_CONFIG[view_cat])

st.divider()

# 表示処理
if (
    view_cat in data
    and view_cls in data[view_cat]
    and len(data[view_cat][view_cls]) > 0
):
  races = data[view_cat][view_cls]

  # レース選択（最新が一番上に来るよう逆順）
  race_names = [r["race_name"] for r in reversed(races)]
  selected_race_name = st.selectbox("🏆 レースを選択（過去ログ）", race_names)

  # 該当レースの検索
  target_race = next(
      r for r in races if r["race_name"] == selected_race_name
  )

  st.markdown(f"### **{view_cat} - {view_cls}**｜ `{target_race['race_name']}`")

  # 順位表を作成
  df = pd.DataFrame(
      {
          "順位": [f"P{i+1}" for i in range(len(target_race["results"]))],
          "チーム / ドライバー": target_race["results"],
      }
  )

  # 表の表示
  st.dataframe(df, use_container_width=True, hide_index=True)

else:
  st.info(
      f"現在【{view_cat} - {view_cls}】の登録データはありません。左側のフォームから入力してください。"
  )
