from __future__ import annotations

import numpy as np
import pandas as pd

from config import ProjectConfig
from features import expected_points_from_rates


def build_counterfactual_matches(
    actual_df: pd.DataFrame, config: ProjectConfig, scenario_name: str = "counterfactual_cdm",
) -> pd.DataFrame:
    """Apply scenario assumptions to create a counterfactual 2021/22 match profile."""

    scenario = config.scenario
    counterfactual = actual_df.copy()
    counterfactual["scenario"] = scenario_name

    if scenario_name == "casemiro_counterfactual":
        attack_xg_multiplier = scenario.casemiro_attack_xg_multiplier
        attack_shots_multiplier = scenario.casemiro_attack_shots_multiplier
        control_xg_bonus = scenario.casemiro_control_xg_bonus
        defensive_xga_multiplier = scenario.casemiro_defensive_xga_multiplier
        defensive_shots_against_multiplier = scenario.casemiro_defensive_shots_against_multiplier
        shot_suppression_xga_bonus = scenario.casemiro_shot_suppression_xga_bonus
    else:
        attack_xg_multiplier = scenario.attack_xg_multiplier
        attack_shots_multiplier = scenario.attack_shots_multiplier
        control_xg_bonus = scenario.control_xg_bonus
        defensive_xga_multiplier = scenario.defensive_xga_multiplier
        defensive_shots_against_multiplier = scenario.defensive_shots_against_multiplier
        shot_suppression_xga_bonus = scenario.shot_suppression_xga_bonus

    counterfactual["cf_shots_for"] = (counterfactual["shots_for"] * attack_shots_multiplier).round(
        2
    )
    counterfactual["cf_shots_against"] = (
        counterfactual["shots_against"] * defensive_shots_against_multiplier
    ).round(2)
    counterfactual["cf_xg"] = np.maximum(
        scenario.minimum_xg_floor, counterfactual["xg"] * attack_xg_multiplier + control_xg_bonus,
    ).round(3)
    counterfactual["cf_xga"] = np.maximum(
        scenario.minimum_xga_floor,
        counterfactual["xga"] * defensive_xga_multiplier
        - (counterfactual["shots_against"] * shot_suppression_xga_bonus),
    ).round(3)
    counterfactual["cf_expected_points"] = [
        expected_points_from_rates(xg_for, xg_against, config.model.max_goals)
        for xg_for, xg_against in zip(counterfactual["cf_xg"], counterfactual["cf_xga"])
    ]
    return counterfactual


def simulate_match_probabilities(
    xg_for: float, xg_against: float, draws: int, rng: np.random.Generator,
) -> tuple[float, float, float, float]:
    """Simulate a single match many times and return win/draw/loss probabilities and mean points."""

    gf = rng.poisson(lam=xg_for, size=draws)
    ga = rng.poisson(lam=xg_against, size=draws)
    wins = (gf > ga).mean()
    draws_pct = (gf == ga).mean()
    losses = (gf < ga).mean()
    points = 3 * wins + draws_pct
    return wins, draws_pct, losses, points


def simulate_season_points(
    df: pd.DataFrame, xg_for_col: str, xg_against_col: str, draws: int, seed: int = 7,
) -> np.ndarray:
    """Simulate total points across a sequence of matches."""

    rng = np.random.default_rng(seed)
    total_points = np.zeros(draws)
    for _, row in df.iterrows():
        gf = rng.poisson(lam=row[xg_for_col], size=draws)
        ga = rng.poisson(lam=row[xg_against_col], size=draws)
        total_points += np.where(gf > ga, 3, np.where(gf == ga, 1, 0))
    return total_points


def build_simulation_outputs(
    actual_df: pd.DataFrame, scenario_dfs: dict[str, pd.DataFrame], config: ProjectConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create match-level probabilities, scenario summary, and simulation distributions."""

    rng = np.random.default_rng(11)
    match_rows: list[dict[str, object]] = []
    for _, row in actual_df.iterrows():
        actual_probs = simulate_match_probabilities(
            row["xg"], row["xga"], config.model.simulation_draws, rng
        )
        match_rows.append(
            {
                "date": row["date"],
                "opponent": row["opponent"],
                "scenario": "actual_profile",
                "win_probability": round(actual_probs[0], 4),
                "draw_probability": round(actual_probs[1], 4),
                "loss_probability": round(actual_probs[2], 4),
                "expected_points": round(actual_probs[3], 4),
            }
        )
        for scenario_name, scenario_df in scenario_dfs.items():
            cf_row = scenario_df.loc[scenario_df["date"] == row["date"]].iloc[0]
            cf_probs = simulate_match_probabilities(
                cf_row["cf_xg"], cf_row["cf_xga"], config.model.simulation_draws, rng,
            )
            match_rows.append(
                {
                    "date": row["date"],
                    "opponent": row["opponent"],
                    "scenario": scenario_name,
                    "win_probability": round(cf_probs[0], 4),
                    "draw_probability": round(cf_probs[1], 4),
                    "loss_probability": round(cf_probs[2], 4),
                    "expected_points": round(cf_probs[3], 4),
                }
            )

    match_probability_table = pd.DataFrame(match_rows)

    distributions = {
        "actual_profile": simulate_season_points(
            actual_df,
            xg_for_col="xg",
            xg_against_col="xga",
            draws=config.model.simulation_draws,
            seed=21,
        )
    }
    for idx, (scenario_name, scenario_df) in enumerate(scenario_dfs.items(), start=22):
        distributions[scenario_name] = simulate_season_points(
            scenario_df,
            xg_for_col="cf_xg",
            xg_against_col="cf_xga",
            draws=config.model.simulation_draws,
            seed=idx,
        )

    distribution_table = pd.DataFrame(distributions)

    summary_rows = []
    for label, distribution in distributions.items():
        summary_rows.append(
            {
                "scenario": label,
                "mean_points": round(distribution.mean(), 2),
                "median_points": round(float(np.median(distribution)), 2),
                "p10_points": round(float(np.percentile(distribution, 10)), 2),
                "p90_points": round(float(np.percentile(distribution, 90)), 2),
                "std_points": round(float(distribution.std()), 2),
            }
        )

    scenario_summary = pd.DataFrame(summary_rows)
    return match_probability_table, scenario_summary, distribution_table
