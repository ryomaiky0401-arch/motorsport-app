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
    "F2": ["総合"],
    "F3": ["総合"],
    "GTWC Asia": ["Pro", "Pro-Am", "Silver", "Am"],
    "Japan Cup": ["Pro", "Pro-Am", "Silver", "Am"],
}

PRESET_TEAMS = {
    "SUPER GT_GT500": [
        "#8 ARTA MUGEN HRC PRELUDE-GT",
        "#12 TRS IMPUL with SDG Z",
        "#14 ENEOS X PRIME GR Supra",
        "#16 ARTA MUGEN HRC PRELUDE-GT",
        "#17 Astemo HRC PRELUDE-GT",
        "#19 WedsSport BANDOH GR Supra",
        "#23 MOTUL Niterra Z",
        "#24 リアライズコーポレーション Z",
        "#36 au TOM'S GR Supra",
        "#37 Deloitte TOM'S GR Supra",
        "#38 KeePer CERUMO GR Supra",
        "#39 DENSO KOBELCO SARD GR Supra",
        "#64 Modulo HRC PRELUDE-GT",
        "#100 STANLEY HRC PRELUDE-GT",
    ],
    "SUPER GT_GT300": [
        "#2 muta Racing GR86 GT",
        "#4 グッドスマイル 初音ミク AMG",
        "#6 UNI-CONSTRUCTION AMG GT3",
        "#7 BMW M Team Studie x CSL",
        "#9 PACIFIC VSPO NAC AMG",
        "#11 GAINER TANAX Z",
        "#18 UPGARAGE NSX GT3",
        "#20 シェイドレーシング GR86 GT",
        "#22 アールキューズ AMG GT3",
        "#25 HOPPPY Schatz GR Supra",
        "#30 apr GR86 GT",
        "#31 apr LC500h GT",
        "#45 PONOS FERRARI 296 GT3",
        "#48 NILZZ Racing GT-R",
        "#50 ANEST IWATA Racing RC F GT3",
        "#52 埼玉 Green Brave GR Supra GT",
        "#56 リアライズ日産メカニックチャレンジ GT-R",
        "#60 LMcorsa GR Supra GT",
        "#61 SUBARU BRZ R&D SPORT",
        "#65 LEON PYRAMID AMG",
        "#87 JLOC Lamborghini Huracan GT3",
        "#88 JLOC Lamborghini Huracan GT3",
        "#96 K-tunes RC F GT3",
        "#360 RUNUP RIVAUX GT-R",
        "#777 D'station Vantage GT3",
    ],
}

DEFAULT_PTS_RACE = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
DEFAULT_PTS_QUALIFY = [3, 2, 1, 0, 0, 0, 0, 0, 0, 0]
DEFAULT_PTS_SPRINT = [8, 7, 6, 5, 4, 3, 2, 1, 0, 0]

YEARS = ["2026年", "2025年", "2024年", "2023年"]


def load_data():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      if "teams" in data:
        for k, v in PRESET_TEAMS.items():
          if k not in data["teams"] or not data["teams"][k]:
            data["teams"][k] = v
      if "points_master" not in data:
        data["points_master"] = {}
      return data
  return {"races": {}, "teams": PRESET_TEAMS.copy(), "points_master": {}}


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


def parse_race_pdf(text, registered_teams):
  """PDFからメタ情報（日付・レース名・セッション）と順位結果を抽出"""
  parsed_info = {
      "race_name": "",
      "race_date": datetime.date.today(),
      "session_type": "決勝",
      "results": [],
  }

  lines = [line.strip() for line in text.split("\n") if line.strip()]

  # 1. 日付の抽出 (例: 2024/08/25, 2024-08-25, 2024年8月25日)
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

  # 2. セッションの抽出
  if "予選" in text or "Qualifying" in text or "QUALIFY" in text:
    parsed_info["session_type"] = "予選"
  elif "スプリント" in text or "Sprint" in text:
    parsed_info["session_type"] = "スプリント"
  else:
    parsed_info["session_type"] = "決勝"

  # 3. レース名/ラウンドの抽出 (例: Rd.1, Round 1, SUPER GT Rd.5 など)
  rd_match = re.search(
      r"(Rd\.\d+|Round\s*\d+|第\d+戦)[^\n]*", text, re.IGNORECASE
  )
  if rd_match:
    parsed_info["race_name"] = rd_match.group(0).strip()
  else:
    # 該当がなければヘッダー1行目を仮設定
    parsed_info["race_name"] = lines[0] if lines else "公式レース"

  # 4. リザルト・チームの抽出
  for line in lines:
    matched_team = None
    for team in registered_teams:
      num_match = re.search(r"#(\d+)", team)
      if num_match and f"#{num_match.group(1)}" in line:
        matched_team = team
        break
      elif team in line:
        matched_team = team
        break

    if matched_team:
      laps_match = re.search(r"\b(\d{1,3})\s*(Laps|laps|周|Lap)?\b", line)
      time_match = re.search(
          r"(\d+[:'’]\d+[\.'’]\d+|\d+[\.'’]\d+|\+\d+\s*Lap)", line
      )

      laps = laps_match.group(1) if laps_match else "-"
      total_time = time_match.group(1) if time_match else "-"

      parsed_info["results"].append({
          "team": matched_team,
          "laps": laps,
          "time": total_time,
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
    "⚙️ 車両・チーム・ポイントマスタ管理",
    "💾 データバックアップ / 復元",
])

# --- サイドバー：結果入力 ---
st.sidebar.header("📝 結果入力")
s_year = st.sidebar.selectbox("シーズン年度", YEARS, key="s_year")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")

team_key = f"{s_cat}_{s_cls}"
registered_teams = data["teams"].get(team_key, [])

# --- PDF自動解析処理 ---
st.sidebar.markdown("---")
st.sidebar.subheader("📄 PDFから全自動取り込み")
pdf_file = st.sidebar.file_uploader("公式リザルトPDFを選択", type=["pdf"])

auto_race_name = ""
auto_date = datetime.date.today()
auto_session = "決勝"
pdf_results = []

if pdf_file is not None:
  if HAS_PDF_PARSER:
    pdf_text = extract_text_from_pdf(pdf_file)
    parsed_info = parse_race_pdf(pdf_text, registered_teams)

    auto_race_name = parsed_info["race_name"]
    auto_date = parsed_info["race_date"]
    auto_session = parsed_info["session_type"]
    pdf_results = parsed_info["results"]

    if pdf_results:
      st.sidebar.success(
          f"✨ レース名・日付・{len(pdf_results)}台のデータを自動検出しました！"
      )
    else:
      st.sidebar.warning(
          "PDFからチーム名を一致させられませんでした。チーム名登録をご確認ください。"
      )
  else:
    st.sidebar.error("PDF解析ライブラリがありません。(requirements.txtを確認してください)")

st.sidebar.markdown("---")

session_type = st.sidebar.radio(
    "セッション種別",
    ["決勝", "予選", "スプリント"],
    index=["決勝", "予選", "スプリント"].index(
        auto_session if auto_session in ["決勝", "予選", "スプリント"] else "決勝"
    ),
    key="session_type_input",
)

race_date = st.sidebar.date_input("開催日", value=auto_date, key="race_date_input")
race_name = st.sidebar.text_input(
    "レース名 / ラウンド",
    value=auto_race_name,
    placeholder="例: Rd.1 岡山",
    key="race_name_input",
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
        key=f"custom_pts_{i}",
    )
    applied_pts.append(val)

selected_results = []
laps_list = []
times_list = []
available_teams = registered_teams.copy()

if registered_teams:
  for rank in range(1, len(registered_teams) + 1):
    default_team = "(選択なし)"
    default_lap = "-"
    default_time = "-"

    if pdf_results and rank <= len(pdf_results):
      item = pdf_results[rank - 1]
      default_team = item["team"]
      default_lap = item["laps"]
      default_time = item["time"]

    options = ["(選択なし)"] + available_teams
    idx = options.index(default_team) if default_team in options else 0

    team = st.sidebar.selectbox(f"{rank}位", options, index=idx, key=f"rank_s_{rank}")

    if team != "(選択なし)":
      selected_results.append(team)
      laps_list.append(default_lap)
      times_list.append(default_time)
      if team in available_teams:
        available_teams.remove(team)

if st.sidebar.button("結果を保存する", type="primary"):
  if not race_name:
    st.sidebar.error("レース名を入力してください。")
  elif not selected_results:
    st.sidebar.error("順位を選択するかPDFをアップロードしてください。")
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
        f"[{s_year}]「{race_name} ({session_type})」の結果を保存しました！"
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
      sel_round = st.selectbox("ラウンド（大会）を選択", rounds)
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
        r_date_str = target.get("race_date", "日付未設定")
        is_custom = target.get("is_custom_pts", False)
        pts_label = "⚠️ 特別ポイント" if is_custom else "通常ポイント"

        st.subheader(
            f"📍 {sel_round} - 【{target.get('session_type', '決勝')}】"
        )
        st.caption(f"📅 開催日: {r_date_str} ｜ 🎯 適用ルール: {pts_label}")

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
            "チーム / 車両": res_teams,
            "周回数": res_laps,
            "レースタイム / 差": res_times,
        })
        st.table(df_res)

        with st.expander(
            f"⚙️ 「{sel_round} ({target.get('session_type', '決勝')})」の削除"
        ):
          if st.button(
              "🗑️ このセッション結果を削除",
              type="primary",
              key=f"del_btn_{sel_round}_{target.get('session_type')}",
          ):
            races_list.remove(target)
            save_data(data)
            st.warning("データを削除しました。")
            st.rerun()
        st.markdown("---")
    else:
      st.info(f"「{sel_round}」のデータはありません。")
  else:
    st.info(f"{v_year} のレース結果データはまだありません。")

# --- タブ2: ポイントランキング自動計算 ---
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
    races = data["races"][r_year][r_cat][r_cls]

    for r in races:
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
    st.info(f"{r_year} のランキングデータはありません。")

# --- タブ3 & 4 は前述同様 ---
