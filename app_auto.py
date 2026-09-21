import json
import os
import streamlit as st

from f1_sync import fetch_f1_season, merge_f1_results

DATA_FILE = "race_data_v12.json"


def load_sync_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {"races": {}, "teams": {}, "points_master": {}}


def save_sync_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


@st.cache_data(ttl=900, show_spinner=False)
def sync_f1():
    season = 2026
    data = load_sync_data()
    imported = fetch_f1_season(season)
    added = merge_f1_results(data, season, imported)
    if added > 0:
        save_sync_data(data)
    return added, len(imported)


try:
    added_count, fetched_count = sync_f1()
    if added_count > 0:
        st.toast(f"F1の新しいセッションを{added_count}件追加しました")
except Exception as error:
    st.warning(f"F1の自動取得をスキップしました。既存データはそのまま表示します。\n\n詳細: {error}")

# 既存の画面をそのまま利用する
import app  # noqa: E402,F401
