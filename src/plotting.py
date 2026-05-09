from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

RED = "#9f1d20"
SALMON = "#d86a6d"
NAVY = "#16324f"
GRAY = "#5b6573"
LIGHT = "#f5f1eb"
GREEN = "#2e8b57"
GOLD = "#b88a1b"


def set_plot_style() -> None:
    """Apply a clean, publication-friendly plotting style."""

    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (12.5, 6.5),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.titlesize": 18,
            "axes.labelsize": 12,
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "grid.color": "#d9dee5",
            "grid.alpha": 0.5,
            "font.family": "DejaVu Sans",
        }
    )


def plot_rolling_xg_diff(
    matches: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot rolling xG difference by season."""

    fig, ax = plt.subplots()
    sns.lineplot(
        data=matches,
        x="match_number",
        y="rolling_xg_diff",
        hue="season",
        marker="o",
        palette=[NAVY, RED],
        linewidth=2.5,
        ax=ax,
    )
    ax.axhline(0, color=GRAY, linestyle="--", linewidth=1)
    ax.set_title("Rolling xG Difference", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "United's underlying control worsened from the 2020/21 baseline into the 2021/22 start.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("Match Number")
    ax.set_ylabel("Rolling xG Difference")
    ax.legend(title="")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_defensive_fragility(
    df_2021_22: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot rolling xGA and rolling shots against together."""

    fig, ax = plt.subplots()
    ax.plot(
        df_2021_22["match_number"],
        df_2021_22["rolling_xga"],
        color=RED,
        marker="o",
        linewidth=2.5,
        label="Rolling xGA",
    )
    ax.plot(
        df_2021_22["match_number"],
        df_2021_22["rolling_shots_against"],
        color=NAVY,
        marker="s",
        linewidth=2.3,
        label="Rolling shots against",
    )
    ax.set_title("Defensive Fragility Trend in 2021/22", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "The team became easier to attack: higher chance quality and more pressure conceded.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("Match Number")
    ax.set_ylabel("Rolling defensive pressure")
    ax.legend()
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_actual_vs_expected_points(
    df_2021_22: pd.DataFrame,
    output_path: Path,
) -> None:
    """Compare cumulative actual points and cumulative expected points."""

    fig, ax = plt.subplots()
    ax.plot(
        df_2021_22["match_number"],
        df_2021_22["cum_points"],
        color=RED,
        marker="o",
        linewidth=2.5,
        label="Actual points",
    )
    ax.plot(
        df_2021_22["match_number"],
        df_2021_22["cum_expected_points"],
        color=NAVY,
        marker="o",
        linestyle="--",
        linewidth=2.3,
        label="Expected points from xG/xGA",
    )
    ax.set_title("Actual Points vs Expected Points", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "Compares observed results with the underlying xG-based process up to Ole's exit.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("Match Number")
    ax.set_ylabel("Cumulative points")
    ax.legend()
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_pre_post_comparison(
    period_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot pre/post Ronaldo comparison across core averages."""

    metrics = ["goals_for", "goals_against", "xg", "xga", "shots_against"]
    plot_df = period_summary.melt(
        id_vars="ronaldo_period", value_vars=metrics, var_name="metric", value_name="value"
    )
    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(
        data=plot_df,
        x="metric",
        y="value",
        hue="ronaldo_period",
        palette=[NAVY, RED],
        ax=ax,
    )
    ax.set_title("Pre vs Post Ronaldo Team Profile", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "Attack stayed dangerous at times, but defensive exposure and loss of control increased.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Average per match")
    ax.legend(title="")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def _annotate_bar_values(ax: plt.Axes, fmt: str = "{:.2f}") -> None:
    """Annotate bars with their heights."""

    for patch in ax.patches:
        height = patch.get_height()
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            height + 0.15,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=10,
            color=GRAY,
        )


def plot_scenario_comparison(
    scenario_summary: pd.DataFrame,
    output_path: Path,
    title: str = "Scenario Comparison: Simulated Points to Ole's Exit",
    subtitle: str = "The counterfactual asks whether greater midfield control outperforms the observed squad build.",
) -> None:
    """Plot mean simulated points by scenario."""

    fig, ax = plt.subplots()
    sns.barplot(
        data=scenario_summary,
        x="scenario",
        y="mean_points",
        palette=[GRAY, RED, GOLD],
        ax=ax,
    )
    _annotate_bar_values(ax)
    ax.set_title(title, loc="left", pad=28)
    ax.text(
        0,
        1.01,
        subtitle,
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Mean simulated points")
    label_map = {
        "actual_profile": "Actual profile",
        "counterfactual_cdm": "Generic CDM",
        "casemiro_counterfactual": "Casemiro",
    }
    ax.set_xticklabels([label_map.get(text.get_text(), text.get_text()) for text in ax.get_xticklabels()])
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_simulation_distribution(
    distributions: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot overlapping distributions of simulated points."""

    fig, ax = plt.subplots()
    sns.kdeplot(
        distributions["actual_profile"],
        fill=True,
        color=GRAY,
        alpha=0.35,
        label="Actual profile",
        ax=ax,
    )
    sns.kdeplot(
        distributions["counterfactual_cdm"],
        fill=True,
        color=RED,
        alpha=0.35,
        label="Counterfactual CDM",
        ax=ax,
    )
    if "casemiro_counterfactual" in distributions.columns:
        sns.kdeplot(
            distributions["casemiro_counterfactual"],
            fill=True,
            color=GOLD,
            alpha=0.30,
            label="Casemiro",
            ax=ax,
        )
    ax.set_title("Simulation Distribution of League Points", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "The full distribution matters: the CDM scenario shifts the expected range, not just the average.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("Simulated points")
    ax.set_ylabel("Density")
    ax.legend()
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_full_season_comparison(
    comparison_table: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot actual full-season points against the counterfactual mean."""

    fig, ax = plt.subplots()
    sns.barplot(
        data=comparison_table,
        x="scenario",
        y="points",
        palette=[GRAY, RED, GOLD],
        ax=ax,
    )
    _annotate_bar_values(ax)
    ax.set_title("Full 2021/22 Points: Actual vs CDM Counterfactual", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "The model suggests an improvement, but not a complete transformation of the season.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Points")
    label_map = {
        "actual_2021_22_points": "Actual 2021/22",
        "counterfactual_cdm_mean": "Generic CDM",
        "casemiro_counterfactual_mean": "Casemiro",
    }
    ax.set_xticklabels([label_map.get(text.get_text(), text.get_text()) for text in ax.get_xticklabels()])
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_year_over_year_points(
    yoy_table: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot points per match across baseline, Ole exit window, and full season."""

    fig, ax = plt.subplots()
    sns.barplot(
        data=yoy_table,
        x="window",
        y="points_per_match",
        palette=[NAVY, RED, SALMON],
        ax=ax,
    )
    _annotate_bar_values(ax)
    ax.set_title("United's Points Profile Worsened Sharply After 2020/21", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "The decline appears both in the Ole stretch and in the final full-season outcome.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Points per match")
    ax.set_xticklabels(["2020/21 baseline", "2021/22 to Ole exit", "2021/22 full season"])
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_year_over_year_profile(
    yoy_table: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot key year-over-year profile metrics."""

    metrics = ["xg_per_match", "xga_per_match", "shots_against_per_match"]
    plot_df = yoy_table.melt(
        id_vars="window",
        value_vars=metrics,
        var_name="metric",
        value_name="value",
    )
    metric_labels = {
        "xg_per_match": "xG per match",
        "xga_per_match": "xGA per match",
        "shots_against_per_match": "Shots against per match",
    }
    plot_df["metric"] = plot_df["metric"].map(metric_labels)

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.barplot(
        data=plot_df,
        x="metric",
        y="value",
        hue="window",
        palette=[NAVY, RED, SALMON],
        ax=ax,
    )
    ax.set_title("The 2021/22 Drop-Off Was More Than A Results Swing", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "Chance prevention and overall control deteriorated materially relative to the previous year.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Average per match")
    ax.legend(title="")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def plot_sensitivity_analysis(
    sensitivity_table: pd.DataFrame,
    output_path: Path,
) -> None:
    """Plot full-season points across sensitivity cases."""

    plot_df = sensitivity_table.copy()
    plot_df["label"] = plot_df["sensitivity_case"] + " (" + plot_df["scenario_type"] + ")"

    fig, ax = plt.subplots(figsize=(13, 6.5))
    sns.barplot(
        data=plot_df,
        x="label",
        y="mean_points",
        palette=[NAVY, RED, GOLD, SALMON],
        ax=ax,
    )
    _annotate_bar_values(ax)
    actual_points = float(
        plot_df.loc[plot_df["scenario_type"] == "Observed actual", "actual_points"].iloc[0]
    )
    ax.axhline(actual_points, color=GRAY, linestyle="--", linewidth=1.5)
    ax.set_title("Sensitivity Check: The Conclusion Survives More Than One Assumption Set", loc="left", pad=28)
    ax.text(
        0,
        1.01,
        "Even under milder assumptions, the model still points toward a more useful midfield-oriented squad build.",
        transform=ax.transAxes,
        fontsize=10,
        color=GRAY,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Full-season mean points")
    ax.set_xticklabels(
        ["Actual", "Mild CDM", "Base CDM", "Strong CDM"],
        rotation=0,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
