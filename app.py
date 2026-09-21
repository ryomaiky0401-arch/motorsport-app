import requests
import urllib.parse
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


def extract_supergt_result_url(url):
    """SUPER GT公式リザルトページ（GT500/GT300、予選Q1/Q2/決勝）を解析する。"""
    import re
    import requests
    from html.parser import HTMLParser
    from urllib.parse import urlparse, parse_qs

    class TableParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.tables, self.table, self.row, self.cell = [], None, None, None
        def handle_starttag(self, tag, attrs):
            if tag == "table":
                self.table = []
            elif tag == "tr" and self.table is not None:
                self.row = []
            elif tag in ("td", "th") and self.row is not None:
                self.cell = ""
        def handle_data(self, data):
            if self.cell is not None:
                self.cell += data
        def handle_endtag(self, tag):
            if tag in ("td", "th") and self.cell is not None:
                self.row.append(re.sub(r"\s+", " ", self.cell).strip())
                self.cell = None
            elif tag == "tr" and self.row is not None:
                if self.row:
                    self.table.append(self.row)
                self.row = None
            elif tag == "table" and self.table is not None:
                self.tables.append(self.table)
                self.table = None

    url = url.strip()
    parsed = urlparse(url)
    if parsed.netloc.lower() not in ["supergt.net", "www.supergt.net"] or parsed.path.rstrip("/") != "/result":
        raise ValueError("SUPER GT公式サイトの「順位 / リザルト」URLを入力してください。")
    qs = parse_qs(parsed.query)
    cls_raw = qs.get("gt_class", [""])[0].lower()
    cls = "GT500" if cls_raw == "gt500" else "GT300" if cls_raw == "gt300" else None
    race_num = qs.get("race_num", [""])[0]
    if not cls:
        raise ValueError("URLからGT500 / GT300を判定できませんでした。")
    if race_num == "2":
        session = "予選Q1"
    elif race_num == "3":
        session = "予選Q2"
    elif race_num == "4":
        session = "決勝"
    else:
        raise ValueError("公式予選Q1・Q2または決勝レースのURLを使用してください。")

    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    parser = TableParser()
    parser.feed(response.text)

    table = None
    header = None
    for t in parser.tables:
        for row in t[:4]:
            joined = " ".join(row)
            if ("順位" in joined or "Pos" in joined) and ("No." in joined or "No" in row) and ("ドライバー" in joined or "Driver" in joined):
                table, header = t, row
                break
        if table:
            break
    if not table:
        raise ValueError("SUPER GT公式ページの結果表を見つけられませんでした。")

    h = [re.sub(r"\s+", "", x).lower() for x in header]
    def find_col(keys):
        for i, x in enumerate(h):
            if any(k in x for k in keys):
                return i
        return None

    pos_i = find_col(["順位", "pos"])
    no_i = find_col(["no.", "no", "車番"])
    team_i = find_col(["チーム/マシン", "チーム", "team"])
    driver_i = find_col(["ドライバー", "driver"])
    lap_i = find_col(["ラップ", "lap"])
    if None in (pos_i, no_i, team_i, driver_i):
        raise ValueError("結果表の順位・車番・チーム・ドライバー列を判定できませんでした。")

    race_pts = {
        "GT500": [20, 15, 11, 8, 6, 5, 4, 3, 2, 1],
        "GT300": [25, 20, 16, 13, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    }
    rows = []
    header_idx = table.index(header)
    for raw in table[header_idx + 1:]:
        if max(pos_i, no_i, team_i, driver_i) >= len(raw):
            continue
        pm = re.search(r"\d+", raw[pos_i])
        num = raw[no_i].strip()
        if not pm or not num:
            continue
        rank = int(pm.group())
        group = ""
        if cls == "GT300" and session == "予選Q1":
            pos_text = raw[pos_i].strip().upper()
            gm = re.search(r"([AB])\s*[-－]?\s*\d+", pos_text)
            if gm:
                group = gm.group(1) + "組"
        team_machine = raw[team_i].strip()
        # 公式セルは「チーム ... マシン ...」を含む。ランキング用にはチーム名だけを保存。
        tm = re.search(r"チーム\s*(.*?)\s*マシン\s*", team_machine)
        team = tm.group(1).strip() if tm else team_machine
        drivers = raw[driver_i].strip()
        # SUPER GT公式HTMLは複数ドライバーを1セル内に空白だけで並べる。
        # 2026エントリーの車番ごとの人数/姓名を使って確実に「 / 」区切りへ整形する。
        sgt_driver_map_2026 = {
            "8": ["太田 格之進", "大津 弘樹"], "12": ["平峰 一貴", "ベルトラン・バゲット"],
            "14": ["福住 仁嶺", "大嶋 和也"], "16": ["野尻 智紀", "佐藤 蓮"],
            "17": ["塚越 広大", "野村 勇斗"], "19": ["国本 雄資", "阪口 晴南"],
            "23": ["千代 勝正", "高星 明誠"], "24": ["名取 鉄平", "三宅 淳詞"],
            "36": ["坪井 翔", "山下 健太"], "37": ["笹原 右京", "ジュリアーノ・アレジ"],
            "38": ["大湯 都史樹", "小林 利徠斗"], "39": ["関口 雄飛", "サッシャ・フェネストラズ"],
            "64": ["大草 りき", "イゴール・オオムラ・フラガ"], "100": ["山本 尚貴", "牧野 任祐"],
        }
        if cls == "GT300":
            sgt_driver_map_2026.update({
                "2": ["堤 優威", "卜部 和久"], "4": ["谷口 信輝", "片岡 龍也"],
                "5": ["塩津 佑介", "荒尾 創大"], "6": ["片山 義章", "ニクラス・クルッテン"],
                "7": ["ザック・オサリバン", "伊東 黎明"], "9": ["冨林 勇佑", "藤原 優汰"],
                "11": ["富田 竜一郎", "大木 一輝"], "18": ["小林 崇志", "新原 光太郎"],
                "20": ["平中 克幸", "清水 英志郎"], "22": ["和田 久", "加納 政樹"],
                "25": ["松井 孝允", "洞地 遼大"], "26": ["安田 裕信", "リ・ジョンウ"],
                "30": ["永井 宏明", "平良 響"], "31": ["小高 一斗", "小山 美姫"],
                "32": ["石浦 宏明", "鈴木 斗輝哉"], "45": ["ケイ・コッツォリーノ", "篠原 拓朗"],
                "48": ["井田 太陽", "ジェームス・プル"], "52": ["吉田 広樹", "野中 誠太"],
                "56": ["ジョアオ・パオロ・デ・オリベイラ", "木村 偉織"],
                "60": ["吉本 大樹", "河野 駿佑"], "61": ["井口 卓人", "山内 英輝"],
                "62": ["平木 湧也", "平木 玲次"], "65": ["蒲生 尚弥", "菅波 冬悟"],
                "87": ["元嶋 佑弥", "松浦 孝亮"], "88": ["小暮 卓史", "ダニール・クビアト"],
                "96": ["新田 守男", "高木 真一"], "360": ["荒川 麟", "金丸 ユウ"],
                "666": ["スヴェン・ミューラー", "藤波 清斗"], "777": ["藤井 誠暢", "チャーリー・ファグ"],
            })
        known_drivers = sgt_driver_map_2026.get(num)
        if known_drivers:
            drivers = " / ".join(known_drivers)
        else:
            drivers = re.sub(r"\s{2,}", " / ", drivers)
        # 予選ポイントは最終予選(Q2)のポールポジションだけ1pt。Q1は0pt。
        points = 1 if session == "予選Q2" and rank == 1 else (
            race_pts[cls][rank - 1] if session == "決勝" and rank <= len(race_pts[cls]) else 0
        )
        laps = None
        if lap_i is not None and lap_i < len(raw):
            lm = re.search(r"\d+", raw[lap_i])
            laps = int(lm.group()) if lm else None
        rows.append({
            "順位": rank, "グループ": group, "カーナンバー": num, "ドライバー": drivers,
            "チーム": team, "ポイント": points, "ステータス": "完走",
            "周回数": laps,
        })

    # Q1ではタイム未計測などで順位欄が数値にならない車両が表末尾に出ることがある。
    # 2026年はエントリーマップを使い、結果表から漏れた車両も0ptで残す。
    if session in ["予選Q1", "予選Q2"]:
        expected_nums = list(sgt_driver_map_2026.keys())
        seen_nums = {str(x["カーナンバー"]) for x in rows}
        for missing_num in expected_nums:
            if missing_num in seen_nums:
                continue
            # GT500/GT300のマップが混ざらないよう、元のクラス台数で絞る。
            if cls == "GT500" and missing_num not in {"8","12","14","16","17","19","23","24","36","37","38","39","64","100"}:
                continue
            if cls == "GT300" and missing_num in {"8","12","14","16","17","19","23","24","36","37","38","39","64","100"}:
                continue
            # 順位なし車両でも、公式表の該当行からチーム名を回収する。
            missing_team = ""
            for raw in table[header_idx + 1:]:
                if no_i < len(raw) and raw[no_i].strip() == missing_num and team_i < len(raw):
                    team_machine = raw[team_i].strip()
                    tm = re.search(r"チーム\s*(.*?)\s*マシン\s*", team_machine)
                    missing_team = tm.group(1).strip() if tm else team_machine
                    break
            rows.append({
                "順位": len(rows) + 1, "カーナンバー": missing_num,
                "ドライバー": " / ".join(sgt_driver_map_2026[missing_num]),
                "チーム": missing_team, "ポイント": 0, "ステータス": "予選未分類", "周回数": None,
            })

    if not rows:
        raise ValueError("SUPER GTの順位データを取得できませんでした。")
    return rows, session, cls


def extract_sf_result_url(url):
    """SUPER FORMULA公式リザルトページを解析する。公式HTMLは通常のtableタグではないため本文構造から取得。"""
    import re
    import requests
    from html import unescape
    from urllib.parse import urlparse

    url = url.strip()
    parsed = urlparse(url)
    if parsed.netloc.lower() not in ["superformula.net", "www.superformula.net"]:
        raise ValueError("SUPER FORMULA公式サイトのリザルトURLを入力してください。")

    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"

    lower_url = url.lower()
    if "qf" in lower_url:
        session = "予選"
    elif "race" in lower_url:
        session = "決勝"
    else:
        raise ValueError("予選 / 決勝をURLから判定できませんでした。")

    # script/styleを除去し、HTMLをプレーンテキスト化。
    html = re.sub(r"<script[\s\\S]*?</script>", " ", response.text, flags=re.I)
    html = re.sub(r"<style[\s\\S]*?</style>", " ", html, flags=re.I)
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"\s+", " ", text)

    # 2026の公式ページは「Po. No. Driver Team ／ Engine Lap ...」の順。
    # 公式HTMLではヘッダーの区切りが装飾要素で崩れる場合があるため、
    # 厳密な1本の正規表現ではなく No. / Driver / Team の位置関係で結果開始点を探す。
    marker = re.search(r"No\\.?\s+Driver\s+Team", text, flags=re.I)
    if not marker:
        # さらに装飾文字を無視したフォールバック。
        compact = re.sub(r"[^A-Za-z0-9一-龥ぁ-んァ-ヶ]+", " ", text)
        marker2 = re.search(r"No\s+Driver\s+Team", compact, flags=re.I)
        if not marker2:
            raise ValueError("公式ページの結果ヘッダーを見つけられませんでした。")
        # compact側の位置は元HTML本文に対応しないので、最初の2026エントリー順位列を直接探す。
        start = re.search(r"\b1\s+[AB]\s+\d{1,2}\s+", text) if session == "予選" else re.search(r"\b1\s+\d{1,2}\s+", text)
        if not start:
            raise ValueError("公式ページの順位データ開始位置を見つけられませんでした。")
        result_text = text[start.start():]
    else:
        result_text = text[marker.end():]
    end_markers = ["車両：", "Fastest Lap", "PENALTIES", "GO TO TOP"]
    end_positions = [result_text.find(x) for x in end_markers if result_text.find(x) >= 0]
    if end_positions:
        result_text = result_text[:min(end_positions)]

    # 2026エントリーの車番→ドライバー/チーム。
    # 日本語名の直後に英語名が連結される公式HTMLなので、車番を境界として各行を切り出す。
    sf_entries = {
        "1": ("岩佐 歩夢", "TEAM MUGEN AUTOBACS"),
        "16": ("野尻 智紀", "TEAM MUGEN AUTOBACS"),
        "3": ("ルーク･ブラウニング", "REALIZE KONDO RACING"),
        "4": ("笹原 右京", "REALIZE KONDO RACING"),
        "5": ("牧野 任祐", "DOCOMO TEAM DANDELION RACING"),
        "6": ("太田 格之進", "DOCOMO TEAM DANDELION RACING"),
        "7": ("小林 可夢偉", "KDDI TGMGP TGR-DC"),
        "28": ("小林 利徠斗", "KDDI TGMGP TGR-DC"),
        "8": ("山下 健太", "KCMG"),
        "9": ("野中 誠太", "KCMG"),
        "10": ("Juju", "HAZAMA ANDO Triple Tree Racing"),
        "12": ("小出 峻", "ThreeBond Racing"),
        "14": ("福住 仁嶺", "NTT docomo Business ROOKIE"),
        "19": ("ザック･オサリバン", "TEAM IMPUL"),
        "22": ("松下 信治", "DELiGHTWORKS RACING"),
        "36": ("坪井 翔", "VANTELIN TEAM TOM’S"),
        "37": ("サッシャ･フェネストラズ", "VANTELIN TEAM TOM’S"),
        "38": ("阪口 晴南", "SANKI VERTEX PARTNERS CERUMO･INGING"),
        "39": ("大湯 都史樹", "SANKI VERTEX PARTNERS CERUMO･INGING"),
        "50": ("野村 勇斗", "San-Ei Gen with B-Max"),
        "53": ("チャーリー･ブルツ", "TEAM GOH"),
        "64": ("佐藤 蓮", "PONOS NAKAJIMA RACING"),
        "65": ("イゴール･オオムラ･フラガ", "PONOS NAKAJIMA RACING"),
        "97": ("ロマン･スタネック", "Buzz MK RACING"),
    }

    rows = []
    race_points = [20, 15, 11, 8, 6, 5, 4, 3, 2, 1]
    qual_points = [3, 2, 1]
    # 公式ページの結果部分から各2026車番の出現位置を探し、その直前にある順位を採用する。
    # 決勝はラップ数/タイム等の数字が多いため「順位 車番」の連続regexには頼らない。
    found = []
    seen_ranks = set()
    used_nums = set()
    for num, (driver, team) in sf_entries.items():
        # 車番の後ろ180文字以内にそのドライバー名がある出現だけを結果行候補にする。
        for nm in re.finditer(r"(?<!\d)" + re.escape(num) + r"(?!\d)", result_text):
            after = result_text[nm.end():nm.end() + 180]
            compact_after = re.sub(r"\s+", "", after).replace("・", "･")
            compact_driver = re.sub(r"\s+", "", driver).replace("・", "･")
            driver_parts = [p for p in re.split(r"[ ･・]+", driver) if p]
            if compact_driver not in compact_after and not (
                driver_parts and all(p in after for p in driver_parts)
            ):
                continue

            # 車番の直前には決勝なら順位、予選なら「順位 A/B」がある。
            before = result_text[max(0, nm.start() - 25):nm.start()]
            if session == "予選":
                rm = re.search(r"(\d{1,2})\s+[AB]\s*$", before)
            else:
                rm = re.search(r"(\d{1,2})\s*$", before)
            if not rm:
                continue
            rank = int(rm.group(1))
            if not (1 <= rank <= 30) or rank in seen_ranks or num in used_nums:
                continue

            seen_ranks.add(rank)
            used_nums.add(num)
            pts = (qual_points[rank - 1] if session == "予選" and rank <= 3
                   else race_points[rank - 1] if session == "決勝" and rank <= 10 else 0)
            found.append((nm.start(), {
                "順位": rank, "カーナンバー": num, "ドライバー": driver,
                "チーム": team, "ポイント": pts, "ステータス": "完走"
            }))
            break

    # 決勝の未分類車は順位自体が無い場合もあるので、NOT CLASSIFIED部から未取得車を追加。
    if session == "決勝":
        nc_pos = result_text.find("NOT CLASSIFIED")
        if nc_pos >= 0:
            nc_text = result_text[nc_pos:]
            next_rank = max([row["順位"] for _, row in found], default=0) + 1
            for num, (driver, team) in sf_entries.items():
                if num in used_nums:
                    continue
                for nm in re.finditer(r"(?<!\d)" + re.escape(num) + r"(?!\d)", nc_text):
                    after = nc_text[nm.end():nm.end() + 180]
                    compact_after = re.sub(r"\s+", "", after).replace("・", "･")
                    compact_driver = re.sub(r"\s+", "", driver).replace("・", "･")
                    driver_parts = [p for p in re.split(r"[ ･・]+", driver) if p]
                    if compact_driver in compact_after or (
                        driver_parts and all(p in after for p in driver_parts)
                    ):
                        found.append((nc_pos + nm.start(), {
                            "順位": next_rank, "カーナンバー": num, "ドライバー": driver,
                            "チーム": team, "ポイント": 0, "ステータス": "リタイア"
                        }))
                        used_nums.add(num)
                        next_rank += 1
                        break

    rows.extend(row for _, row in found)

    # 予選のNOT CLASSIFIEDは順位番号が付かないため、通常の順位regexでは拾えない。
    # 公式ページに掲載された未分類車も末尾へ追加し、24台すべて保持する。
    if session == "予選":
        not_classified_pos = result_text.find("NOT CLASSIFIED")
        if not_classified_pos >= 0:
            nc_text = result_text[not_classified_pos:]
            already_nums = {x["カーナンバー"] for x in rows}
            nc_order = []
            for num, (driver, team) in sf_entries.items():
                if num in already_nums:
                    continue
                # NOT CLASSIFIED部分で「A/B + 車番 + ドライバー名」の並びを確認する。
                pat = re.compile(r"(?:^|\s)[AB]\s+" + re.escape(num) + r"(?=\s)")
                m_nc = pat.search(nc_text)
                if not m_nc:
                    continue
                tail = nc_text[m_nc.end():]
                next_entry = re.search(r"\s[AB]\s+\d{1,2}(?=\s)", tail)
                chunk = tail[:next_entry.start()] if next_entry else tail
                driver_parts = [p for p in re.split(r"[ ･・]+", driver) if p]
                if driver_parts and all(p in chunk for p in driver_parts):
                    nc_order.append((m_nc.start(), num, driver, team))
            nc_order.sort()
            next_rank = max([x["順位"] for x in rows], default=0) + 1
            for _, num, driver, team in nc_order:
                rows.append({
                    "順位": next_rank,
                    "カーナンバー": num,
                    "ドライバー": driver,
                    "チーム": team,
                    "ポイント": 0,
                    "ステータス": "予選未分類",
                })
                next_rank += 1

    rows.sort(key=lambda x: x["順位"])
    if not rows:
        raise ValueError("順位データを取得できませんでした。")
    return rows, session

def extract_wec_timing_url(url):
    """Al Kamel Timing Resultsのテキスト入りClassification PDFを直接解析する。OCRは使わない。"""
    import io
    import re
    import requests
    import pdfplumber

    from urllib.parse import urlparse

    url = url.strip()
    parsed = urlparse(url)
    if parsed.netloc.lower() != "fiawec.alkamelsystems.com" or "/Results/" not in parsed.path or not parsed.path.lower().endswith(".pdf"):
        raise ValueError("Al Kamel Timing ResultsのPDF URLを入力してください。")

    # URL末尾に ?utm_source=... などが付いていても受け付ける
    response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    pdf_bytes = io.BytesIO(response.content)

    with pdfplumber.open(pdf_bytes) as pdf:
        text = "\n".join((p.extract_text(x_tolerance=2, y_tolerance=2) or "") for p in pdf.pages)

    upper = text.upper()
    if "HYPERPOLE" in upper:
        session = "ハイパーポール"
    elif "QUALIFYING" in upper:
        session = "予選"
    elif "RACE" in upper:
        session = "決勝"
    else:
        raise ValueError("Race / Qualifying / Hyperpoleを判定できませんでした。")

    # 2026年の車番→チーム。PDF本文からドライバーは直接取得する。
    entries = {
        "15": ("BMW M Team WRT", "Hypercar"), "51": ("Ferrari AF Corse", "Hypercar"),
        "12": ("Cadillac Hertz Team Jota", "Hypercar"), "38": ("Cadillac Hertz Team Jota", "Hypercar"),
        "83": ("AF Corse", "Hypercar"), "007": ("Aston Martin Thor Team", "Hypercar"),
        "50": ("Ferrari AF Corse", "Hypercar"), "20": ("BMW M Team WRT", "Hypercar"),
        "009": ("Aston Martin Thor Team", "Hypercar"), "35": ("Alpine Endurance Team", "Hypercar"),
        "36": ("Alpine Endurance Team", "Hypercar"), "7": ("Toyota Racing", "Hypercar"),
        "19": ("Genesis Magma Racing", "Hypercar"), "94": ("Peugeot Totalenergies", "Hypercar"),
        "17": ("Genesis Magma Racing", "Hypercar"), "93": ("Peugeot Totalenergies", "Hypercar"),
        "8": ("Toyota Racing", "Hypercar"),
        "34": ("Racing Team Turkey by TF", "LMGT3"), "69": ("Team WRT", "LMGT3"),
        "92": ("The Bend Manthey", "LMGT3"), "91": ("Manthey DK Engineering", "LMGT3"),
        "88": ("Proton Competition", "LMGT3"), "61": ("Iron Lynx", "LMGT3"),
        "87": ("Akkodis ASP Team", "LMGT3"), "33": ("TF Sport", "LMGT3"),
        "21": ("Vista AF Corse", "LMGT3"), "77": ("Proton Competition", "LMGT3"),
        "58": ("Garage 59", "LMGT3"), "32": ("Team WRT", "LMGT3"),
        "27": ("Heart of Racing Team", "LMGT3"), "78": ("Akkodis ASP Team", "LMGT3"),
        "79": ("Iron Lynx", "LMGT3"), "10": ("Garage 59", "LMGT3"),
        "54": ("Vista AF Corse", "LMGT3"), "23": ("Heart of Racing Team", "LMGT3"),
    }

    # 行の並びがPDF内部で前後することがあるので、順位+車番を全文から探す。
    # ドライバー列は「A. NAME / B. NAME ...」の形を独立して取得。
    driver_pat = re.compile(
        r"([A-ZÀ-ÖØ-Þ]\.?\s*[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-öø-ÿ' .-]+"
        r"(?:\s*/\s*[A-ZÀ-ÖØ-Þ]\.?\s*[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-öø-ÿ' .-]+){1,2})"
    )

    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines() if x.strip()]
    rows_by_class = {"Hypercar": [], "LMGT3": []}

    for line in lines:
        # Classificationの実順位・車番は必ず行頭側にある。
        # 行中のラップ数などを順位/車番と誤認しないよう、再び行頭に固定する。
        # HPは行頭にある場合と行の途中にある場合があるが、途中のHPは無視してよい。
        # 007/009はPDFの文字配置上、pdfplumberが "00 7" / "0 09" のように
        # 車番内部へ空白を入れて抽出することがある。Astonの3桁車番だけ内部空白を許可する。
        m = re.match(
            r"^(?:HP\s*)?(?:(\d{1,2})\s+((?:0\s*0\s*[79])|\d{1,3})\s+|(\d{1,2})(00[79]))(.+)$",
            line,
        )
        if not m:
            continue
        if m.group(1) is not None:
            rank, num, rest = int(m.group(1)), re.sub(r"\s+", "", m.group(2)), m.group(5)
        else:
            rank, num, rest = int(m.group(3)), m.group(4), m.group(5)
        if num not in entries:
            continue
        team, cls = entries[num]

        dm = driver_pat.search(rest)
        crew = dm.group(1).strip() if dm else ""

        # pdfplumberの内部順序でドライバーが行末側に来るケースもある。
        if not crew:
            dm = driver_pat.search(line)
            crew = dm.group(1).strip() if dm else ""

        # pdfplumberでは車種列の一部がドライバー列の前後に連結される。
        # 例: "WRT K. MAGNUSSEN / ... / D. VANTHOOR BMW M H"
        #      "... / A. GIOVINAZZI F"
        # まず先頭を「頭文字. 姓」が始まる位置まで切り、末尾は車種由来の断片を除去する。
        first_driver = re.search(r"[A-ZÀ-ÖØ-Þ]\.\s", crew)
        if first_driver:
            crew = crew[first_driver.start():].strip()

        parts = [p.strip() for p in crew.split("/")][:3]
        if parts:
            # 最後のドライバー末尾に付く車種列。
            parts[-1] = re.split(
                r"\s+(?=(?:BMW|FERRARI|CADILLAC|ASTON|ALPINE|PEUGEOT|TOYOTA|GENESIS|PORSCHE|FORD|LEXUS|MERCEDES|CORVETTE|MCLAREN)\b)",
                parts[-1], maxsplit=1, flags=re.I
            )[0].strip()
            # PDF列の残骸が1文字だけ付くケース (F/C/A/P/G/T/H/M) を除去。
            # 正規の姓は1文字では終わらないため安全に落とせる。
            parts[-1] = re.sub(r"\s+[A-Z]$", "", parts[-1]).strip()
            crew = " / ".join(parts)

        points = 0
        if session == "ハイパーポール" and rank == 1:
            points = 1
        elif session == "決勝":
            # WEC公式配点はレース長で変わる。
            # 6h: 通常配点 / 8h・10h・1812km: 1.5倍系 / Le Mans 24h: 2倍。
            url_upper = urllib.parse.unquote(url).upper()
            text_upper = text.upper()
            event_hint = f"{url_upper} {text_upper}"
            if "LE MANS" in event_hint and "LONE STAR" not in event_hint:
                race_points = [50, 36, 30, 24, 20, 16, 12, 8, 4, 2]
                points_scale = "24h"
            elif any(token in event_hint for token in ["1812", "QATAR", "BAHRAIN", "8 HOURS", "8 HOUR", "10 HOURS", "10 HOUR"]):
                race_points = [38, 27, 23, 18, 15, 12, 9, 6, 3, 2]
                points_scale = "8h/10h"
            else:
                race_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
                points_scale = "6h"
            points = race_points[rank - 1] if rank <= 10 else 0

        rows_by_class[cls].append({
            "順位": rank, "カーナンバー": num, "ドライバー": crew,
            "チーム": team, "ポイント": points, "ステータス": "完走",
        })

    groups = []
    for cls, rows in rows_by_class.items():
        # 同じ車を重複取得した場合は順位の最初の1件だけ残す
        unique = {}
        for row in sorted(rows, key=lambda x: x["順位"]):
            unique.setdefault(row["カーナンバー"], row)
        rows = list(unique.values())
        if rows:
            group = {"クラス": cls, "セッション": session, "rows": rows}
            if session == "決勝":
                group["配点区分"] = points_scale
            groups.append(group)
    return groups



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
# --- SUPER GT公式Webリザルトインポート ---
if s_cat == "SUPER GT":
    with st.sidebar.expander("🌐 SUPER GT公式リザルトを読み込む"):
        if st.session_state.get("sgt_import_success"):
            st.success(st.session_state.pop("sgt_import_success"))
        st.caption("SUPER GT公式「順位」ページの予選Q1・Q2または決勝レースURLを貼り付けます。GT500/GT300とセッションはURLから自動判定します。")
        sgt_url = st.text_input("SUPER GT公式リザルトURL", placeholder="https://supergt.net/result?gt_class=gt500&race_num=4&round=Round1&series=2026", key="sgt_result_url")
        if sgt_url.strip():
            try:
                with st.spinner("SUPER GT公式リザルトを読み込み中…"):
                    sgt_rows, sgt_session, sgt_class = extract_supergt_result_url(sgt_url.strip())
                st.success(f"{len(sgt_rows)}台を読み取れました！ {sgt_class} / {sgt_session}")
                st.dataframe(pd.DataFrame(sgt_rows), use_container_width=True, hide_index=True)

                sgt_year = st.selectbox("登録年度", YEARS, key="sgt_import_year")
                sgt_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.1 岡山", key="sgt_import_round")
                sgt_date = st.date_input("開催日", datetime.date.today(), key="sgt_import_date")

                if st.button("このSUPER GT結果を登録 / 更新", type="primary", use_container_width=True, key="sgt_import_save"):
                    if not sgt_round.strip():
                        st.error("レース名 / ラウンドを入力してください。")
                    else:
                        races = data.setdefault("races", {}).setdefault(sgt_year, {}).setdefault("SUPER GT", {}).setdefault(sgt_class, [])
                        teams = [x["チーム"] for x in sgt_rows]
                        drivers = [x["ドライバー"] for x in sgt_rows]
                        car_numbers = [x["カーナンバー"] for x in sgt_rows]
                        statuses = [x["ステータス"] for x in sgt_rows]
                        official_points = [x["ポイント"] for x in sgt_rows]
                        groups = [x.get("グループ", "") for x in sgt_rows]
                        new_race = {
                            "round_name": sgt_round.strip(), "race_date": str(sgt_date),
                            "session_type": sgt_session, "is_custom_pts": True,
                            "points_table": official_points, "results": teams, "drivers": drivers,
                            "car_numbers": car_numbers, "statuses": statuses,
                            "official_points": official_points,
                            "groups": groups,
                            "laps": [x.get("周回数") for x in sgt_rows],
                        }
                        idx = next((i for i, x in enumerate(races)
                                    if x.get("round_name") == sgt_round.strip()
                                    and x.get("session_type", "決勝") == sgt_session), None)
                        if idx is None:
                            races.append(new_race)
                        else:
                            races[idx] = new_race
                        master = data.setdefault("teams", {}).setdefault(f"SUPER GT_{sgt_class}", [])
                        for team in teams:
                            if team and team not in master:
                                master.append(team)
                        save_data(data)
                        st.session_state["sgt_import_success"] = f"✅ SUPER GT {sgt_class} / {sgt_session}を登録 / 更新しました！"
                        st.rerun()
            except Exception as e:
                st.error(f"SUPER GT公式リザルトの読み込みに失敗しました: {e}")


# --- SUPER FORMULA公式Webリザルトインポート ---
if s_cat == "Super Formula":
    with st.sidebar.expander("🌐 SF公式リザルトを読み込む"):
        if st.session_state.get("sf_import_success"):
            st.success(st.session_state.pop("sf_import_success"))
        st.caption("SUPER FORMULA公式サイトの予選または決勝リザルトURLを貼り付けます。")
        sf_url = st.text_input("SF公式リザルトURL", placeholder="https://superformula.net/sf2/race2026/.../r1race", key="sf_result_url")
        if sf_url.strip():
            try:
                with st.spinner("SF公式リザルトを読み込み中…"):
                    sf_rows, sf_session = extract_sf_result_url(sf_url.strip())
                st.success(f"{len(sf_rows)}台を読み取れました！ セッション: {sf_session}")
                st.dataframe(pd.DataFrame(sf_rows), use_container_width=True, hide_index=True)

                sf_year = st.selectbox("登録年度", YEARS, key="sf_import_year")
                sf_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.1 もてぎ", key="sf_import_round")
                sf_date = st.date_input("開催日", datetime.date.today(), key="sf_import_date")
                sf_multiplier = 1.0
                if sf_session == "決勝":
                    sf_multiplier = st.selectbox(
                        "決勝ポイント倍率",
                        [1.0, 0.5],
                        format_func=lambda x: "通常（100%）" if x == 1.0 else "ハーフポイント（50%）",
                        key="sf_points_multiplier",
                    )
                    if sf_multiplier == 0.5:
                        st.info("短縮レース等のハーフポイントとして登録します。")

                preview_points = [row["ポイント"] * sf_multiplier for row in sf_rows]
                if sf_session == "決勝" and sf_multiplier != 1.0:
                    st.caption("登録ポイント: " + " / ".join(f"P{i+1} {p:g}pt" for i, p in enumerate(preview_points[:10])))

                if st.button("このSF結果を登録 / 更新", type="primary", use_container_width=True, key="sf_import_save"):
                    if not sf_round.strip():
                        st.error("レース名 / ラウンドを入力してください。")
                    else:
                        races = data.setdefault("races", {}).setdefault(sf_year, {}).setdefault("Super Formula", {}).setdefault("総合", [])
                        teams = [x["チーム"] for x in sf_rows]
                        drivers = [x["ドライバー"] for x in sf_rows]
                        car_numbers = [x["カーナンバー"] for x in sf_rows]
                        statuses = [x["ステータス"] for x in sf_rows]
                        official_points = [x["ポイント"] * sf_multiplier for x in sf_rows]
                        new_race = {
                            "round_name": sf_round.strip(), "race_date": str(sf_date),
                            "session_type": sf_session, "is_custom_pts": sf_multiplier != 1.0,
                            "points_table": official_points, "results": teams, "drivers": drivers,
                            "car_numbers": car_numbers, "statuses": statuses,
                            "official_points": official_points,
                            "sf_points_multiplier": sf_multiplier,
                        }
                        idx = next((i for i, x in enumerate(races)
                                    if x.get("round_name") == sf_round.strip()
                                    and x.get("session_type", "決勝") == sf_session), None)
                        if idx is None:
                            races.append(new_race)
                        else:
                            races[idx] = new_race
                        master = data.setdefault("teams", {}).setdefault("Super Formula_総合", [])
                        for team in teams:
                            if team and team not in master:
                                master.append(team)
                        save_data(data)
                        st.session_state["sf_import_success"] = f"✅ SF {sf_session}結果を登録 / 更新しました！"
                        st.rerun()
            except Exception as e:
                st.error(f"SF公式リザルトの読み込みに失敗しました: {e}")


# --- F1公式PDFインポート ---
if s_cat == "WEC":
    with st.sidebar.expander("🌐 WEC Timing Resultsを読み込む"):
        if st.session_state.get("wec_import_success"):
            st.success(st.session_state.pop("wec_import_success"))
        st.caption("Al Kamel Timing Resultsの「CLASSIFICATION BY CATEGORY」PDFのURLを貼り付けます。OCRは使いません。")
        wec_url = st.text_input(
            "Classification PDF URL",
            placeholder="https://fiawec.alkamelsystems.com/Results/.../05_ClassificationByCategory_....PDF",
            key="wec_timing_url",
        )
        if wec_url.strip():
            try:
                with st.spinner("公式Timing Resultsを読み込み中…"):
                    wec_groups = extract_wec_timing_url(wec_url.strip())
                if wec_groups:
                    for g in wec_groups:
                        scale_note = f" / 配点: {g['配点区分']}" if g.get("配点区分") else ""
                        st.markdown(f"**{g['クラス']} / {g['セッション']} — {len(g['rows'])}台{scale_note}**")
                        st.dataframe(pd.DataFrame(g["rows"]), use_container_width=True, hide_index=True)

                    wec_year = st.selectbox("登録年度", YEARS, key="wec_import_year")
                    wec_round = st.text_input("レース名 / ラウンド", placeholder="例: Rd.4 サンパウロ6時間", key="wec_import_round")
                    wec_date = st.date_input("開催日", datetime.date.today(), key="wec_import_date")

                    if st.button("このWEC結果を登録 / 更新", type="primary", use_container_width=True, key="wec_import_save"):
                        if not wec_round.strip():
                            st.error("レース名 / ラウンドを入力してください。")
                        else:
                            saved = 0
                            for g in wec_groups:
                                cls, session, rows = g["クラス"], g["セッション"], g["rows"]
                                races = data.setdefault("races", {}).setdefault(wec_year, {}).setdefault("WEC", {}).setdefault(cls, [])
                                teams = [x["チーム"] for x in rows]
                                drivers = [x["ドライバー"] for x in rows]
                                car_numbers = [x["カーナンバー"] for x in rows]
                                statuses = [x["ステータス"] for x in rows]
                                official_points = [x["ポイント"] for x in rows]
                                new_race = {
                                    "round_name": wec_round.strip(), "race_date": str(wec_date),
                                    "session_type": session, "is_custom_pts": True,
                                    "points_table": official_points, "results": teams, "drivers": drivers,
                                    "car_numbers": car_numbers, "statuses": statuses,
                                    "official_points": official_points,
                                    "wec_points_scale": g.get("配点区分"),
                                }
                                idx = next((i for i, x in enumerate(races)
                                            if x.get("round_name") == wec_round.strip()
                                            and x.get("session_type", "決勝") == session), None)
                                if idx is None:
                                    races.append(new_race)
                                else:
                                    races[idx] = new_race
                                master = data.setdefault("teams", {}).setdefault(f"WEC_{cls}", [])
                                for team in teams:
                                    if team not in master:
                                        master.append(team)
                                saved += 1
                            save_data(data)
                            st.session_state["wec_import_success"] = f"✅ WEC結果を{saved}クラス登録 / 更新しました！"
                            st.rerun()
                else:
                    st.warning("順位を取得できませんでした。CLASSIFICATION BY CATEGORYのPDF URLか確認してください。")
            except Exception as e:
                st.error(f"WEC Timing Resultsの読み込みに失敗しました: {e}")


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
                                "car_numbers": car_numbers,
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
            # WEC/SUPER GTでは詳細な予選セッションを「予選」の下にまとめる
            if v_cat in ["WEC", "SUPER GT"]:
                session_options = ["すべて", "決勝", "予選"]
            else:
                session_options = ["すべて", "決勝", "予選", "スプリント"]
            sel_session_filter = st.selectbox("セッション選択", session_options)

            wec_qualifying_filter = None
            sgt_qualifying_filter = None
            if v_cat == "WEC" and sel_session_filter == "予選":
                wec_qualifying_filter = st.selectbox(
                    "予選セッション",
                    ["すべて", "予選", "ハイパーポール"],
                    key="wec_qualifying_session_filter",
                )
            elif v_cat == "SUPER GT" and sel_session_filter == "予選":
                sgt_qualifying_filter = st.selectbox(
                    "予選セッション",
                    ["すべて", "予選Q1", "予選Q1 A", "予選Q1 B", "予選Q2"],
                    key="sgt_qualifying_session_filter",
                )

        round_races = [
            r
            for r in races_list
            if r.get("round_name", r.get("race_name")) == sel_round
        ]
        if sel_session_filter != "すべて":
            if v_cat == "WEC" and sel_session_filter == "予選":
                if wec_qualifying_filter in [None, "すべて"]:
                    round_races = [
                        r for r in round_races
                        if r.get("session_type", "決勝") in ["予選", "ハイパーポール"]
                    ]
                else:
                    round_races = [
                        r for r in round_races
                        if r.get("session_type", "決勝") == wec_qualifying_filter
                    ]
            elif v_cat == "SUPER GT" and sel_session_filter == "予選":
                if sgt_qualifying_filter in [None, "すべて"]:
                    round_races = [
                        r for r in round_races
                        if r.get("session_type", "決勝") in ["予選", "予選Q1", "予選Q1 A", "予選Q1 B", "予選Q2"]
                    ]
                else:
                    round_races = [
                        r for r in round_races
                        if r.get("session_type", "決勝") == sgt_qualifying_filter
                    ]
            else:
                round_races = [
                    r
                    for r in round_races
                    if r.get("session_type", "決勝") == sel_session_filter
                ]

        if round_races:
            # 閲覧画面は見やすさ優先で「決勝 → スプリント → 予選」の順に表示
            view_session_order = {"決勝": 0, "スプリント": 1, "ハイパーポール": 2, "予選": 3, "予選Q2": 3, "予選Q1": 4, "予選Q1 A": 4, "予選Q1 B": 5}
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
                wec_scale = target.get("wec_points_scale")
                if v_cat == "WEC" and target.get("session_type", "決勝") == "決勝" and wec_scale:
                    scale_names = {"6h": "6時間レース", "8h/10h": "8時間 / 10時間レース", "24h": "24時間レース"}
                    st.caption(
                        f"📅 開催日: {r_date_str} ｜ ⏱️ レース区分: {scale_names.get(wec_scale, wec_scale)} ｜ 🎯 適用ルール: {pts_label}"
                    )
                else:
                    st.caption(f"📅 開催日: {r_date_str} ｜ 🎯 適用ルール: {pts_label}")

                # 削除は結果表の右上に小さく配置し、誤操作を減らす
                _, delete_col = st.columns([5, 1])
                with delete_col:
                    if st.button(
                        "🗑️ 削除",
                        key=f"del_btn_{sel_round}_{target.get('session_type')}",
                        help="このセッション結果を削除",
                    ):
                        races_list.remove(target)
                        save_data(data)
                        st.warning("データを削除しました。")
                        st.rerun()

                pts_table = target.get("points_table", DEFAULT_PTS_RACE)

                statuses = target.get("statuses", ["完走"] * len(target["results"]))
                drivers = target.get("drivers", [])
                car_numbers = target.get("car_numbers", [])
                groups = target.get("groups", [])
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
                if groups and any(groups):
                    df_data["グループ"] = [
                        groups[i] if i < len(groups) and groups[i] else "-"
                        for i in range(len(target["results"]))
                    ]
                if car_numbers:
                    df_data["カーナンバー"] = [
                        f"#{car_numbers[i]}" if i < len(car_numbers) and car_numbers[i] not in [None, ""] else "-"
                        for i in range(len(target["results"]))
                    ]
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

                    if st.button(
                        "変更を保存する",
                        key=f"save_btn_{sel_round}_{target.get('session_type')}",
                        use_container_width=True,
                    ):
                        target["results"] = edit_results
                        save_data(data)
                        st.success("結果を更新しました！")
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
        session_order = {"予選": 0, "ハイパーポール": 1, "スプリント": 2, "決勝": 3}
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
        # WEC Hypercarのマニュファクチャラー選手権は、各メーカーが指定した2台が対象。
        # 追加車両（例: Ferrari #83）は対象外にし、対象車だけで順位を詰め直して
        # その順位に応じた決勝ポイントを2台分合算する。
        wec_manufacturer_cars = {
            "15": "BMW", "20": "BMW",
            "50": "FERRARI", "51": "FERRARI",
            "12": "CADILLAC", "38": "CADILLAC",
            "007": "ASTON MARTIN", "009": "ASTON MARTIN",
            "35": "ALPINE", "36": "ALPINE",
            "7": "TOYOTA", "8": "TOYOTA",
            "17": "GENESIS", "19": "GENESIS",
            "93": "PEUGEOT", "94": "PEUGEOT",
        }
        is_wec_manufacturer = r_cat == "WEC" and r_cls == "Hypercar"

        if is_wec_manufacturer:
            manufacturers = list(dict.fromkeys(wec_manufacturer_cars.values()))
            for manufacturer in manufacturers:
                team_points_matrix[manufacturer] = [0] * len(races)

            for race_idx, r in enumerate(races):
                session_type = r.get("session_type", "決勝")
                car_numbers = [str(n) for n in r.get("car_numbers", [])]

                if session_type == "決勝":
                    # 決勝はメーカー選手権対象の2台だけを抜き出し、その中で順位を再計算する。
                    eligible = []
                    statuses = r.get("statuses", [])
                    for original_idx, num in enumerate(car_numbers):
                        manufacturer = wec_manufacturer_cars.get(num)
                        if manufacturer:
                            status = statuses[original_idx] if original_idx < len(statuses) else "完走"
                            eligible.append((manufacturer, status))

                    scale = r.get("wec_points_scale", "6h")
                    manufacturer_points = {
                        "6h": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1],
                        "8h/10h": [38, 27, 23, 18, 15, 12, 9, 6, 3, 2],
                        "24h": [50, 36, 30, 24, 20, 16, 12, 8, 4, 2],
                    }.get(scale, [25, 18, 15, 12, 10, 8, 6, 4, 2, 1])

                    for eligible_rank, (manufacturer, status) in enumerate(eligible):
                        pt = 0 if status in ["DNS", "DSQ"] else (
                            manufacturer_points[eligible_rank] if eligible_rank < len(manufacturer_points) else 0
                        )
                        team_points_matrix[manufacturer][race_idx] += pt

                elif session_type == "ハイパーポール":
                    # Hyperpoleのポール1点はマニュファクチャラー選手権にも加算。
                    official = r.get("official_points", [])
                    for idx, num in enumerate(car_numbers):
                        manufacturer = wec_manufacturer_cars.get(num)
                        pt = official[idx] if idx < len(official) else 0
                        if manufacturer and pt:
                            team_points_matrix[manufacturer][race_idx] += pt
        else:
            # PDF/公式結果からドライバー情報付きで登録されたカテゴリーは、
            # 過去シーズン共通のチームマスターを0pt枠として混ぜない。
            registered = data["teams"].get(f"{r_cat}_{r_cls}", [])
            has_pdf_driver_data = any(r.get("drivers") for r in races)
            if not (r_cat in ["F1", "F2", "F3", "WEC"] and has_pdf_driver_data):
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
                    team_points_matrix[team][race_idx] += pt

        summary_list = []
        for team, pts_list in team_points_matrix.items():
            total_pt = sum(pts_list)
            summary_list.append({"チーム / 車両": team, "合計ポイント": total_pt, "pts_list": pts_list})

        summary_list.sort(key=lambda x: x["合計ポイント"], reverse=True)

        ranking_name_column = "マニュファクチャラー" if is_wec_manufacturer else "チーム / 車両"
        df_rank = pd.DataFrame([
            {
                "順位": f"P{i+1}",
                ranking_name_column: item["チーム / 車両"],
                "合計ポイント": item["合計ポイント"],
            }
            for i, item in enumerate(summary_list)
        ])

        # PDFインポートで保存されたドライバー情報から年間ランキングを集計
        driver_points = {}
        driver_teams = {}
        driver_car_numbers = {}
        has_driver_data = False
        for race_idx, race in enumerate(races):
            drivers = race.get("drivers", [])
            if drivers:
                has_driver_data = True
            pts_table = race.get("points_table", DEFAULT_PTS_RACE)
            statuses = race.get("statuses", [])
            race_teams = race.get("results", [])
            race_car_numbers = race.get("car_numbers", [])
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

                # WECは1台に2～3名のクルーが乗るため、PDFの "A / B / C" を
                # 個々のドライバーへ分割し、そのセッションで実際に登録された全員へ加点する。
                # 欠場・代役があっても、そのラウンドのPDFに載ったメンバーだけが対象になる。
                driver_names = (
                    [name.strip() for name in driver.split("/") if name.strip()]
                    if r_cat == "WEC"
                    else [driver.strip()]
                )
                for driver_name in driver_names:
                    if driver_name not in driver_points:
                        driver_points[driver_name] = [0] * len(races)
                    driver_points[driver_name][race_idx] += pt
                    if rank_idx < len(race_teams) and race_teams[rank_idx]:
                        driver_teams[driver_name] = race_teams[rank_idx]
                    if rank_idx < len(race_car_numbers) and race_car_numbers[rank_idx] not in [None, ""]:
                        driver_car_numbers[driver_name] = race_car_numbers[rank_idx]

        team_tab_label = "🏭 マニュファクチャラー" if is_wec_manufacturer else "🏎️ チーム / 車両"
        ranking_tab_team, ranking_tab_driver = st.tabs(
            [team_tab_label, "👤 ドライバー"]
        )

        with ranking_tab_team:
            if is_wec_manufacturer:
                st.subheader("🥇 マニュファクチャラーランキング")
                st.caption("WEC Hypercar公式方式：指定2台を対象に順位を詰め直して2台分を合算。Hyperpoleのポール1点も加算。")
            else:
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
                        "カーナンバー": driver_car_numbers.get(driver),
                        "チーム": driver_teams.get(driver, "-"),
                        "合計ポイント": sum(pts_list),
                        "pts_list": pts_list,
                    })
                driver_summary.sort(key=lambda x: x["合計ポイント"], reverse=True)

                df_driver_rank = pd.DataFrame([
                    {
                        "順位": f"P{i+1}",
                        "カーナンバー": f"#{item['カーナンバー']}" if item.get("カーナンバー") not in [None, ""] else "-",
                        "ドライバー": item["ドライバー"],
                        "チーム": item.get("チーム", "-"),
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
