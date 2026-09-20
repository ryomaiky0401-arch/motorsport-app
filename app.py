import datetime
import json
import os
import re
import pandas as pd
import streamlit as st

# PDF解析ライブラリのインポート試行
try:
  import pdfplumber

  HAS_PDF_PARSER = True
except ImportError:
  try:
    import pypdf

    HAS_PDF_PARSER = True
  except ImportError:
    HAS_PDF_PARSER = False

DATA_FILE = "race_data_v13.json"

CATEGORY_CONFIG = {
    "SUPER GT": ["GT500", "GT300"],
    "Super Formula": ["総合"],
    "WEC": ["Hypercar", "LMGT3"],
    "F1": ["総合"],
    "GTWC Asia": ["Pro", "Pro-Am", "Silver", "Am"],
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


def extract_text_from_pdf(pdf_file):
  text = ""
  try:
    if "pdfplumber" in globals():
      with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
          text += (page.extract_text() or "") + "\n"
    elif "pypdf" in globals():
      reader = pypdf.PdfReader(pdf_file)
      for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
  except Exception as e:
    st.error(f"PDF解析エラー: {e}")
  return text


def parse_race_text(text):
  """PDF生テキストまたはコピペテキストから情報を抽出する超柔軟ロジック"""
  parsed_info = {
      "race_name": "",
      "race_date": datetime.date.today(),
      "session_type": "決勝",
      "results": [],
  }

  lines = [line.strip() for line in text.split("\n") if line.strip()]

  # 1. 日付抽出
  date_match = re.search(r"(\d{4})[/\-年](\d{1,2})[/\-月](\d{1,2})", text)
  if date_match:
    try:
      parsed_info["race_date"] = datetime.date(
          int(date_match.group(1)),
          int(date_match.group(2)),
          int(date_match.group(3)),
      )
    except ValueError:
      pass

  # 2. セッション抽出
  if "予選" in text or "Qualifying" in text or "QUALIFY" in text:
    parsed_info["session_type"] = "予選"
  elif "スプリント" in text or "Sprint" in text:
    parsed_info["session_type"] = "スプリント"
  else:
    parsed_info["session_type"] = "決勝"

  # 3. レース名抽出
  rd_match = re.search(
      r"(Rd\.\d+|Round\s*\d+|第\d+戦)[^\n]*", text, re.IGNORECASE
  )
  if rd_match:
    parsed_info["race_name"] = rd_match.group(0).strip()
  else:
    parsed_info["race_name"] = lines[0] if lines else "公式レース"

  # 4. リザルト抽出（超ゆるめパターン）
  for line in lines:
    # 順位(数字) + 車番 + チーム名 + 周回 + タイム のような一般的な並びに対応
    # 例: "1 36 au TOM'S GR Supra 84 Lap 2:10'15.123" や "1 #36 TOMS..."
    parts = line.split()
    if len(parts) >= 2:
      # 行頭が数字（順位または車番）で始まるか判定
      if re.match(r"^\d+$", parts[0]) or parts[0].startswith("#"):
        # タイム表記（::や'や.を含む）や Lap 表記を探す
        time_str = "-"
        lap_str = "-"

        for p in parts:
          if re.search(r"(\d+[:'’]\d+|\+\d+Lap|\d+\.\d+)", p):
            time_str = p
          elif re.match(r"^\d{1,3}$", p) and p != parts[0]:
            lap_str = p

        # チーム名エリア（数値やタイムっぽい要素を除いた残り）
        name_parts = [
            p
            for p in parts
            if not re.search(r"(\d+[:'’]\d+|\+\d+Lap)", p) and p != time_str
        ]
        team_name = " ".join(name_parts)

        if len(team_name) > 1:
          parsed_info["results"].append({
              "team": team_name,
              "laps": lap_str,
              "time": time_str,
          })

  return parsed_info


st.set_page_config(
    page_title="モータースポーツ総合結果 & ランキング", layout="wide"
)
st.title("🏎️ モータースポーツ ダッシュボード")

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 レース結果閲覧・編集",
    "🏆 ポイントランキング",
    "⚙️ チームマスタ管理",
    "💾 バックアップ",
])

# --- サイドバー：結果入力 ---
st.sidebar.header("📝 結果入力")
s_year = st.sidebar.selectbox("シーズン年度", YEARS, key="s_year")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")

team_key = f"{s_cat}_{s_cls}"
if team_key not in data["teams"]:
  data["teams"][team_key] = []

st.sidebar.markdown("---")
st.sidebar.subheader("📥 データの自動取り込み")

import_mode = st.sidebar.radio(
    "取り込み方法を選択", ["PDFファイルから", "テキストコピペから"]
)

parsed_info = {
    "race_name": "",
    "race_date": datetime.date.today(),
    "session_type": "決勝",
    "results": [],
}

if import_mode == "PDFファイルから":
  pdf_file = st.sidebar.file_uploader("公式リザルトPDFを選択", type=["pdf"])
  if pdf_file is not None and HAS_PDF_PARSER:
    pdf_text = extract_text_from_pdf(pdf_file)
    parsed_info = parse_race_text(pdf_text)
    if parsed_info["results"]:
      st.sidebar.success(
          f"✨ PDFから {len(parsed_info['results'])} 件のデータを読み込みました！"
      )
    else:
      st.sidebar.warning(
          "PDFのレイアウトを自動解析できませんでした。テキストコピペ機能をお試しください。"
      )
else:
  raw_paste_text = st.sidebar.text_area(
      "リザルトテキストをそのまま貼り付け",
      height=150,
      placeholder="1 #36 au TOM'S GR Supra 84 2:10'15.123\n2 #37 Deloitte TOM'S ...",
  )
  if raw_paste_text.strip():
    parsed_info = parse_race_text(raw_paste_text)
    if parsed_info["results"]:
      st.sidebar.success(
          f"✨ テキストから {len(parsed_info['results'])} 件のデータを自動抽出しました！"
      )

st.sidebar.markdown("---")

session_type = st.sidebar.radio(
    "セッション種別",
    ["決勝", "予選", "スプリント"],
    index=["決勝", "予選", "スプリント"].index(
        parsed_info["session_type"]
        if parsed_info["session_type"] in ["決勝", "予選", "スプリント"]
        else "決勝"
    ),
)

race_date = st.sidebar.date_input("開催日", value=parsed_info["race_date"])
race_name = st.sidebar.text_input(
    "レース名 / ラウンド",
    value=parsed_info["race_name"],
    placeholder="例: Rd.1 岡山",
)

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

selected_results = []
laps_list = []
times_list = []

res_items = parsed_info["results"]
max_ranks = max(len(res_items), 10)

for rank in range(1, max_ranks + 1):
  def_name = res_items[rank - 1]["team"] if rank <= len(res_items) else ""
  def_lap = res_items[rank - 1]["laps"] if rank <= len(res_items) else "-"
  def_time = res_items[rank - 1]["time"] if rank <= len(res_items) else "-"

  team_input = st.sidebar.text_input(
      f"{rank}位 チーム・車両表記", value=def_name, key=f"r_inp_{rank}"
  )

  if team_input.strip():
    selected_results.append(team_input.strip())
    laps_list.append(def_lap)
    times_list.append(def_time)

if st.sidebar.button("結果を保存する", type="primary"):
  if not race_name:
    st.sidebar.error("レース名を入力してください。")
  elif not selected_results:
    st.sidebar.error("順位データを入力してください。")
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
        "laps": laps_list,
        "times": times_list,
    })
    save_data(data)
    st.sidebar.success(
        f"[{s_year}]「{race_name} ({session_type})」を保存しました！"
    )
    st.rerun()

# --- タブ1: レース結果閲覧・編集 ---
with tab1:
  st.header("🏁 レース結果 閲覧・編集")
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
        res_laps = target.get("laps", ["-"] * len(res_teams))
        res_times = target.get("times", ["-"] * len(res_teams))

        df_res = pd.DataFrame({
            "順位": [f"P{i+1}" for i in range(len(res_teams))],
            "獲得pt": [
                f"{pts_table[i]} pt" if i < len(pts_table) else "0 pt"
                for i in range(len(res_teams))
            ],
            "チーム / 車両表記": res_teams,
            "周回数": res_laps,
            "タイム / 差": res_times,
        })
        st.table(df_res)
    else:
      st.info("該当データがありません。")
  else:
    st.info("データがありません。")

# --- タブ2: ポイントランキング ---
with tab2:
  st.header("🏆 年间ポイントランキング")
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
