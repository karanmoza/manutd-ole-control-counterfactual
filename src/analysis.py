from __future__ import annotations

from dataclasses import replace

import pandas as pd

from clean_data import clean_match_data
from config import ProjectConfig
from data_loader import load_match_data
from features import (
    add_match_features,
    build_period_summary,
    build_season_summary,
    build_year_over_year_comparison,
    mark_ronaldo_periods,
)
from plotting import (
    plot_actual_vs_expected_points,
    plot_defensive_fragility,
    plot_full_season_comparison,
    plot_pre_post_comparison,
    plot_rolling_xg_diff,
    plot_scenario_comparison,
    plot_sensitivity_analysis,
    plot_simulation_distribution,
    plot_year_over_year_points,
    plot_year_over_year_profile,
    set_plot_style,
)
from simulation import build_counterfactual_matches, build_simulation_outputs
from utils import ensure_directories, save_table


def run_analysis(config: ProjectConfig) -> dict[str, pd.DataFrame]:
    """Run the full analytics pipeline and save outputs."""

    ensure_directories(
        [config.paths.data_processed, config.paths.outputs_figures, config.paths.outputs_tables,]
    )

    raw_frames = load_match_data(config)
    baseline = clean_match_data(raw_frames["baseline"], "2020_21_ole_baseline")
    ole_2021_22 = clean_match_data(raw_frames["ole_2021_22"], "2021_22_to_ole_exit")
    full_2021_22 = clean_match_data(raw_frames["full_2021_22"], "2021_22_full_season")

    baseline = add_match_features(baseline, config.model)
    ole_2021_22 = add_match_features(ole_2021_22, config.model)
    full_2021_22 = add_match_features(full_2021_22, config.model)
    ole_2021_22 = mark_ronaldo_periods(ole_2021_22, config.model.ronaldo_debut_date)
    full_2021_22 = mark_ronaldo_periods(full_2021_22, config.model.ronaldo_debut_date)

    combined = pd.concat([baseline, ole_2021_22], ignore_index=True)
    season_summary = build_season_summary(combined)
    period_summary = build_period_summary(ole_2021_22)
    year_over_year = build_year_over_year_comparison(baseline, ole_2021_22, full_2021_22)
    sensitivity_configs = {
        "Mild": replace(
            config.scenario,
            attack_xg_multiplier=0.96,
            attack_shots_multiplier=0.98,
            control_xg_bonus=0.03,
            defensive_xga_multiplier=0.92,
            defensive_shots_against_multiplier=0.95,
            shot_suppression_xga_bonus=0.008,
        ),
        "Base": config.scenario,
        "Strong": replace(
            config.scenario,
            attack_xg_multiplier=0.95,
            attack_shots_multiplier=0.97,
            control_xg_bonus=0.07,
            defensive_xga_multiplier=0.82,
            defensive_shots_against_multiplier=0.86,
            shot_suppression_xga_bonus=0.016,
        ),
    }

    counterfactual = build_counterfactual_matches(
        ole_2021_22, config, scenario_name="counterfactual_cdm"
    )
    casemiro_counterfactual = build_counterfactual_matches(
        ole_2021_22, config, scenario_name="casemiro_counterfactual"
    )
    match_probability_table, scenario_summary, distributions = build_simulation_outputs(
        actual_df=ole_2021_22,
        scenario_dfs={
            "counterfactual_cdm": counterfactual,
            "casemiro_counterfactual": casemiro_counterfactual,
        },
        config=config,
    )
    full_counterfactual = build_counterfactual_matches(
        full_2021_22, config, scenario_name="counterfactual_cdm"
    )
    full_casemiro_counterfactual = build_counterfactual_matches(
        full_2021_22, config, scenario_name="casemiro_counterfactual"
    )
    (
        full_match_probability_table,
        full_scenario_summary,
        full_distributions,
    ) = build_simulation_outputs(
        actual_df=full_2021_22,
        scenario_dfs={
            "counterfactual_cdm": full_counterfactual,
            "casemiro_counterfactual": full_casemiro_counterfactual,
        },
        config=config,
    )

    scenario_assumptions = pd.DataFrame(
        [
            {
                "assumption": "attack_xg_multiplier",
                "value": config.scenario.attack_xg_multiplier,
                "interpretation": "Slight reduction in attacking output without Ronaldo",
            },
            {
                "assumption": "control_xg_bonus",
                "value": config.scenario.control_xg_bonus,
                "interpretation": "Small control-driven attack compensation from better midfield balance",
            },
            {
                "assumption": "defensive_xga_multiplier",
                "value": config.scenario.defensive_xga_multiplier,
                "interpretation": "Improved defensive stability with a strong defensive midfielder",
            },
            {
                "assumption": "defensive_shots_against_multiplier",
                "value": config.scenario.defensive_shots_against_multiplier,
                "interpretation": "Fewer shots conceded under the counterfactual build",
            },
            {
                "assumption": "shot_suppression_xga_bonus",
                "value": config.scenario.shot_suppression_xga_bonus,
                "interpretation": "Extra xGA reduction tied to shot suppression",
            },
            {
                "assumption": "casemiro_defensive_xga_multiplier",
                "value": config.scenario.casemiro_defensive_xga_multiplier,
                "interpretation": "Stronger defensive improvement for the Casemiro-specific scenario",
            },
            {
                "assumption": "casemiro_control_xg_bonus",
                "value": config.scenario.casemiro_control_xg_bonus,
                "interpretation": "Slightly larger control bonus for a named elite ball-winning midfielder",
            },
        ]
    )

    scenario_comparison = scenario_summary.copy()
    actual_mean = scenario_comparison.loc[
        scenario_comparison["scenario"] == "actual_profile", "mean_points"
    ].iloc[0]
    scenario_comparison["delta_vs_actual"] = (
        scenario_comparison["mean_points"] - actual_mean
    ).round(2)
    full_actual_mean = full_scenario_summary.loc[
        full_scenario_summary["scenario"] == "actual_profile", "mean_points"
    ].iloc[0]
    full_scenario_comparison = full_scenario_summary.copy()
    full_scenario_comparison["delta_vs_actual"] = (
        full_scenario_comparison["mean_points"] - full_actual_mean
    ).round(2)
    actual_full_points = int(full_2021_22["points"].sum())
    full_season_points_comparison = pd.DataFrame(
        [
            {
                "scenario": "actual_2021_22_points",
                "points": actual_full_points,
                "label": "Observed Manchester United league points",
            },
            {
                "scenario": "counterfactual_cdm_mean",
                "points": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "counterfactual_cdm", "mean_points",
                    ].iloc[0],
                    2,
                ),
                "label": "Mean simulated points with a CDM profile instead of Ronaldo",
            },
            {
                "scenario": "casemiro_counterfactual_mean",
                "points": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "casemiro_counterfactual",
                        "mean_points",
                    ].iloc[0],
                    2,
                ),
                "label": "Mean simulated points with a Casemiro-style signing instead of Ronaldo",
            },
        ]
    )
    sensitivity_rows = [
        {
            "sensitivity_case": "Observed",
            "scenario_type": "Observed actual",
            "mean_points": round(float(actual_full_points), 2),
            "delta_vs_actual": 0.0,
            "actual_points": float(actual_full_points),
            "attack_xg_multiplier": "",
            "control_xg_bonus": "",
            "defensive_xga_multiplier": "",
            "defensive_shots_against_multiplier": "",
            "shot_suppression_xga_bonus": "",
        }
    ]
    for label, scenario_params in sensitivity_configs.items():
        scenario_config = replace(config, scenario=scenario_params)
        cf_full = build_counterfactual_matches(
            full_2021_22, scenario_config, scenario_name="counterfactual_cdm"
        )
        _, sensitivity_summary, _ = build_simulation_outputs(
            actual_df=full_2021_22,
            scenario_dfs={"counterfactual_cdm": cf_full},
            config=scenario_config,
        )
        mean_points = float(
            sensitivity_summary.loc[
                sensitivity_summary["scenario"] == "counterfactual_cdm", "mean_points",
            ].iloc[0]
        )
        sensitivity_rows.append(
            {
                "sensitivity_case": label,
                "scenario_type": "Generic CDM",
                "mean_points": round(mean_points, 2),
                "delta_vs_actual": round(mean_points - actual_full_points, 2),
                "actual_points": float(actual_full_points),
                "attack_xg_multiplier": scenario_params.attack_xg_multiplier,
                "control_xg_bonus": scenario_params.control_xg_bonus,
                "defensive_xga_multiplier": scenario_params.defensive_xga_multiplier,
                "defensive_shots_against_multiplier": scenario_params.defensive_shots_against_multiplier,
                "shot_suppression_xga_bonus": scenario_params.shot_suppression_xga_bonus,
            }
        )
    sensitivity_analysis = pd.DataFrame(sensitivity_rows)
    executive_summary = pd.DataFrame(
        [
            {
                "question": "2020/21 baseline points per match",
                "actual_observed_or_profile": round(float(baseline["points"].mean()), 2),
                "counterfactual_cdm_mean": "",
                "difference": "",
            },
            {
                "question": "2021/22 points per match to Ole exit",
                "actual_observed_or_profile": round(float(ole_2021_22["points"].mean()), 2),
                "counterfactual_cdm_mean": "",
                "difference": round(
                    float(ole_2021_22["points"].mean() - baseline["points"].mean()), 2
                ),
            },
            {
                "question": "Points to Ole exit",
                "actual_observed_or_profile": round(float(ole_2021_22["points"].sum()), 2),
                "counterfactual_cdm_mean": round(
                    scenario_summary.loc[
                        scenario_summary["scenario"] == "counterfactual_cdm", "mean_points",
                    ].iloc[0],
                    2,
                ),
                "difference": round(
                    scenario_summary.loc[
                        scenario_summary["scenario"] == "counterfactual_cdm", "mean_points",
                    ].iloc[0]
                    - float(ole_2021_22["points"].sum()),
                    2,
                ),
            },
            {
                "question": "Points to Ole exit (Casemiro scenario)",
                "actual_observed_or_profile": round(float(ole_2021_22["points"].sum()), 2),
                "counterfactual_cdm_mean": round(
                    scenario_summary.loc[
                        scenario_summary["scenario"] == "casemiro_counterfactual", "mean_points",
                    ].iloc[0],
                    2,
                ),
                "difference": round(
                    scenario_summary.loc[
                        scenario_summary["scenario"] == "casemiro_counterfactual", "mean_points",
                    ].iloc[0]
                    - float(ole_2021_22["points"].sum()),
                    2,
                ),
            },
            {
                "question": "Points over full 2021/22 season",
                "actual_observed_or_profile": float(actual_full_points),
                "counterfactual_cdm_mean": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "counterfactual_cdm", "mean_points",
                    ].iloc[0],
                    2,
                ),
                "difference": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "counterfactual_cdm", "mean_points",
                    ].iloc[0]
                    - float(actual_full_points),
                    2,
                ),
            },
            {
                "question": "Points over full 2021/22 season (Casemiro scenario)",
                "actual_observed_or_profile": float(actual_full_points),
                "counterfactual_cdm_mean": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "casemiro_counterfactual",
                        "mean_points",
                    ].iloc[0],
                    2,
                ),
                "difference": round(
                    full_scenario_summary.loc[
                        full_scenario_summary["scenario"] == "casemiro_counterfactual",
                        "mean_points",
                    ].iloc[0]
                    - float(actual_full_points),
                    2,
                ),
            },
            {
                "question": "Sensitivity range for generic CDM full-season uplift",
                "actual_observed_or_profile": float(actual_full_points),
                "counterfactual_cdm_mean": (
                    f"{sensitivity_analysis.loc[sensitivity_analysis['scenario_type'] == 'Generic CDM', 'mean_points'].min():.2f} "
                    f"to {sensitivity_analysis.loc[sensitivity_analysis['scenario_type'] == 'Generic CDM', 'mean_points'].max():.2f}"
                ),
                "difference": (
                    f"{sensitivity_analysis.loc[sensitivity_analysis['scenario_type'] == 'Generic CDM', 'delta_vs_actual'].min():.2f} "
                    f"to {sensitivity_analysis.loc[sensitivity_analysis['scenario_type'] == 'Generic CDM', 'delta_vs_actual'].max():.2f}"
                ),
            },
        ]
    )

    save_table(combined, config.paths.data_processed / "combined_matches.csv")
    save_table(counterfactual, config.paths.data_processed / "counterfactual_matches.csv")
    save_table(full_2021_22, config.paths.data_processed / "full_2021_22_matches.csv")
    save_table(
        full_counterfactual,
        config.paths.data_processed / "full_2021_22_counterfactual_matches.csv",
    )
    save_table(
        casemiro_counterfactual,
        config.paths.data_processed / "casemiro_counterfactual_matches.csv",
    )
    save_table(
        full_casemiro_counterfactual,
        config.paths.data_processed / "full_2021_22_casemiro_counterfactual_matches.csv",
    )
    save_table(season_summary, config.paths.outputs_tables / "season_summary.csv")
    save_table(period_summary, config.paths.outputs_tables / "pre_post_ronaldo_summary.csv")
    save_table(year_over_year, config.paths.outputs_tables / "year_over_year_comparison.csv")
    save_table(scenario_assumptions, config.paths.outputs_tables / "scenario_assumptions.csv")
    save_table(
        match_probability_table, config.paths.outputs_tables / "match_simulation_probabilities.csv"
    )
    save_table(scenario_summary, config.paths.outputs_tables / "simulation_summary.csv")
    save_table(scenario_comparison, config.paths.outputs_tables / "scenario_comparison.csv")
    save_table(distributions, config.paths.outputs_tables / "simulation_distributions.csv")
    save_table(
        full_match_probability_table,
        config.paths.outputs_tables / "full_season_match_simulation_probabilities.csv",
    )
    save_table(
        full_scenario_summary, config.paths.outputs_tables / "full_season_simulation_summary.csv",
    )
    save_table(
        full_scenario_comparison,
        config.paths.outputs_tables / "full_season_scenario_comparison.csv",
    )
    save_table(
        full_distributions,
        config.paths.outputs_tables / "full_season_simulation_distributions.csv",
    )
    save_table(
        full_season_points_comparison,
        config.paths.outputs_tables / "full_season_points_comparison.csv",
    )
    save_table(
        sensitivity_analysis, config.paths.outputs_tables / "sensitivity_analysis.csv",
    )
    save_table(
        executive_summary, config.paths.outputs_tables / "executive_summary.csv",
    )

    set_plot_style()
    plot_rolling_xg_diff(combined, config.paths.outputs_figures / "rolling_xg_difference.png")
    plot_defensive_fragility(
        ole_2021_22, config.paths.outputs_figures / "defensive_fragility_trend.png"
    )
    plot_actual_vs_expected_points(
        ole_2021_22, config.paths.outputs_figures / "actual_vs_expected_points.png"
    )
    plot_pre_post_comparison(
        period_summary, config.paths.outputs_figures / "pre_post_ronaldo_profile.png"
    )
    plot_year_over_year_points(
        year_over_year, config.paths.outputs_figures / "year_over_year_points.png"
    )
    plot_year_over_year_profile(
        year_over_year, config.paths.outputs_figures / "year_over_year_profile.png"
    )
    plot_scenario_comparison(
        scenario_summary, config.paths.outputs_figures / "scenario_comparison.png"
    )
    plot_simulation_distribution(
        distributions, config.paths.outputs_figures / "simulation_distribution.png"
    )
    plot_full_season_comparison(
        full_season_points_comparison,
        config.paths.outputs_figures / "full_season_points_comparison.png",
    )
    plot_scenario_comparison(
        full_scenario_summary, config.paths.outputs_figures / "full_season_scenario_comparison.png",
    )
    plot_simulation_distribution(
        full_distributions,
        config.paths.outputs_figures / "full_season_simulation_distribution.png",
    )
    plot_sensitivity_analysis(
        sensitivity_analysis, config.paths.outputs_figures / "sensitivity_analysis.png",
    )

    return {
        "baseline": baseline,
        "ole_2021_22": ole_2021_22,
        "full_2021_22": full_2021_22,
        "combined": combined,
        "counterfactual": counterfactual,
        "casemiro_counterfactual": casemiro_counterfactual,
        "full_counterfactual": full_counterfactual,
        "full_casemiro_counterfactual": full_casemiro_counterfactual,
        "season_summary": season_summary,
        "period_summary": period_summary,
        "year_over_year": year_over_year,
        "scenario_summary": scenario_summary,
        "scenario_comparison": scenario_comparison,
        "match_probability_table": match_probability_table,
        "distributions": distributions,
        "full_scenario_summary": full_scenario_summary,
        "full_scenario_comparison": full_scenario_comparison,
        "full_season_points_comparison": full_season_points_comparison,
        "sensitivity_analysis": sensitivity_analysis,
        "executive_summary": executive_summary,
    }
