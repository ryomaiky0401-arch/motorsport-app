import json
import os
import streamlit as st

DATA_FILE = "race_results.json"
CATEGORIES = [
    "SUPER GT",
    "Super Formula",
    "WEC",
    "F1",
    "F2",
    "F3",
    "GTWC Asia",
    "Japan Cup",
]


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {
      cat: {"race_name": "-", "p1": "-", "p2": "-", "p3": "-"}
      for cat in CATEGORIES
  }


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


st.set_page_config(
    page_title="モータースポーツ結果", layout="wide", initial_sidebar_state="expanded"
)
st.title("🏎️ モータースポーツ レース結果")

data = load_data()

st.sidebar.header("📝 結果の入力・更新")
selected_cat = st.sidebar.selectbox("カテゴリー選択", CATEGORIES)

with st.sidebar.form("input_form"):
  race_name = st.text_input(
      "レース名 / ラウンド", value=data[selected_cat]["race_name"]
  )
  p1 = st.text_input("🥇 1位", value=data[selected_cat]["p1"])
  p2 = st.text_input("🥈 2位", value=data[selected_cat]["p2"])
  p3 = st.text_input("🥉 3位", value=data[selected_cat]["p3"])

  submitted = st.form_submit_button("結果を更新する")
  if submitted:
    data[selected_cat] = {
        "race_name": race_name,
        "p1": p1,
        "p2": p2,
        "p3": p3,
    }
    save_data(data)
    st.sidebar.success(f"{selected_cat} の結果を更新しました！")
    st.rerun()

st.subheader("🏁 最新レース結果一覧")
cols = st.columns(2)

for i, cat in enumerate(CATEGORIES):
  col = cols[i % 2]
  cat_data = data[cat]

  with col:
    with st.container(border=True):
      st.markdown(f"### **{cat}**")
      st.caption(f"レース: {cat_data['race_name']}")
      st.write(f"🥇 **1位:** {cat_data['p1']}")
      st.write(f"🥈 **2位:** {cat_data['p2']}")
      st.write(f"🥉 **3位:** {cat_data['p3']}")
