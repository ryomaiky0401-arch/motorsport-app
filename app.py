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
    "F1_総合": [
        "Oracle Red Bull Racing",
        "Mercedes-AMG PETRONAS F1 Team",
        "Scuderia Ferrari HP",
        "McLaren Formula 1 Team",
        "Aston Martin Aramco F1 Team",
        "BWT Alpine F1 Team",
        "Williams Racing",
        "Visa Cash App RB F1 Team",
        "MoneyGram Haas F1 Team",
        "Stake F1 Team Kick Sauber",
        "Cadillac Formula 1 Team",
    ],
    "F2_総合": [
        "ART Grand Prix",
        "PREMA Racing",
        "Rodin Motorsport",
        "DAMS Lucas Oil",
        "Invicta Racing",
        "MP Motorsport",
        "Van Amersfoort Racing",
        "Hitech Pulse-Eight",
        "Campos Racing",
        "Trident",
        "PHM AIX Racing",
    ],
    "F3_総合": [
        "PREMA Racing",
        "Trident",
        "ART Grand Prix",
        "Campos Racing",
        "Hitech Pulse-Eight",
        "MP Motorsport",
        "Van Amersfoort Racing",
        "Rodin Motorsport",
        "AIX Racing",
        "Jenzer Motorsport",
    ],
    "WEC_Hypercar": [
        "#2 Cadillac Racing",
        "#5 Porsche Penske Motorsport",
        "#6 Porsche Penske Motorsport",
        "#7 TOYOTA GAZOO Racing",
        "#8 TOYOTA GAZOO Racing",
        "#11 Isotta Fraschini",
        "#12 Hertz Team JOTA",
        "#15 BMW M Team WRT",
        "#20 BMW M Team WRT",
        "#35 Alpine Endurance Team",
        "#36 Alpine Endurance Team",
        "#38 Hertz Team JOTA",
        "#50 Ferrari AF Corse",
        "#51 Ferrari AF Corse",
        "#63 Lamborghini Iron Lynx",
        "#83 AF Corse (Ferrari)",
        "#93 Peugeot TotalEnergies",
        "#94 Peugeot TotalEnergies",
        "#99 Proton Competition",
    ],
    "WEC_LMGT3": [
        "#27 Heart of Racing Team (Aston Martin)",
        "#31 Team WRT (BMW)",
        "#46 Team WRT (BMW)",
        "#54 Vista AF Corse (Ferrari)",
        "#55 Vista AF Corse (Ferrari)",
        "#59 United Autosports (McLaren)",
        "#77 Proton Competition (Ford)",
        "#78 Akkodis ASP Team (Lexus)",
        "#81 TF Sport (Corvette)",
        "#82 TF Sport (Corvette)",
        "#85 Iron Dames (Lamborghini)",
        "#87 Akkodis ASP Team (Lexus)",
        "#88 Proton Competition (Ford)",
        "#91 Manthey EMA (Porsche)",
        "#92 Manthey PureRxcing (Porsche)",
        "#95 United Autosports (McLaren)",
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
  """PDFからテキストを抽出する"""
  text = ""
  try:
    if "pdfplumber" in globals():
      with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
          text += page.extract_text() or ""
    elif "pypdf" in globals():
      reader = pypdf.PdfReader(pdf_file)
      for page in reader.pages:
        text += page.extract_text() or ""
  except Exception as e:
    st.error(f"PDF解析エラー: {e}")
  return text


def parse_race_pdf(text, registered_teams):
  """PDFテキストから順位・チーム・周回数・タイムを自動抽出する汎用パーサー"""
  parsed_results = []
  lines = text.split("\n")

  for line in lines:
    line_clean = line.strip()
    if not line_clean:
      continue

    # 登録済みチーム名が含まれているか検索
    matched_team = None
    for team in registered_teams:
      # ゼッケン番号やチーム名の一部でマッチング
      num_match = re.search(r"#(\d+)", team)
      if num_match and f"#{num_match.group(1)}" in line_clean:
        matched_team = team
        break
      elif team in line_clean:
        matched_team = team
        break

    if matched_team:
      # 周回数（数字2〜3桁）と タイム（1:23'45.678 や 23:45.678 など）を正規表現で探す
      laps_match = re.search(r"\b(\d{1,3})\s*(Laps|laps|周|Lap)?\b", line_clean)
      time_match = re.search(
          r"(\d+[:'’]\d+[\.'’]\d+|\d+[\.'’]\d+|\+\d+\s*Lap)", line_clean
      )

      laps = laps_match.group(1) if laps_match else "-"
      total_time = time_match.group(1) if time_match else "-"

      parsed_results.append({
          "team": matched_team,
          "laps": laps,
          "time": total_time,
      })

  return parsed_results


st.set_page_config(
    page_title="モータースポーツ総合結果 & ランキング",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.title("🏎️ モータースポーツ ダッシュボード")

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 レース結果閲覧・編集",
    "🏆 ポイントランキング",
    "⚙️ 車両・チーム・ポイントマスタ管理",
    "💾 データバックアップ / 復元",
])

# --- タブ4: バックアップ・復元 ---
with tab4:
  st.header("💾 データのバックアップと復元")
  c_bak1, c_bak2 = st.columns(2)
  with c_bak1:
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 データをバックアップ（JSON保存）",
        data=json_str,
        file_name="motorsport_data_backup.json",
        mime="application/json",
    )
  with c_bak2:
    uploaded_file = st.file_uploader(
        "バックアップファイルを選択", type=["json"]
    )
    if uploaded_file is not None:
      if st.button("ファイルを読み込んでデータを復元する"):
        loaded_data = json.load(uploaded_file)
        data.update(loaded_data)
        save_data(data)
        st.success("データの復元が完了しました！")
        st.rerun()

# --- タブ3: マスタ管理 ---
with tab3:
  st.header("⚙️ マスタ管理")

  m_tab1, m_tab2 = st.tabs(
      ["🏎️ 参加チーム・車両の管理", "🎯 シリーズ基本ポイント設定"]
  )

  with m_tab1:
    c1, c2 = st.columns(2)
    with c1:
      m_cat = st.selectbox(
          "カテゴリー", list(CATEGORY_CONFIG.keys()), key="m_cat"
      )
    with c2:
      m_cls = st.selectbox("クラス", CATEGORY_CONFIG[m_cat], key="m_cls")

    key_name = f"{m_cat}_{m_cls}"
    current_teams = data["teams"].get(key_name, [])

    st.subheader("➕ チーム・車両の新規追加")
    new_team = st.text_input("チーム名 / 車両名")
    if st.button("チームを追加"):
      if new_team and new_team not in current_teams:
        current_teams.append(new_team)
        data["teams"][key_name] = current_teams
        save_data(data)
        st.success(f"「{new_team}」を追加しました！")
        st.rerun()

    st.divider()
    st.subheader("✏️ 登録済みチームの編集・削除")
    if current_teams:
      selected_edit_team = st.selectbox(
          "編集・削除するチームを選択", current_teams
      )
      col_e1, col_e2 = st.columns(2)
      with col_e1:
        updated_name = st.text_input(
            "修正後の名称", value=selected_edit_team, key="edit_input"
        )
        if st.button("名称を更新する"):
          idx = current_teams.index(selected_edit_team)
          current_teams[idx] = updated_name
          data["teams"][key_name] = current_teams
          save_data(data)
          st.success("名称を更新しました！")
          st.rerun()
      with col_e2:
        if st.button("このチームを削除する", type="primary"):
          current_teams.remove(selected_edit_team)
          data["teams"][key_name] = current_teams
          save_data(data)
          st.warning(f"「{selected_edit_team}」を削除しました。")
          st.rerun()
    else:
      st.info("まだ登録されていません。")

  with m_tab2:
    st.subheader("🎯 カテゴリーごとのデフォルトポイント設定")
    p_cat = st.selectbox(
        "対象カテゴリー選択", list(CATEGORY_CONFIG.keys()), key="p_cat"
    )

    cat_pts = data["points_master"].get(
        p_cat,
        {
            "決勝": DEFAULT_PTS_RACE,
            "予選": DEFAULT_PTS_QUALIFY,
            "スプリント": DEFAULT_PTS_SPRINT,
        },
    )

    p_col1, p_col2, p_col3 = st.columns(3)
    new_race_pts, new_qual_pts, new_sprt_pts = [], [], []

    with p_col1:
      st.markdown("**🏁 決勝ポイント**")
      for i in range(10):
        val = st.number_input(
            f"{i+1}位",
            min_value=0,
            value=cat_pts["決勝"][i] if i < len(cat_pts["決勝"]) else 0,
            key=f"m_pts_race_{p_cat}_{i}",
        )
        new_race_pts.append(val)

    with p_col2:
      st.markdown("**⏱️ 予選ポイント**")
      for i in range(10):
        val = st.number_input(
            f"{i+1}位",
            min_value=0,
            value=cat_pts["予選"][i] if i < len(cat_pts["予選"]) else 0,
            key=f"m_pts_qual_{p_cat}_{i}",
        )
        new_qual_pts.append(val)

    with p_col3:
      st.markdown("**⚡ スプリントポイント**")
      for i in range(10):
        val = st.number_input(
            f"{i+1}位",
            min_value=0,
            value=(
                cat_pts["スプリント"][i] if i < len(cat_pts["スプリント"]) else 0
            ),
            key=f"m_pts_sprt_{p_cat}_{i}",
        )
        new_sprt_pts.append(val)

    if st.button(f"【{p_cat}】の基本ポイント設定を保存", type="primary"):
      data["points_master"][p_cat] = {
          "決勝": new_race_pts,
          "予選": new_qual_pts,
          "スプリント": new_sprt_pts,
      }
      save_data(data)
      st.success(f"{p_cat} の基本ポイント配点を保存しました！")

# --- サイドバー：レース結果の入力 ---
st.sidebar.header("📝 結果入力")
s_year = st.sidebar.selectbox("シーズン年度", YEARS, key="s_year")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")
session_type = st.sidebar.radio(
    "セッション種別", ["決勝", "予選", "スプリント"], key="session_type_input"
)

race_date = st.sidebar.date_input(
    "開催日", datetime.date.today(), key="race_date_input"
)
race_name = st.sidebar.text_input(
    "レース名 / ラウンド", placeholder="例: Rd.1 岡山", key="race_name_input"
)

team_key = f"{s_cat}_{s_cls}"
registered_teams = data["teams"].get(team_key, [])

# --- PDF読み込み機能 ---
st.sidebar.markdown("---")
st.sidebar.subheader("📄 PDFから全自動取り込み")
pdf_file = st.sidebar.file_uploader("公式リザルトPDFを選択", type=["pdf"])

pdf_parsed_data = []
if pdf_file is not None:
  if HAS_PDF_PARSER:
    pdf_text = extract_text_from_pdf(pdf_file)
    pdf_parsed_data = parse_race_pdf(pdf_text, registered_teams)
    if pdf_parsed_data:
      st.sidebar.success(
          f"✨ PDFから {len(pdf_parsed_data)} 台のデータを解析しました！"
      )
    else:
      st.sidebar.warning(
          "PDFからチーム名を抽出できませんでした。手動選択を行ってください。"
      )
  else:
    st.sidebar.error(
        "PDF解析ライブラリがインストールされていません。(pdfplumberまたはpypdfが必要)"
    )

st.sidebar.markdown("---")

# ポイント取得
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

st.sidebar.markdown("---")
st.sidebar.caption("順位順にチームを選択（PDF読み込み時は自動入力）")

selected_results = []
laps_list = []
times_list = []
available_teams = registered_teams.copy()

# PDF解析データがある場合はデフォルト値にセット
if registered_teams:
  for rank in range(1, len(registered_teams) + 1):
    default_team = "(選択なし)"
    default_lap = "-"
    default_time = "-"

    if pdf_parsed_data and rank <= len(pdf_parsed_data):
      item = pdf_parsed_data[rank - 1]
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
    existing_races = (
        data.get("races", {}).get(s_year, {}).get(s_cat, {}).get(s_cls, [])
    )
    is_already_exist = any(
        r.get("round_name") == race_name
        and r.get("session_type", "決勝") == session_type
        for r in existing_races
    )

    if is_already_exist:
      st.sidebar.error(
          f"⚠️ 「{race_name}」の【{session_type}】結果はすでに登録されています！"
      )
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

# --- タブ1: レース結果閲覧・編集・削除 ---
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
      st.info(f"「{sel_round}」の【{sel_session_filter}】データはありません。")
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
