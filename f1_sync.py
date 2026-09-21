import json
from urllib.request import Request, urlopen

API_BASE = "https://api.jolpi.ca/ergast/f1"

TEAM_NAMES = {
    "red_bull": "Oracle Red Bull Racing",
    "mercedes": "Mercedes-AMG PETRONAS F1 Team",
    "ferrari": "Scuderia Ferrari HP",
    "mclaren": "McLaren Formula 1 Team",
    "aston_martin": "Aston Martin Aramco F1 Team",
    "alpine": "BWT Alpine F1 Team",
    "williams": "Williams Racing",
    "rb": "Visa Cash App RB F1 Team",
    "haas": "MoneyGram Haas F1 Team",
    "sauber": "Stake F1 Team Kick Sauber",
    "cadillac": "Cadillac Formula 1 Team",
}


def _get_json(path):
    request = Request(
        f"{API_BASE}/{path.lstrip('/')}.json",
        headers={"User-Agent": "motorsport-app/1.0"},
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _race_list(payload):
    return payload.get("MRData", {}).get("RaceTable", {}).get("Races", [])


def _result_rows(race, result_key):
    return race.get("Results", []) if result_key == "Results" else race.get(result_key, [])


def fetch_f1_season(season):
    """Return F1 race, qualifying and sprint sessions in the app's simple format."""
    schedule_payload = _get_json(f"{season}")
    races = _race_list(schedule_payload)
    imported = []

    for race in races:
        round_no = race.get("round", "")
        race_name = race.get("raceName", f"Round {round_no}")
        race_date = race.get("date", "")

        endpoints = [
            ("決勝", f"{season}/{round_no}/results", "Results"),
            ("予選", f"{season}/{round_no}/qualifying", "QualifyingResults"),
            ("スプリント", f"{season}/{round_no}/sprint", "SprintResults"),
        ]

        for session_type, path, result_key in endpoints:
            session_races = _race_list(_get_json(path))
            if not session_races:
                continue

            rows = _result_rows(session_races[0], result_key)
            if not rows:
                continue

            results = []
            for row in rows:
                constructor = row.get("Constructor", {}).get("constructorId", "")
                team_name = TEAM_NAMES.get(constructor, constructor)
                if team_name:
                    results.append(team_name)

            if results:
                imported.append({
                    "round_name": f"Rd.{round_no} {race_name}",
                    "race_date": race_date,
                    "session_type": session_type,
                    "is_custom_pts": False,
                    "results": results,
                    "source": "Jolpica F1 API",
                })

    return imported


def merge_f1_results(data, season, imported):
    """Merge imported sessions without creating duplicates."""
    year_key = f"{season}年"
    data.setdefault("races", {}).setdefault(year_key, {}).setdefault("F1", {}).setdefault("総合", [])
    target = data["races"][year_key]["F1"]["総合"]
    existing_keys = {
        (item.get("round_name"), item.get("session_type", "決勝"))
        for item in target
    }

    added = 0
    for item in imported:
        key = (item.get("round_name"), item.get("session_type", "決勝"))
        if key in existing_keys:
            continue
        item["points_table"] = []
        target.append(item)
        existing_keys.add(key)
        added += 1

    return added
