import datetime
import json
import os
import pandas as pd
import streamlit as st

DATA_FILE = "race_data_v12.json"

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
            if "points_master" not in data:
                data["points_master"] = {}
            return data
    return {"races": {}, "teams": PRESET_TEAMS.copy(), "points_master": {}}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_f1_pdf(uploaded_pdf):
    """FIA F1の決勝・予選・スプリントClassification PDFを抽出する。"""
    import pdfplumber
    import re

    rows = []
    session = "決勝"

    with pdfplumber.open(uploaded_pdf) as pdf:
        full_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if "Qualifying Session Final Classification" in full_text:
            session = "予選"
        elif "Sprint" in full_text and "Classification" in full_text:
            session = "スプリント"

        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                if not table:
                    continue

                is_not_classified = any(
                    row and str(row[0] or "").strip() == "NOT CLASSIFIED"
                    for row in table
                )

                for row in table:
                    cells = [str(x).replace("\n", " ").strip() if x is not None else "" for x in row]

                    if (
                        session == "予選"
                        and len(cells) >= 16
                        and re.fullmatch(r"\d+", cells[0])
                        and re.fullmatch(r"\d+", cells[1])
                    ):
                        rank = int(cells[0])
                        driver = cells[2]
                        team = cells[5]
                        if driver and team:
                            rows.append({
                                "順位": rank, "ドライバー": driver, "チーム": team,
                                "ポイント": 0, "ステータス": "完走",
                            })

                    elif (
                        session != "予選"
                        and not is_not_classified
                        and len(cells) >= 14
                        and re.fullmatch(r"\d+", cells[0])
                        and re.fullmatch(r"\d+", cells[1])
                    ):
                        rank = int(cells[0])
                        driver = cells[2]
                        team = cells[5]
                        pts_text = cells[13].replace(",", ".")
                        try:
                            official_pts = float(pts_text) if pts_text else 0.0
                        except ValueError:
                            official_pts = 0.0
                        if official_pts.is_integer():
                            official_pts = int(official_pts)
                        if 1 <= rank <= 30 and driver and team:
                            rows.append({
                                "順位": rank, "ドライバー": driver, "チーム": team,
                                "ポイント": official_pts, "ステータス": "完走",
                            })

                    elif (
                        session != "予選"
                        and is_not_classified
                        and len(cells) >= 5
                        and re.fullmatch(r"\d+", cells[0])
                    ):
                        # NOT CLASSIFIED表は通常 NO, DRIVER, NAT(空欄), ENTRANT, LAPS, STATUS...
                        driver = cells[1]
                        team = cells[4] if len(cells) > 4 else ""
                        # PDFによってNAT列が省略され、ENTRANTが3列目になる場合にも対応
                        if not team or re.fullmatch(r"\d+", team):
                            team = cells[3] if len(cells) > 3 else ""
                        status_text = " ".join(cells).upper()
                        if "DNS" in status_text:
                            status = "DNS"
                        elif "DSQ" in status_text:
                            status = "DSQ"
                        elif "DNF" in status_text:
                            status = "リタイア"
                        else:
                            status = "リタイア"
                        if driver and team:
                            rows.append({
                                "順位": status,
                                "ドライバー": driver,
                                "チーム": team,
                                "ポイント": 0,
                                "ステータス": status,
                            })

    return rows, session


def extract_f2_pdf(uploaded_pdf):
    """FIA F2の予選・スプリント・フィーチャーレースClassification PDFを抽出する。"""
    import pdfplumber
    import re

    rows = []
    session = "決勝"

    with pdfplumber.open(uploaded_pdf) as pdf:
        full_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if "F2 Qualifying" in full_text or "Qualifying Session Final Classification" in full_text:
            session = "予選"
        elif "Race 1 (Sprint)" in full_text or "Sprint Race Final Classification" in full_text:
            session = "スプリント"
        elif "Race 2 (Feature)" in full_text or "Feature Race Final Classification" in full_text:
            session = "決勝"

        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                if not table:
                    continue

                is_not_classified = any(
                    row and str(row[0] or "").strip() == "NOT CLASSIFIED"
                    for row in table
                )

                for row in table:
                    cells = [str(x).replace("\n", " ").strip() if x is not None else "" for x in row]

                    # F2予選はTEAM列が7列目。ポールポジションの2ptを保存。
                    if (
                        session == "予選"
                        and len(cells) >= 14
                        and re.fullmatch(r"\d+", cells[0])
                        and re.fullmatch(r"\d+", cells[1])
                    ):
                        rank = int(cells[0])
                        driver = cells[2].replace(" *", "").strip()
                        team = cells[6]
                        if driver and team:
                            rows.append({
                                "順位": rank,
                                "ドライバー": driver,
                                "チーム": team,
                                "ポイント": 2 if rank == 1 else 0,
                                "ステータス": "完走",
                            })

                    # F2 Sprint / Featureの分類表はF1決勝と同じ14列構成。
                    elif (
                        session != "予選"
                        and not is_not_classified
                        and len(cells) >= 14
                        and re.fullmatch(r"\d+", cells[0])
                        and re.fullmatch(r"\d+", cells[1])
                    ):
                        rank = int(cells[0])
                        driver = cells[2].replace(" *", "").strip()
                        team = cells[5]
                        pts_text = cells[13].replace(",", ".")
                        try:
                            official_pts = float(pts_text) if pts_text else 0.0
                        except ValueError:
                            official_pts = 0.0
                        if official_pts.is_integer():
                            official_pts = int(official_pts)
                        if driver and team:
                            rows.append({
                                "順位": rank,
                                "ドライバー": driver,
                                "チーム": team,
                                "ポイント": official_pts,
                                "ステータス": "完走",
                            })

                    elif (
                        session != "予選"
                        and is_not_classified
                        and len(cells) >= 5
                        and re.fullmatch(r"\d+", cells[0])
                    ):
                        driver = cells[1].replace(" *", "").strip()
                        team = cells[4]
                        status_text = " ".join(cells).upper()
                        status = "DNS" if "DNS" in status_text else ("DSQ" if "DSQ" in status_text else "リタイア")
                        if driver and team:
                            rows.append({
                                "順位": status,
                                "ドライバー": driver,
                                "チーム": team,
                                "ポイント": 0,
                                "ステータス": status,
                            })

    return rows, session


def extract_f3_pdf(uploaded_pdf):
    """FIA F3の予選・スプリント・フィーチャーレースClassification PDFを抽出する。"""
    import pdfplumber
    import re

    rows = []
    session = "決勝"

    with pdfplumber.open(uploaded_pdf) as pdf:
        full_text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        if "F3 Qualifying" in full_text or "Qualifying Session Final Classification" in full_text:
            session = "予選"
        elif "Race 1 (Sprint)" in full_text or "Sprint Race Final Classification" in full_text:
            session = "スプリント"
        elif "Race 2 (Feature)" in full_text or "Feature Race Final Classification" in full_text:
            session = "決勝"

        # F3の実物PDFはテキスト抽出が安定しているため、表セル位置ではなく行テキストを解析する。
        team_names = [
            "Van Amersfoort Racing", "ART Grand Prix", "Rodin Motorsport",
            "PREMA Racing", "Campos Racing", "DAMS Lucas Oil",
            "MP Motorsport", "AIX Racing", "TRIDENT", "Hitech",
        ]
        lines = [line.strip() for line in full_text.splitlines() if line.strip()]
        not_classified = False

        for line in lines:
            upper = line.upper()
            if upper.startswith("NOT CLASSIFIED"):
                not_classified = True
                continue
            if upper.startswith(("OVERALL FASTEST", "FASTEST LAP", "* PENALTIES", "TIMEKEEPER")):
                if not_classified and not upper.startswith("FASTEST LAP ELIGIBLE"):
                    # NOT CLASSIFIED欄の終了
                    pass
                continue

            team = next((t for t in team_names if t.lower() in line.lower()), None)
            if not team:
                continue

            # 行頭は、分類済みなら「順位 車番」、NOT CLASSIFIEDなら「車番」。
            if not_classified:
                m = re.match(r"^(\d+)\s+(.+?)\s+" + re.escape(team) + r"\b", line, re.I)
                if not m:
                    continue
                car_number = int(m.group(1))
                driver = m.group(2).replace(" *", "").strip()
                status = "DNS" if " DNS" in upper else ("DSQ" if " DSQ" in upper else "リタイア")
                rows.append({
                    "順位": status,
                    "カーナンバー": car_number,
                    "ドライバー": driver,
                    "チーム": team,
                    "ポイント": 0,
                    "ステータス": status,
                })
                continue

            m = re.match(r"^(\d+)\s+(\d+)\s+(.+?)\s+" + re.escape(team) + r"\b(.*)$", line, re.I)
            if not m:
                continue
            rank = int(m.group(1))
            car_number = int(m.group(2))
            driver = m.group(3).replace(" *", "").strip()
            tail = m.group(4).strip()

            official_pts = 0
            if session != "予選":
                # Sprint / Featureは最終列PTS。PTSなしの行は0。
                parts = tail.split()
                if parts and re.fullmatch(r"\d+(?:\.\d+)?", parts[-1]):
                    # 最終値がPTSかどうかは、レース行にタイム/周回情報が十分ある場合のみ判定。
                    # 公式PTSは最大25なので、それを超える値（速度等）は除外。
                    val = float(parts[-1])
                    if val <= 25:
                        official_pts = int(val) if val.is_integer() else val

            rows.append({
                "順位": rank,
                "カーナンバー": car_number,
                "ドライバー": driver,
                "チーム": team,
                "ポイント": official_pts,
                "ステータス": "完走",
            })

    return rows, session

st.set_page_config(
    page_title="モータースポーツ総合結果 & ランキング",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("🏎️ モータースポーツ ダッシュボード")

data = load_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 レース結果閲覧・編集",
    "🏆 ポイントランキング",
    "⚙️ マスタ管理",
    "💾 バックアップ / 復元",
])

# --- タブ4: バックアップ・復元 ---
with tab4:
    st.header("💾 データのバックアップと復元")
    c_bak1, c_bak2 = st.columns([1, 1])
    with c_bak1:
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 データをバックアップ（JSON保存）",
            data=json_str,
            file_name="motorsport_data_backup.json",
            mime="application/json",
            use_container_width=True,
        )
    with c_bak2:
        uploaded_file = st.file_uploader(
            "バックアップファイルを選択", type=["json"]
        )
        if uploaded_file is not None:
            if st.button("ファイルを読み込んでデータを復元する", use_container_width=True):
                loaded_data = json.load(uploaded_file)
                data.update(loaded_data)
                save_data(data)
                st.success("データの復元が完了しました！")
                st.rerun()

# --- タブ3: マスタ管理（チーム & カテゴリー基本ポイント） ---
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
        if st.button("チームを追加", use_container_width=True):
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
                if st.button("名称を更新する", use_container_width=True):
                    idx = current_teams.index(selected_edit_team)
                    current_teams[idx] = updated_name
                    data["teams"][key_name] = current_teams
                    save_data(data)
                    st.success("名称を更新しました！")
                    st.rerun()
            with col_e2:
                if st.button("このチームを削除する", type="primary", use_container_width=True):
                    current_teams.remove(selected_edit_team)
                    data["teams"][key_name] = current_teams
                    save_data(data)
                    st.warning(f"「{selected_edit_team}」を削除しました。")
                    st.rerun()
        else:
            st.info("まだ登録されていません。")

    with m_tab2:
        st.subheader("🎯 カテゴリーごとのデフォルトポイント設定")
        st.caption("ここで設定した配点が、結果入力時に自動的に適用されます。")
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

        st.write(f"**【{p_cat}】の基本ポイント配点（1位〜10位）**")

        p_col1, p_col2, p_col3 = st.columns(3)
        new_race_pts = []
        new_qual_pts = []
        new_sprt_pts = []

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

        if st.button(f"【{p_cat}】の基本ポイント設定を保存", type="primary", use_container_width=True):
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

# 選択したカテゴリーのPDFインポートだけを表示
# --- F1公式PDFインポート ---
if s_cat == "F1":
    with st.sidebar.expander("📥 F1公式PDFを読み込む"):
        st.caption("FIAのRace Classification PDFから完走車とリタイア車を読み取り、そのまま登録・更新できます。")
        f1_pdf = st.file_uploader("F1結果PDF", type=["pdf"], key="f1_pdf_import")
        if f1_pdf is not None:
            try:
                f1_rows, detected_session = extract_f1_pdf(f1_pdf)
                if f1_rows:
                    st.success(f"{len(f1_rows)}台を読み取れました！ セッション: {detected_session}")
                    st.dataframe(pd.DataFrame(f1_rows), use_container_width=True, hide_index=True)

                    f1_year = st.selectbox("登録年度", YEARS, key="f1_import_year")
                    f1_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.3 日本GP", key="f1_import_round")
                    f1_date = st.date_input("開催日", datetime.date.today(), key="f1_import_date")
                    session_options = ["決勝", "予選", "スプリント"]
                    detected_index = session_options.index(detected_session) if detected_session in session_options else 0
                    f1_session = st.selectbox(
                        "セッション",
                        session_options,
                        index=detected_index,
                        key="f1_import_session",
                    )

                    if st.button("このF1結果を登録 / 更新", type="primary", use_container_width=True, key="f1_import_save"):
                        if not f1_round.strip():
                            st.error("レース名 / ラウンドを入力してください。")
                        else:
                            races = data.setdefault("races", {}).setdefault(f1_year, {}).setdefault("F1", {}).setdefault("総合", [])
                            pts = data.get("points_master", {}).get(
                                "F1",
                                {
                                    "決勝": DEFAULT_PTS_RACE,
                                    "予選": DEFAULT_PTS_QUALIFY,
                                    "スプリント": DEFAULT_PTS_SPRINT,
                                },
                            ).get(f1_session, DEFAULT_PTS_RACE)

                            teams = [row["チーム"] for row in f1_rows]
                            drivers = [row["ドライバー"] for row in f1_rows]
                            statuses = [row["ステータス"] for row in f1_rows]
                            official_points = [row.get("ポイント", 0) for row in f1_rows]
                            new_race = {
                                "round_name": f1_round.strip(),
                                "race_date": str(f1_date),
                                "session_type": f1_session,
                                "is_custom_pts": False,
                                "points_table": pts,
                                "results": teams,
                                "drivers": drivers,
                                "car_numbers": car_numbers,
                                "statuses": statuses,
                                "official_points": official_points,
                            }

                            existing_idx = next(
                                (
                                    i for i, x in enumerate(races)
                                    if x.get("round_name") == f1_round.strip()
                                    and x.get("session_type", "決勝") == f1_session
                                ),
                                None,
                            )
                            if existing_idx is None:
                                races.append(new_race)
                                action = "登録"
                            else:
                                races[existing_idx] = new_race
                                action = "更新"

                            team_master = data.setdefault("teams", {}).setdefault("F1_総合", [])
                            for team in teams:
                                if team not in team_master:
                                    team_master.append(team)

                            save_data(data)
                            st.success(f"「{f1_round.strip()} ({f1_session})」を{action}しました！")
                            st.rerun()
                else:
                    st.warning("順位表を読み取れませんでした。このPDFの形式を確認する必要があります。")
            except Exception as e:
                st.error(f"PDFの読み取りに失敗しました: {e}")

# --- F2公式PDFインポート ---
if s_cat == "F2":
    with st.sidebar.expander("📥 F2公式PDFを読み込む"):
        st.caption("FIAのF2予選・Sprint・Feature Classification PDFを読み取り、登録・更新できます。")
        f2_pdf = st.file_uploader("F2結果PDF", type=["pdf"], key="f2_pdf_import")
        if f2_pdf is not None:
            try:
                f2_rows, f2_detected_session = extract_f2_pdf(f2_pdf)
                if f2_rows:
                    st.success(f"{len(f2_rows)}台を読み取れました！ セッション: {f2_detected_session}")
                    st.dataframe(pd.DataFrame(f2_rows), use_container_width=True, hide_index=True)

                    f2_year = st.selectbox("登録年度", YEARS, key="f2_import_year")
                    f2_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.4 マイアミ", key="f2_import_round")
                    f2_date = st.date_input("開催日", datetime.date.today(), key="f2_import_date")
                    f2_session_options = ["決勝", "予選", "スプリント"]
                    f2_detected_index = f2_session_options.index(f2_detected_session)
                    f2_session = st.selectbox(
                        "セッション",
                        f2_session_options,
                        index=f2_detected_index,
                        key="f2_import_session",
                    )

                    if st.button("このF2結果を登録 / 更新", type="primary", use_container_width=True, key="f2_import_save"):
                        if not f2_round.strip():
                            st.error("レース名 / ラウンドを入力してください。")
                        else:
                            races = data.setdefault("races", {}).setdefault(f2_year, {}).setdefault("F2", {}).setdefault("総合", [])
                            pts = data.get("points_master", {}).get("F2", {}).get(
                                f2_session,
                                DEFAULT_PTS_RACE if f2_session == "決勝" else (
                                    DEFAULT_PTS_SPRINT if f2_session == "スプリント" else DEFAULT_PTS_QUALIFY
                                ),
                            )
                            teams = [r["チーム"] for r in f2_rows]
                            drivers = [r["ドライバー"] for r in f2_rows]
                            statuses = [r["ステータス"] for r in f2_rows]
                            official_points = [r["ポイント"] for r in f2_rows]
                            new_race = {
                                "round_name": f2_round.strip(),
                                "race_date": str(f2_date),
                                "session_type": f2_session,
                                "is_custom_pts": False,
                                "points_table": pts,
                                "results": teams,
                                "drivers": drivers,
                                "statuses": statuses,
                                "official_points": official_points,
                            }
                            existing_idx = next(
                                (
                                    i for i, race in enumerate(races)
                                    if race.get("round_name") == f2_round.strip()
                                    and race.get("session_type", "決勝") == f2_session
                                ),
                                None,
                            )
                            if existing_idx is None:
                                races.append(new_race)
                                action = "登録"
                            else:
                                races[existing_idx] = new_race
                                action = "更新"

                            team_master = data.setdefault("teams", {}).setdefault("F2_総合", [])
                            for team in teams:
                                if team not in team_master:
                                    team_master.append(team)

                            save_data(data)
                            st.success(f"「{f2_round.strip()} ({f2_session})」を{action}しました！")
                            st.rerun()
                else:
                    st.warning("順位表を読み取れませんでした。このPDFの形式を確認する必要があります。")
            except Exception as e:
                st.error(f"PDFの読み取りに失敗しました: {e}")


if s_cat == "F3":
    with st.sidebar.expander("📥 F3公式PDFを読み込む"):
        if st.session_state.get("f3_import_success"):
            st.success(st.session_state.pop("f3_import_success"))
        st.caption("FIAのF3予選・Sprint・Feature Classification PDFを読み取り、登録・更新できます。")
        f3_pdf = st.file_uploader("F3結果PDF", type=["pdf"], key="f3_pdf_import")
        if f3_pdf is not None:
            try:
                f3_rows, f3_detected_session = extract_f3_pdf(f3_pdf)
                if f3_rows:
                    st.success(f"{len(f3_rows)}台を読み取れました！ セッション: {f3_detected_session}")
                    st.dataframe(pd.DataFrame(f3_rows), use_container_width=True, hide_index=True)

                    f3_year = st.selectbox("登録年度", YEARS, key="f3_import_year")
                    f3_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.4 マイアミ", key="f3_import_round")
                    f3_date = st.date_input("開催日", datetime.date.today(), key="f3_import_date")
                    f3_session_options = ["決勝", "予選", "スプリント"]
                    f3_detected_index = f3_session_options.index(f3_detected_session)
                    f3_session = st.selectbox(
                        "セッション",
                        f3_session_options,
                        index=f3_detected_index,
                        key="f3_import_session",
                    )

                    if st.button("このF3結果を登録 / 更新", type="primary", use_container_width=True, key="f3_import_save"):
                        if not f3_round.strip():
                            st.error("レース名 / ラウンドを入力してください。")
                        else:
                            races = data.setdefault("races", {}).setdefault(f3_year, {}).setdefault("F3", {}).setdefault("総合", [])
                            pts = data.get("points_master", {}).get("F3", {}).get(
                                f3_session,
                                DEFAULT_PTS_RACE if f3_session == "決勝" else (
                                    DEFAULT_PTS_SPRINT if f3_session == "スプリント" else DEFAULT_PTS_QUALIFY
                                ),
                            )
                            teams = [r["チーム"] for r in f3_rows]
                            drivers = [r["ドライバー"] for r in f3_rows]
                            car_numbers = [r.get("カーナンバー") for r in f3_rows]
                            statuses = [r["ステータス"] for r in f3_rows]
                            official_points = [r["ポイント"] for r in f3_rows]
                            new_race = {
                                "round_name": f3_round.strip(),
                                "race_date": str(f3_date),
                                "session_type": f3_session,
                                "is_custom_pts": False,
                                "points_table": pts,
                                "results": teams,
                                "drivers": drivers,
                                "statuses": statuses,
                                "official_points": official_points,
                            }
                            existing_idx = next(
                                (
                                    i for i, race in enumerate(races)
                                    if race.get("round_name") == f3_round.strip()
                                    and race.get("session_type", "決勝") == f3_session
                                ),
                                None,
                            )
                            if existing_idx is None:
                                races.append(new_race)
                                action = "登録"
                            else:
                                races[existing_idx] = new_race
                                action = "更新"

                            team_master = data.setdefault("teams", {}).setdefault("F3_総合", [])
                            for team in teams:
                                if team not in team_master:
                                    team_master.append(team)

                            save_data(data)
                            st.session_state["f3_import_success"] = f"✅ 「{f3_round.strip()} ({f3_session})」を{action}しました！"
                            st.rerun()
                else:
                    st.warning("順位表を読み取れませんでした。このPDFの形式を確認する必要があります。")
            except Exception as e:
                st.error(f"PDFの読み取りに失敗しました: {e}")



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

base_pts = data["points_master"].get(
    s_cat,
    {
        "決勝": DEFAULT_PTS_RACE,
        "予選": DEFAULT_PTS_QUALIFY,
        "スプリント": DEFAULT_PTS_SPRINT,
    },
).get(session_type, DEFAULT_PTS_RACE)

st.sidebar.markdown("---")
use_custom_pts = st.sidebar.checkbox(
    "⚠️ このレース専用のポイントを使う (WEC 24h等)", value=False
)
applied_pts = base_pts.copy()

if use_custom_pts:
    st.sidebar.caption("このレース限定の獲得ポイントを直接設定")
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
else:
    st.sidebar.info(
        f"配点: {base_pts[:5]}... (マスタの「{s_cat}」基本ポイントを自動適用)"
    )

st.sidebar.markdown("---")
team_key = f"{s_cat}_{s_cls}"
registered_teams = data["teams"].get(team_key, [])

st.sidebar.caption("順位順にチームを選択してください")
selected_results = []
available_teams = registered_teams.copy()

if registered_teams:
    for rank in range(1, len(registered_teams) + 1):
        options = ["(選択なし)"] + available_teams
        team = st.sidebar.selectbox(f"{rank}位", options, key=f"rank_select_{rank}")
        if team != "(選択なし)":
            selected_results.append(team)
            if team in available_teams:
                available_teams.remove(team)
else:
    st.sidebar.warning("このクラスのチーム一覧はまだ登録されていません。")

if st.sidebar.button("結果を保存する", type="primary", use_container_width=True):
    if not race_name:
        st.sidebar.error("レース名を入力してください。")
    elif not selected_results:
        st.sidebar.error("少なくとも1つ以上の順位を選択してください。")
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
            })
            save_data(data)
            st.sidebar.success(
                f"[{s_year}]「{race_name} ({session_type})」の結果を保存しました！"
            )
            st.rerun()

# --- タブ1: レース結果閲覧・編集・削除 ---
with tab1:
    st.header("🏁 レース結果 閲覧・編集")

    v_y, v_c1, v_c2 = st.columns([1, 1, 1])
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
            # 閲覧画面は見やすさ優先で「決勝 → スプリント → 予選」の順に表示
            view_session_order = {"決勝": 0, "スプリント": 1, "予選": 2}
            round_races = sorted(
                round_races,
                key=lambda x: view_session_order.get(x.get("session_type", "決勝"), 99),
            )
            for target in round_races:
                r_date_str = target.get("race_date", "日付未設定")
                is_custom = target.get("is_custom_pts", False)
                pts_label = "⚠️ 特別ポイント" if is_custom else "通常ポイント"

                st.subheader(
                    f"📍 {sel_round} - 【{target.get('session_type', '決勝')}】"
                )
                st.caption(f"📅 開催日: {r_date_str} ｜ 🎯 適用ルール: {pts_label}")

                pts_table = target.get("points_table", DEFAULT_PTS_RACE)

                statuses = target.get("statuses", ["完走"] * len(target["results"]))
                drivers = target.get("drivers", [])
                df_data = {
                    "順位": [
                        statuses[i] if i < len(statuses) and statuses[i] in ["リタイア", "DNS", "DSQ"] else f"P{i+1}"
                        for i in range(len(target["results"]))
                    ],
                    "獲得ポイント": [
                        f"{target.get('official_points', [])[i]} pt"
                        if i < len(target.get("official_points", []))
                        else (
                            "0 pt"
                            if i < len(statuses) and statuses[i] in ["リタイア", "DNS", "DSQ"]
                            else (f"{pts_table[i]} pt" if i < len(pts_table) else "0 pt")
                        )
                        for i in range(len(target["results"]))
                    ],
                }
                if drivers:
                    df_data["ドライバー"] = drivers
                df_data["チーム / 車両"] = target["results"]
                df_res = pd.DataFrame(df_data)

                # スクロールせずに全体を表示するため height を自動調整
                calc_height = (len(df_res) + 1) * 35 + 3
                st.dataframe(df_res, use_container_width=True, height=calc_height)

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
                            use_container_width=True,
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
                            use_container_width=True,
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

# --- タブ2: ポイントランキング・推移グラフ ---
with tab2:
    st.header("🏆 年間ポイントランキング & 累計推移")
    r_y, r_c1, r_c2 = st.columns([1, 1, 1])
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
        and data["races"][r_year][r_cat][r_cls]
    ):
        races = data["races"][r_year][r_cat][r_cls]

        # 日付 → 同一イベント内は「予選 → スプリント → 決勝」の順に固定。
        # PDFを読み込んだ順番には左右されない。
        session_order = {"予選": 0, "スプリント": 1, "決勝": 2}
        races = sorted(
            races,
            key=lambda x: (
                session_order.get(x.get("session_type", "決勝"), 99),
                x.get("race_date", ""),
                x.get("round_name", ""),
            ),
        )

        registered = data["teams"].get(f"{r_cat}_{r_cls}", [])
        race_headers = [f"{r.get('round_name')} ({r.get('session_type', '決勝')})" for r in races]

        team_points_matrix = {}
        # F1のPDF登録データがある場合は、実際に出場したチームだけをランキング対象にする。
        # これで旧名称や過去シーズンのマスター登録チームが0ptで混ざらない。
        has_pdf_driver_data = any(r.get("drivers") for r in races)
        if not (r_cat in ["F1", "F2"] and has_pdf_driver_data):
            for team in registered:
                team_points_matrix[team] = [0] * len(races)

        for race_idx, r in enumerate(races):
            pts_table = r.get("points_table", DEFAULT_PTS_RACE)
            statuses = r.get("statuses", [])
            for rank_idx, team in enumerate(r["results"]):
                is_retired = rank_idx < len(statuses) and statuses[rank_idx] in ["リタイア", "DNS", "DSQ"]
                official = r.get("official_points", [])
                pt = (
                    official[rank_idx]
                    if rank_idx < len(official)
                    else (0 if is_retired else (pts_table[rank_idx] if rank_idx < len(pts_table) else 0))
                )
                if team not in team_points_matrix:
                    team_points_matrix[team] = [0] * len(races)
                # 同一チームの2台分を合算する
                team_points_matrix[team][race_idx] += pt

        summary_list = []
        for team, pts_list in team_points_matrix.items():
            total_pt = sum(pts_list)
            summary_list.append({"チーム / 車両": team, "合計ポイント": total_pt, "pts_list": pts_list})

        summary_list.sort(key=lambda x: x["合計ポイント"], reverse=True)

        df_rank = pd.DataFrame([
            {
                "順位": f"P{i+1}",
                "チーム / 車両": item["チーム / 車両"],
                "合計ポイント": item["合計ポイント"],
            }
            for i, item in enumerate(summary_list)
        ])

        # PDFインポートで保存されたドライバー情報から年間ランキングを集計
        driver_points = {}
        has_driver_data = False
        for race_idx, race in enumerate(races):
            drivers = race.get("drivers", [])
            if drivers:
                has_driver_data = True
            pts_table = race.get("points_table", DEFAULT_PTS_RACE)
            statuses = race.get("statuses", [])
            for rank_idx, driver in enumerate(drivers):
                if not driver:
                    continue
                is_retired = rank_idx < len(statuses) and statuses[rank_idx] == "リタイア"
                official = race.get("official_points", [])
                pt = (
                    official[rank_idx]
                    if rank_idx < len(official)
                    else (0 if is_retired else (pts_table[rank_idx] if rank_idx < len(pts_table) else 0))
                )
                if driver not in driver_points:
                    driver_points[driver] = [0] * len(races)
                driver_points[driver][race_idx] = pt

        ranking_tab_team, ranking_tab_driver = st.tabs(
            ["🏎️ チーム / 車両", "👤 ドライバー"]
        )

        with ranking_tab_team:
            st.subheader("🥇 ポイントランキング")
        
            # スクロールせずに全体を表示するため height を自動調整
            calc_rank_height = (len(df_rank) + 1) * 35 + 3
            st.dataframe(df_rank, use_container_width=True, height=calc_rank_height)

            csv_rank = df_rank.to_csv(index=False).encode("utf-8_sig")
            st.download_button(
                label="📥 ランキング（CSV）をダウンロード",
                data=csv_rank,
                file_name=f"{r_year}_{r_cat}_{r_cls}_ranking.csv",
                mime="text/csv",
                use_container_width=True,
            )

            st.markdown("---")

            # 大会ごとの獲得ポイント合計を、従来と同じ折れ線グラフで表示
            st.subheader("📈 大会別 獲得ポイント")

            event_order = []
            for race in races:
                event_name = race.get("round_name", race.get("race_name", "大会名未設定"))
                if event_name not in event_order:
                    event_order.append(event_name)

            event_points = {}
            for item in summary_list:
                totals = {event: 0 for event in event_order}
                for race_idx, race in enumerate(races):
                    event_name = race.get("round_name", race.get("race_name", "大会名未設定"))
                    if race_idx < len(item["pts_list"]):
                        try:
                            totals[event_name] += max(float(item["pts_list"][race_idx]), 0)
                        except (TypeError, ValueError):
                            pass
                event_points[item["チーム / 車両"]] = [totals[event] for event in event_order]

            st.line_chart(pd.DataFrame(event_points, index=event_order))


        with ranking_tab_driver:
            if not has_driver_data:
                st.info("ドライバーデータがまだありません。PDFから登録したレース結果で表示されます。")
            else:
                driver_summary = []
                for driver, pts_list in driver_points.items():
                    driver_summary.append({
                        "ドライバー": driver,
                        "合計ポイント": sum(pts_list),
                        "pts_list": pts_list,
                    })
                driver_summary.sort(key=lambda x: x["合計ポイント"], reverse=True)

                df_driver_rank = pd.DataFrame([
                    {
                        "順位": f"P{i+1}",
                        "ドライバー": item["ドライバー"],
                        "合計ポイント": item["合計ポイント"],
                    }
                    for i, item in enumerate(driver_summary)
                ])

                st.subheader("👤 ドライバーランキング")
                driver_height = (len(df_driver_rank) + 1) * 35 + 3
                st.dataframe(
                    df_driver_rank,
                    use_container_width=True,
                    height=driver_height,
                    hide_index=True,
                )

                driver_csv = df_driver_rank.to_csv(index=False).encode("utf-8_sig")
                st.download_button(
                    label="📥 ドライバーランキング（CSV）をダウンロード",
                    data=driver_csv,
                    file_name=f"{r_year}_{r_cat}_{r_cls}_driver_ranking.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

                st.markdown("---")
                st.subheader("📈 ドライバー 大会別獲得ポイント")
                driver_event_points = {}
                for item in driver_summary:
                    totals = {event: 0 for event in event_order}
                    for race_idx, race in enumerate(races):
                        event_name = race.get("round_name", race.get("race_name", "大会名未設定"))
                        if race_idx < len(item["pts_list"]):
                            try:
                                totals[event_name] += max(float(item["pts_list"][race_idx]), 0)
                            except (TypeError, ValueError):
                                pass
                    driver_event_points[item["ドライバー"]] = [totals[event] for event in event_order]

                st.line_chart(pd.DataFrame(driver_event_points, index=event_order))

    else:
        st.info(f"{r_year} {r_cat} ({r_cls}) の集計対象データがまだありません。")
