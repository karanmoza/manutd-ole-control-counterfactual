from __future__ import annotations

import pandas as pd


COLUMN_ALIASES = {
    "comp": "competition",
    "squad": "team",
    "home_away": "venue",
    "home/away": "venue",
    "venue": "venue",
    "opp": "opponent",
    "opponent": "opponent",
    "date": "date",
    "match report": "match_report",
    "day": "match_day",
    "round": "round",
    "result": "result_raw",
    "home_away": "venue",
    "gf": "goals_for",
    "ga": "goals_against",
    "goals for": "goals_for",
    "goals against": "goals_against",
    "xgf": "xg",
    "xg": "xg",
    "xga": "xga",
    "xga_against": "xga",
    "sh": "shots_for",
    "shots": "shots_for",
    "shots for": "shots_for",
    "opp_shots": "shots_against",
    "shots_allowed": "shots_against",
    "shots against": "shots_against",
}

REQUIRED_COLUMNS_AFTER_STANDARDIZATION = [
    "date",
    "opponent",
    "venue",
    "goals_for",
    "goals_against",
    "xg",
    "xga",
    "shots_for",
]


def standardize_match_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize raw column names to the project schema."""

    clean = df.copy()
    clean.columns = [column.strip().lower() for column in clean.columns]
    clean = clean.rename(columns=COLUMN_ALIASES)
    return clean


def _normalize_fbref_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop repeated header rows and obvious non-match rows from FBref-style exports."""

    clean = df.copy()
    if "date" in clean.columns:
        clean = clean[clean["date"].astype(str).str.lower() != "date"]
    if "opponent" in clean.columns:
        clean = clean[clean["opponent"].astype(str).str.lower() != "opponent"]
    clean = clean.dropna(how="all")
    return clean.reset_index(drop=True)


def validate_standardized_columns(df: pd.DataFrame, season_label: str) -> None:
    """Validate required columns after alias mapping rather than before it."""

    missing = [column for column in REQUIRED_COLUMNS_AFTER_STANDARDIZATION if column not in df.columns]
    if missing:
        raise ValueError(
            f"Season {season_label} is missing required columns after standardization: {missing}. "
            "FBref-style files are supported, but they still need date/opponent/venue/GF/GA/xG/xGA/Sh."
        )


def _infer_shots_against(df: pd.DataFrame) -> pd.DataFrame:
    """Infer shots against when the raw source has xGA but no opponent shot totals.

    FBref team schedule exports often include xGA but not always opponent shots.
    For a practical first-pass model, we use xGA as a stable defensive proxy and
    back out a rough shot volume estimate so downstream descriptive charts still work.
    """

    clean = df.copy()
    if "shots_against" not in clean.columns:
        clean["shots_against"] = (clean["xga"] * 8.0).round().clip(lower=1)
        clean["notes"] = clean.get("notes", "").fillna("")
        clean["notes"] = clean["notes"].astype(str).str.strip()
        clean["notes"] = clean["notes"].where(
            clean["notes"] == "",
            clean["notes"] + " | shots_against imputed from xGA",
        )
        clean["notes"] = clean["notes"].mask(
            clean["notes"] == "",
            "shots_against imputed from xGA",
        )
    return clean


def clean_match_data(df: pd.DataFrame, season_label: str) -> pd.DataFrame:
    """Clean a single season dataframe and add stable helper columns."""

    clean = standardize_match_columns(df)
    clean = _normalize_fbref_rows(clean)
    validate_standardized_columns(clean, season_label)

    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    if clean["date"].isna().any():
        raise ValueError(f"Season {season_label} has invalid date values.")

    clean = _infer_shots_against(clean)

    numeric_columns = [
        "goals_for",
        "goals_against",
        "xg",
        "xga",
        "shots_for",
        "shots_against",
    ]
    for column in numeric_columns:
        clean[column] = pd.to_numeric(clean[column], errors="coerce")

    missing_numeric = clean[numeric_columns].isna().sum()
    if (missing_numeric > 0).any():
        bad_cols = missing_numeric[missing_numeric > 0].to_dict()
        raise ValueError(
            f"Season {season_label} has missing numeric values after cleaning: {bad_cols}"
        )

    clean["venue"] = clean["venue"].astype(str).str.upper().str[0]
    if "competition" not in clean.columns:
        clean["competition"] = "Premier League"
    else:
        clean["competition"] = clean["competition"].fillna("Premier League")

    if "manager" not in clean.columns:
        clean["manager"] = "Ole Gunnar Solskjaer"
    else:
        clean["manager"] = clean["manager"].fillna("Ole Gunnar Solskjaer")

    if "notes" not in clean.columns:
        clean["notes"] = ""
    else:
        clean["notes"] = clean["notes"].fillna("")
    clean["venue"] = clean["venue"].replace({"Home": "H", "Away": "A", "home": "H", "away": "A"})
    clean["season"] = season_label
    clean = clean.sort_values("date").reset_index(drop=True)

    return clean
