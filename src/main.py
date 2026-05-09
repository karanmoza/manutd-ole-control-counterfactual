from __future__ import annotations

from analysis import run_analysis
from config import get_project_config


def main() -> None:
    """Entry point for the full project pipeline."""

    config = get_project_config()
    outputs = run_analysis(config)

    print("Project run complete.")
    print(f"Processed matches: {len(outputs['combined'])}")
    print(f"Scenario rows: {len(outputs['scenario_comparison'])}")
    print(f"Figures saved to: {config.paths.outputs_figures}")
    print(f"Tables saved to: {config.paths.outputs_tables}")


if __name__ == "__main__":
    main()

