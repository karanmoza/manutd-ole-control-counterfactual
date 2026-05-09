from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from understatapi import UnderstatClient

from config import get_project_config
from utils import ensure_directories


TEAM_NAME = "Manchester United"


def _extract_match_row(
    match: dict[str, object], shot_payload: dict[str, list[dict[str, object]]]
) -> dict[str, object]:
    """Convert an Understat match record into the project's flat match schema."""

    side = match["side"]
    home = match["h"]
    away = match["a"]
    goals = match["goals"]
    xg = match["xG"]
    venue = "H" if side == "h" else "A"
    opponent = away["title"] if side == "h" else home["title"]
    goals_for = int(goals["h"] if side == "h" else goals["a"])
    goals_against = int(goals["a"] if side == "h" else goals["h"])
    xg_for = float(xg["h"] if side == "h" else xg["a"])
    xga = float(xg["a"] if side == "h" else xg["h"])
    shots_for = len(shot_payload["h"] if side == "h" else shot_payload["a"])
    shots_against = len(shot_payload["a"] if side == "h" else shot_payload["h"])

    return {
        "date": pd.to_datetime(match["datetime"]).strftime("%Y-%m-%d"),
        "opponent": opponent,
        "venue": venue,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "xg": round(xg_for, 3),
        "xga": round(xga, 3),
        "shots_for": shots_for,
        "shots_against": shots_against,
        "competition": "Premier League",
        "manager": "",
        "notes": "Real data fetched from Understat",
    }


def fetch_understat_season(season: str) -> pd.DataFrame:
    """Fetch Manchester United league matches for a single Understat season code."""

    client = UnderstatClient()
    team = client.team(TEAM_NAME)
    matches = team.get_match_data(season=season)

    rows = []
    for match in matches:
        shot_payload = client.match(match["id"]).get_shot_data()
        rows.append(_extract_match_row(match, shot_payload))
        time.sleep(0.1)

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


def add_manager_labels_2021_22(df: pd.DataFrame) -> pd.DataFrame:
    """Assign manager labels for the 2021/22 season timeline."""

    labeled = df.copy()
    labeled["date"] = pd.to_datetime(labeled["date"])
    labeled["manager"] = "Ralf Rangnick"
    labeled.loc[labeled["date"] <= pd.Timestamp("2021-11-20"), "manager"] = "Ole Gunnar Solskjaer"
    labeled.loc[
        (labeled["date"] > pd.Timestamp("2021-11-20"))
        & (labeled["date"] < pd.Timestamp("2021-12-05")),
        "manager",
    ] = "Michael Carrick"
    labeled["notes"] = labeled["notes"].astype(str)
    return labeled


def main() -> None:
    """Fetch and save real match-level datasets for the project."""

    config = get_project_config()
    ensure_directories([config.paths.data_raw])

    df_2020_21 = fetch_understat_season("2020")
    df_2021_22_full = add_manager_labels_2021_22(fetch_understat_season("2021"))
    df_2021_22_ole = df_2021_22_full[
        df_2021_22_full["date"] <= pd.Timestamp(config.model.ole_exit_date)
    ].copy()

    df_2020_21.to_csv(config.paths.data_raw / config.baseline_filename, index=False)
    df_2021_22_full.to_csv(config.paths.data_raw / config.full_season_filename, index=False)
    df_2021_22_ole.to_csv(config.paths.data_raw / config.ole_filename, index=False)

    print("Real Understat data written to data/raw/:")
    print("-", config.paths.data_raw / config.baseline_filename)
    print("-", config.paths.data_raw / config.ole_filename)
    print("-", config.paths.data_raw / config.full_season_filename)


if __name__ == "__main__":
    main()
