import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "race_data_v9.json"

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

# 修正後のSuper GT GT500を含む最新マスタ
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
    "Japan Cup_Pro": [
        "#1 Team 5ZIGEN (Nissan GT-R GT3)",
        "#7 Comet Racing (Ferrari 488 GT3)",
        "#14 MacPherson Racing (Porsche 911 GT3 R)",
        "#98 K-tunes Racing (Lexus RC F GT3)",
    ],
    "Japan Cup_Pro-Am": [
        "#3 Bingo Racing (Ferrari 296 GT3)",
        "#18 TEAM UPGARAGE (Honda NSX GT3)",
        "#36 TEAM GBOX (Porsche 911 GT3 R)",
        "#97 YOGIBO Racing (McLaren 720S GT3)",
    ],
    "Japan Cup_Am": [
        "#5 RM Motorsport (BMW M4 GT3)",
        "#16 ABSSA Motorsport (McLaren 720S GT3)",
        "#22 D'station Racing (Aston Martin Vantage)",
    ],
    "GTWC Asia_Pro": [
        "#4 Craft-Bamboo Racing (Mercedes-AMG)",
        "#13 Phantom Global Racing (Porsche)",
        "#88 Absolute Racing (Porsche/Ferrari)",
        "#99 Triple Eight JMR (Mercedes-AMG)",
    ],
    "GTWC Asia_Pro-Am": [
        "#2 Origine Motorsport (Porsche)",
        "#29 VSR (Lamborghini Huracan)",
        "#63 Vincenzo Sospiri Racing (Lamborghini)",
        "#911 Absolute Racing (Porsche)",
    ],
    "GTWC Asia_Silver": [
        "#5 Climax Racing (Mercedes-AMG)",
        "#11 Harmony Racing (Ferrari 296 GT3)",
        "#89 Team KUSS (Porsche 911 GT3 R)",
    ],
    "GTWC Asia_Am": [
        "#25 AMAC Motorsport (Porsche)",
        "#71 Team EBM (Porsche 911 GT3 R)",
        "#84 Garage 75 (Ferrari 488 GT3)",
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
      return data
  return {"races": {}, "teams": PRESET_TEAMS.copy()}


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

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 レース結果閲覧・編集",
    "🏆 ポイントランキング",
    "⚙️ 車両・チームマスタ管理",
    "💾 データバックアップ / 復元",
])

# --- タブ4: バックアップ・復元 ---
with tab4:
  st.header("💾 データのバックアップと復元")
  st.info("バックアップの保存や復元がここで行えます。")
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

# --- タブ3: チーム・車両の管理 ---
with tab3:
  st.header("⚙️ 参加チーム・車両の管理")
  c1, c2 = st.columns(2)
  with c1:
    m_cat = st.selectbox("カテゴリー", list(CATEGORY_CONFIG.keys()), key="m_cat")
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
    selected_edit_team = st.selectbox("編集・削除するチームを選択", current_teams)
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

# --- サイドバー：レース結果の入力 ---
st.sidebar.header("📝 結果入力")
s_year = st.sidebar.selectbox("シーズン年度", YEARS, key="s_year")
s_cat = st.sidebar.selectbox(
    "カテゴリー", list(CATEGORY_CONFIG.keys()), key="s_cat"
)
s_cls = st.sidebar.selectbox("クラス", CATEGORY_CONFIG[s_cat], key="s_cls")
session_type = st.sidebar.radio("セッション種別", ["決勝", "予選", "スプリント"])

team_key = f"{s_cat}_{s_cls}"
registered_teams = data["teams"].get(team_key, [])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 獲得ポイントの設定")

if session_type == "予選":
  default_pts = DEFAULT_PTS_QUALIFY
elif session_type == "スプリント":
  default_pts = DEFAULT_PTS_SPRINT
else:
  default_pts = DEFAULT_PTS_RACE

custom_pts = []
pts_cols = st.sidebar.columns(2)
for i in range(10):
  col = pts_cols[0] if i < 5 else pts_cols[1]
  val = col.number_input(
      f"{i+1}位 pt",
      min_value=0,
      max_value=100,
      value=default_pts[i] if i < len(default_pts) else 0,
      key=f"pts_setting_{i}",
  )
  custom_pts.append(val)

st.sidebar.markdown("---")

with st.sidebar.form("race_input_form"):
  race_name = st.text_input(
      "レース名 / ラウンド", placeholder="例: Rd.1 岡山"
  )

  st.caption("順位順にチームを選択してください")
  selected_results = []

  if registered_teams:
    for rank in range(1, len(registered_teams) + 1):
      team = st.selectbox(
          f"{rank}位",
          ["(選択なし)"] + registered_teams,
          key=f"rank_{rank}",
      )
      if team != "(選択なし)":
        selected_results.append(team)
  else:
    st.warning("このクラスのチーム一覧はまだ登録されていません。")

  # チームの重複チェック
  duplicates = [
      team
      for team in selected_results
      if selected_results.count(team) > 1
  ]
  has_duplicate = len(duplicates) > 0

  if has_duplicate:
    st.error(
        f"⚠️ 以下の車両が重複選択されています:\n{', '.join(set(duplicates))}"
    )

  submitted = st.form_submit_button(
      "結果を保存する", disabled=has_duplicate
  )

  if submitted:
    if not race_name:
      st.sidebar.error("レース名を入力してください。")
    elif not selected_results:
      st.sidebar.error("少なくとも1つ以上の順位を選択してください。")
    else:
      # 同一レース・同セッションの重複登録チェック
      existing_races = (
          data.get("races", {})
          .get(s_year, {})
          .get(s_cat, {})
          .get(s_cls, [])
      )
      is_already_exist = any(
          r["round_name"] == race_name
          and r.get("session_type", "決勝") == session_type
          for r in existing_races
      )

      if is_already_exist:
        st.sidebar.error(
            f"⚠️ 「{race_name}」の【{session_type}】結果はすでに登録されています！編集する場合は右画面の「閲覧・編集」から行ってください。"
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
            "session_type": session_type,
            "points_table": custom_pts,
            "results": selected_results,
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
      data.get("races", {})
      .get(v_year, {})
      .get(v_cat, {})
      .get(v_cls, [])
  )

  if races_list:
    # ラウンド名（大会名）でユニークにまとめる
    rounds = sorted(
        list(set(r.get("round_name", r.get("race_name")) for r in races_list)),
        reverse=True,
    )
    sel_round = st.selectbox("ラウンド（大会）を選択", rounds)

    # 該当ラウンドのセッション一覧を表示
    round_races = [
        r
        for r in races_list
        if r.get("round_name", r.get("race_name")) == sel_round
    ]

    for target in round_races:
      st.subheader(f"📍 {sel_round} - 【{target.get('session_type', '決勝')}】")
      pts_table = target.get("points_table", DEFAULT_PTS_RACE)

      df_res = pd.DataFrame({
          "順位": [f"P{i+1}" for i in range(len(target["results"]))],
          "獲得ポイント": [
              f"{pts_table[i]} pt" if i < len(pts_table) else "0 pt"
              for i in range(len(target["results"]))
          ],
          "チーム / 車両": target["results"],
      })
      st.dataframe(df_res, use_container_width=True, hide_index=True)

      # 編集・削除アコーディオン
      with st.expander(
          f"⚙️ 「{sel_round} ({target.get('session_type', '決勝')})」の編集・削除"
      ):
        st.write("順位結果の編集:")
        edit_results = []
        team_options = data["teams"].get(f"{v_cat}_{v_cls}", [])
        for idx_r, old_team in enumerate(target["results"]):
          opt = (
              ["(選択なし)"] + team_options
              if old_team in team_options
              else ["(選択なし)", old_team] + team_options
          )
          edit_team = st.selectbox(
              f"{idx_r+1}位",
              opt,
              index=opt.index(old_team) if old_team in opt else 0,
              key=f"edit_{sel_round}_{target.get('session_type')}_{idx_r}",
          )
          if edit_team != "(選択なし)":
            edit_results.append(edit_team)

        e_col1, e_col2 = st.columns(2)
        with e_col1:
          if st.button(
              "変更を保存する",
              key=f"save_btn_{sel_round}_{target.get('session_type')}",
          ):
            target["results"] = edit_results
            save_data(data)
            st.success("結果を更新しました！")
            st.rerun()
        with e_col2:
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
      st.dataframe(df_rank, use_container_width=True, hide_index=True)
    else:
      st.info("集計対象のデータがありません。")
  else:
    st.info(f"{r_year} のランキングデータはありません。")
