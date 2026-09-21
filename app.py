import datetime
import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "race_data_v13.json"

CATEGORY_CONFIG = {
    "SUPER GT": ["GT500", "GT300"],
    "Super Formula": ["総合"],
    "WEC": ["Hypercar", "LMGT3"],
    "F1": ["総合"],
    "GTWC Asia": ["Pro", "Pro-Am", "Silver", "Am"],
}

# 各カテゴリーのデフォルト初期チームリスト（入力の手間を減らすためのプリセット）
DEFAULT_TEAMS = {
    "SUPER GT_GT500": [
        "#36 au TOM'S GR Supra",
        "#37 Deloitte TOM'S GR Supra",
        "#3 NITERRA MOTUL Z",
        "#23 MOTUL AUTECH Z",
        "#100 STANLEY CIVIC TYPE R-GT",
        "#8 ARTA CIVIC TYPE R-GT #8",
        "#16 ARTA CIVIC TYPE R-GT #16",
        "#14 ENEOS X PRIME GR Supra",
        "#38 KeePer CERUMO GR Supra",
        "#39 DENSO KOBELCO SARD GR Supra",
        "#12 MARELLI IMPUL Z",
        "#17 Astemo CIVIC TYPE R-GT",
        "#64 Modulo CIVIC TYPE R-GT",
        "#19 WedsSport ADVAN GR Supra",
        "#24 リアライズコーポレーション ADVAN Z",
    ]
}

DEFAULT_PTS_RACE = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
DEFAULT_PTS_QUALIFY = [3, 2, 1, 0, 0, 0, 0, 0, 0, 0]
DEFAULT_PTS_SPRINT = [8, 7, 6, 5, 4, 3, 2, 1, 0, 0]

YEARS = ["2026年", "2025年", "2024年", "2023年"]


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      if "teams" not in data:
        data["teams"] = {}
      if "points_master" not in data:
        data["points_master"] = {}
      return data
  return {"races": {}, "teams": {}, "points_master": {}}


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


st.set_page_config(
    page_title="モータースポーツ総合結果 & ランキング", layout="wide"
)
st.title("🏎️ モータースポーツ ダッシュボード")

data = load_data()

tab1, tab2, tab3 = st.tabs(
    ["🏁 レース結果閲覧・編集", "🏆 ポイントランキング", "⚙️ チームマスタ管理"]
)

# ---------------------------------------------------------
# サイドバー：確実な「マスタ選択式」結果入力
# ---------------------------------------------------------
st.sidebar.header("📝 レース結果の入力")
s_year = st.sidebar.selectbox("シーズン年度", YEARS, key="s_year")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")

team_key = f"{s_cat}_{s_cls}"

# 該当クラスの登録済みチームを取得
registered_teams = data["teams"].get(team_key, [])

# プリセット初期値が未読み込みの場合はセット
if not registered_teams and team_key in DEFAULT_TEAMS:
  data["teams"][team_key] = DEFAULT_TEAMS[team_key]
  save_data(data)
  registered_teams = DEFAULT_TEAMS[team_key]

st.sidebar.markdown("---")

session_type = st.sidebar.radio(
    "セッション種別", ["決勝", "予選", "スプリント"], index=0
)
race_date = st.sidebar.date_input("開催日", value=datetime.date.today())
race_name = st.sidebar.text_input("レース名 / ラウンド", placeholder="例: Rd.1 岡山")

st.sidebar.markdown("---")
st.sidebar.subheader("🏆 順位の選択")

if not registered_teams:
  st.sidebar.warning(
      "⚠️ チームがまだ登録されていません。「⚙️ チームマスタ管理」タブでチームを追加してください。"
  )
  team_options = ["(未登録)"]
else:
  team_options = ["-- 選択してください --"] + registered_teams

# 1位〜10位（必要に応じて拡大可能）の選択ボックス
max_rank_input = st.sidebar.slider("入力する順位の数", 5, 20, 10)

selected_results = []
for rank in range(1, max_rank_input + 1):
  selected_team = st.sidebar.selectbox(
      f"{rank} 位", options=team_options, key=f"select_rank_{rank}"
  )
  if selected_team and selected_team != "-- 選択してください --":
    selected_results.append(selected_team)

# ポイントルールの設定
base_pts = data["points_master"].get(
    s_cat,
    {
        "決勝": DEFAULT_PTS_RACE,
        "予選": DEFAULT_PTS_QUALIFY,
        "スプリント": DEFAULT_PTS_SPRINT,
    },
).get(session_type, DEFAULT_PTS_RACE)

use_custom_pts = st.sidebar.checkbox(
    "⚠️ このレース専用ポイントを使う", value=False
)
applied_pts = base_pts.copy()

if use_custom_pts:
  applied_pts = []
  pts_cols = st.sidebar.columns(2)
  for i in range(10):
    col = pts_cols[0] if i < 5 else pts_cols[1]
    val = col.number_input(
        f"{i+1}位 pt",
        min_value=0,
        max_value=200,
        value=base_pts[i] if i < len(base_pts) else 0,
        key=f"c_pt_{i}",
    )
    applied_pts.append(val)

st.sidebar.markdown("---")
if st.sidebar.button("💾 レース結果を保存する", type="primary"):
  if not race_name:
    st.sidebar.error("レース名を入力してください。")
  elif not selected_results:
    st.sidebar.error("少なくとも1つの順位を選択してください。")
  else:
    if s_year not in data["races"]:
      data["races"][s_year] = {}
    if s_cat not in data["races"][s_year]:
      data["races"][s_year][s_cat] = {}
    if s_cls not in data["races"][s_year][s_cat]:
      data["races"][s_year][s_cat][s_cls] = []

    data["races"][s_year][s_cat][s_cls].append({
        "round_name": race_name,
        "race_date": str(race_date),
        "session_type": session_type,
        "is_custom_pts": use_custom_pts,
        "points_table": applied_pts,
        "results": selected_results,
    })
    save_data(data)
    st.sidebar.success(
        f"[{s_year}]「{race_name} ({session_type})」の結果を保存しました！"
    )
    st.rerun()

# ---------------------------------------------------------
# タブ1: レース結果閲覧
# ---------------------------------------------------------
with tab1:
  st.header("🏁 レース結果 閲覧")
  v_y, v_c1, v_c2 = st.columns(3)
  with v_y:
    v_year = st.selectbox("年度", YEARS, key="v_year")
  with v_c1:
    v_cat = st.selectbox(
        "カテゴリー選択", list(CATEGORY_CONFIG.keys()), key="v_cat"
    )
  with v_c2:
    v_cls = st.selectbox("クラス選択", CATEGORY_CONFIG[v_cat], key="v_cls")

  races_list = (
      data.get("races", {}).get(v_year, {}).get(v_cat, {}).get(v_cls, [])
  )

  if races_list:
    rounds = sorted(
        list(set(r.get("round_name", r.get("race_name")) for r in races_list)),
        reverse=True,
    )
    r_col1, r_col2 = st.columns(2)
    with r_col1:
      sel_round = st.selectbox("ラウンドを選択", rounds)
    with r_col2:
      sel_session_filter = st.selectbox(
          "セッション選択", ["すべて", "決勝", "予選", "スプリント"]
      )

    round_races = [
        r
        for r in races_list
        if r.get("round_name", r.get("race_name")) == sel_round
    ]
    if sel_session_filter != "すべて":
      round_races = [
          r
          for r in round_races
          if r.get("session_type", "決勝") == sel_session_filter
      ]

    if round_races:
      for target in round_races:
        st.subheader(
            f"📍 {sel_round} - 【{target.get('session_type', '決勝')}】"
        )
        st.caption(f"📅 開催日: {target.get('race_date', '未設定')}")

        pts_table = target.get("points_table", DEFAULT_PTS_RACE)
        res_teams = target.get("results", [])

        df_res = pd.DataFrame({
            "順位": [f"P{i+1}" for i in range(len(res_teams))],
            "獲得pt": [
                f"{pts_table[i]} pt" if i < len(pts_table) else "0 pt"
                for i in range(len(res_teams))
            ],
            "チーム / 車両": res_teams,
        })
        st.table(df_res)
    else:
      st.info("該当するセッションのデータがありません。")
  else:
    st.info("登録されているレースデータがありません。")

# ---------------------------------------------------------
# タブ2: ポイントランキング
# ---------------------------------------------------------
with tab2:
  st.header("🏆 年間ポイントランキング")
  r_y, r_c1, r_c2 = st.columns(3)
  with r_y:
    r_year = st.selectbox("年度", YEARS, key="r_year")
  with r_c1:
    r_cat = st.selectbox(
        "カテゴリー選択", list(CATEGORY_CONFIG.keys()), key="r_cat"
    )
  with r_c2:
    r_cls = st.selectbox("クラス選択", CATEGORY_CONFIG[r_cat], key="r_cls")

  if (
      r_year in data["races"]
      and r_cat in data["races"][r_year]
      and r_cls in data["races"][r_year][r_cat]
  ):
    scores = {}
    for r in data["races"][r_year][r_cat][r_cls]:
      pts_table = r.get("points_table", DEFAULT_PTS_RACE)
      for idx, team in enumerate(r["results"]):
        pt = pts_table[idx] if idx < len(pts_table) else 0
        scores[team] = scores.get(team, 0) + pt

    if scores:
      sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
      df_rank = pd.DataFrame({
          "順位": [f"{i+1} 位" for i in range(len(sorted_scores))],
          "チーム / 車両": [item[0] for item in sorted_scores],
          "合計ポイント": [f"{item[1]} pt" for item in sorted_scores],
      })
      st.table(df_rank)
    else:
      st.info("集計対象のデータがありません。")
  else:
    st.info("まだレース結果が登録されていません。")

# ---------------------------------------------------------
# タブ3: チームマスタ管理
# ---------------------------------------------------------
with tab3:
  st.header("⚙️ チームマスタ管理")
  st.caption(
      "ここで登録したチームが、サイドバーのドロップダウン選択肢に反映されます。"
  )

  m_c1, m_c2 = st.columns(2)
  with m_c1:
    m_cat = st.selectbox(
        "管理するカテゴリー", list(CATEGORY_CONFIG.keys()), key="m_cat"
    )
  with m_c2:
    m_cls = st.selectbox("管理するクラス", CATEGORY_CONFIG[m_cat], key="m_cls")

  m_key = f"{m_cat}_{m_cls}"
  current_teams = data["teams"].get(m_key, [])

  st.subheader(f"📋 登録済みチーム一覧 ({m_cat} - {m_cls})")

  if current_teams:
    st.write(current_teams)
  else:
    st.warning("まだチームが登録されていません。")

  st.markdown("---")
  st.subheader("➕ チームの追加")
  new_team_name = st.text_input(
      "追加するチーム・車両名",
      placeholder="例: #100 STANLEY CIVIC TYPE R-GT",
  )

  if st.button("チームを追加する"):
    if new_team_name.strip():
      if m_key not in data["teams"]:
        data["teams"][m_key] = []
      if new_team_name.strip() not in data["teams"][m_key]:
        data["teams"][m_key].append(new_team_name.strip())
        save_data(data)
        st.success(f"「{new_team_name.strip()}」を追加しました！")
        st.rerun()
      else:
        st.error("すでに登録されているチーム名です。")
    else:
      st.error("チーム名を入力してください。")
