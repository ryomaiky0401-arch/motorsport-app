import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "race_data_v4.json"

# カテゴリーとクラスの設定
CATEGORY_CONFIG = {
    "SUPER GT": ["GT500", "GT300"],
    "Super Formula": ["総合"],
    "WEC": ["Hypercar", "LMGT3"],
    "F1": ["総合"],
    "F2": ["総合"],
    "F3": ["総合"],
    "GTWC Asia": ["Pro", "Pro-Am", "Silver", "Am"],
    "Japan Cup": ["Pro", "Pro-Am", "Silver", "Am"],
}

# 獲得ポイントの基本配点（1位〜10位）
POINTS_TABLE = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  return {"races": {}, "teams": {}}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


st.set_page_config(
    page_title="モータースポーツ総合結果 & ランキング",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🏎️ モータースポーツ ダッシュボード")

data = load_data()
if "races" not in data:
  data["races"] = {}
if "teams" not in data:
  data["teams"] = {}

# タブ切り替え（レース結果 / ポイントランキング / チーム・車両登録）
tab1, tab2, tab3 = st.tabs(
    ["🏁 レース結果閲覧", "🏆 ポイントランキング", "⚙️ 車両・チームマスタ登録"]
)

# --- タブ3: チーム・車両の登録 ---
with tab3:
  st.header("⚙️ 参加チーム・車両の登録")
  st.caption(
      "ここでカテゴリーごとにチームや車両を登録しておくと、入力時に全台数分を選択できるようになります。"
  )

  c1, c2 = st.columns(2)
  with c1:
    m_cat = st.selectbox("カテゴリー", list(CATEGORY_CONFIG.keys()), key="m_cat")
  with c2:
    m_cls = st.selectbox("クラス", CATEGORY_CONFIG[m_cat], key="m_cls")

  key_name = f"{m_cat}_{m_cls}"
  current_teams = data["teams"].get(key_name, [])

  new_team = st.text_input("追加するチーム名 / 車両名（例: #36 au TOM'S GR Supra）")
  if st.button("チームを追加"):
    if new_team and new_team not in current_teams:
      current_teams.append(new_team)
      data["teams"][key_name] = current_teams
      save_data(data)
      st.success(f"「{new_team}」を登録しました！")
      st.rerun()

  st.subheader("登録済み一覧")
  if current_teams:
    for t in current_teams:
      st.write(f"・ {t}")
  else:
    st.info("まだ登録されていません。")

# --- サイドバー：レース結果の入力 ---
st.sidebar.header("📝 レース結果入力")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")

team_key = f"{s_cat}_{s_cls}"
registered_teams = data["teams"].get(team_key, [])

with st.sidebar.form("race_input_form"):
  race_name = st.text_input(
      "レース名 / ラウンド", placeholder="例: Rd.1 岡山"
  )

  st.caption("順位順（1位から順番）にチームを選択してください")
  selected_results = []

  if registered_teams:
    # 登録されている全台数分の選択ボックスを自動生成
    for rank in range(1, len(registered_teams) + 1):
      team = st.selectbox(
          f"{rank}位",
          ["(選択なし)"] + registered_teams,
          key=f"rank_{rank}",
      )
      if team != "(選択なし)":
        selected_results.append(team)
  else:
    st.warning("先に「⚙️ 車両・チームマスタ登録」タブでチームを登録してください。")

  # フォーム内の保存ボタン（修正箇所）
  submitted = st.form_submit_button("レース結果を保存する")

  if submitted:
    if not race_name:
      st.sidebar.error("レース名を入力してください。")
    elif not selected_results:
      st.sidebar.error("少なくとも1つ以上の順位を選択してください。")
    else:
      if s_cat not in data["races"]:
        data["races"][s_cat] = {}
      if s_cls not in data["races"][s_cat]:
        data["races"][s_cat][s_cls] = []

      data["races"][s_cat][s_cls].append(
          {"race_name": race_name, "results": selected_results}
      )
      save_data(data)
      st.sidebar.success(f"「{race_name}」の結果を保存しました！")
      st.rerun()

# --- タブ1: レース結果閲覧 ---
with tab1:
  st.header("🏁 レース結果")
  v_c1, v_c2 = st.columns(2)
  with v_c1:
    v_cat = st.selectbox(
        "カテゴリー選択", list(CATEGORY_CONFIG.keys()), key="v_cat"
    )
  with v_c2:
    v_cls = st.selectbox("クラス選択", CATEGORY_CONFIG[v_cat], key="v_cls")

  if (
      v_cat in data["races"]
      and v_cls in data["races"][v_cat]
      and len(data["races"][v_cat][v_cls]) > 0
  ):
    races = data["races"][v_cat][v_cls]
    race_names = [r["race_name"] for r in reversed(races)]
    sel_race = st.selectbox("レースを選択", race_names)

    target = next(r for r in races if r["race_name"] == sel_race)

    df_res = pd.DataFrame({
        "順位": [f"P{i+1}" for i in range(len(target["results"]))],
        "獲得ポイント": [
            f"{POINTS_TABLE[i]} pt" if i < len(POINTS_TABLE) else "0 pt"
            for i in range(len(target["results"]))
        ],
        "チーム / 車両": target["results"],
    })
    st.dataframe(df_res, use_container_width=True, hide_index=True)
  else:
    st.info("レース結果データがありません。")

# --- タブ2: ポイントランキング自動計算 ---
with tab2:
  st.header("🏆 年間ポイントランキング")
  r_c1, r_c2 = st.columns(2)
  with r_c1:
    r_cat = st.selectbox(
        "カテゴリー選択", list(CATEGORY_CONFIG.keys()), key="r_cat"
    )
  with r_c2:
    r_cls = st.selectbox("クラス選択", CATEGORY_CONFIG[r_cat], key="r_cls")

  if r_cat in data["races"] and r_cls in data["races"][r_cat]:
    scores = {}
    races = data["races"][r_cat][r_cls]

    for r in races:
      for idx, team in enumerate(r["results"]):
        pt = POINTS_TABLE[idx] if idx < len(POINTS_TABLE) else 0
        scores[team] = scores.get(team, 0) + pt

    if scores:
      sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

      df_rank = pd.DataFrame({
          "順位": [f"{i+1} 位" for i in range(len(sorted_scores))],
          "チーム / 車両": [item[0] for item in sorted_scores],
          "合計ポイント": [f"{item[1]} pt" for item in sorted_scores],
      })
      st.dataframe(df_rank, use_container_width=True, hide_index=True)
    else:
      st.info("集計対象のデータがありません。")
  else:
    st.info("レース結果データがありません。")
