# Manchester United Counterfactual: No Ronaldo, More Control?

## Project Question

This project studies a counterfactual football question:

If Manchester United had not signed Cristiano Ronaldo in summer 2021, and had instead added a strong defensive midfielder profile, how might Ole Gunnar Solskjaer's 2021/22 league season have looked up to his exit in November 2021?

The project is designed as a portfolio-grade, end-to-end Python workflow. It favors transparency and interpretability over black-box complexity. The goal is not to "prove" causality, but to build an honest model of how team-level match outcomes might have shifted under different squad assumptions.

**Core thesis:** United added output when they needed control.

## Application Memo

A one-page memo version of this project was created for football data analyst applications:

- [Karan Moza Manchester United Control Memo](memo/Karan_Moza_Manchester_United_Control_Memo.pdf)

## Key Findings

- Using real public match-level data, the model estimates `18.13` counterfactual points by Ole's exit versus `17` actual points.
- Over the full `2021/22` league season, the model estimates `61.16` counterfactual points versus `58` actual points.
- The result is best interpreted as a modest but meaningful improvement, not a radically different season.
- The strategic takeaway is that United may have invested in the wrong capability in 2021: more attacking star power rather than more midfield control.

## Data Source

The project now supports two practical raw-data paths:

- manual FBref-style CSV exports placed in `data/raw/`
- automated real-data fetching from Understat via `src/fetch_understat_data.py`

FBref remains a supported import format for local CSVs, but the automated end-to-end real-data run in this project uses Understat because FBref blocks automated requests in this environment.

## Evidence Trail

The repo is organized to make the analytical path inspectable:

1. `data/raw/` stores public match-level inputs or reproducible examples.
2. `src/clean_data.py` and `src/features.py` standardize match records and create descriptive indicators.
3. `outputs/tables/season_summary.csv` and `outputs/tables/pre_post_ronaldo_summary.csv` document the descriptive profile.
4. `src/config.py` stores scenario assumptions.
5. `src/simulation.py` converts actual and counterfactual xG/xGA rates into Poisson match simulations.
6. `outputs/figures/` and `outputs/tables/` feed the application memo and supporting charts.

## Model Approach

The workflow has four layers:

1. Descriptive analysis
   Compares a 2020/21 Ole baseline against the first 12 Premier League matches of 2021/22 up to the Watford loss.

2. Diagnostic analysis
   Examines changes in team profile using goals, xG, xGA, shots, points, and rolling indicators.

3. Counterfactual design
   Models a generic high-level defensive midfielder profile instead of Ronaldo. The scenario assumptions are editable in `src/config.py`.

4. Forecasting and simulation
   Uses match-level Poisson simulations based on xG and xGA to compare the observed 2021/22 profile with the counterfactual version.

## Counterfactual Scenarios

- **Actual profile:** observed 2021/22 Manchester United match profile.
- **Generic CDM scenario:** a profile-level defensive midfielder intervention, not a named-player estimate.
- **Casemiro-style scenario:** an upper-bound illustration of what a more elite ball-winning/control profile might imply under the model assumptions.

## Key Implementation Choices

- A Poisson simulation is used because football scoring is low-event and match outcomes can be translated from xG/xGA into win, draw, and loss probabilities.
- The model is a scenario exercise, not causal proof. It shows plausible outcome ranges under explicit assumptions.
- The Generic CDM scenario is a profile scenario, not a claim about any single real player.
- The Casemiro-style scenario is treated as an upper-bound illustration rather than a recruitment recommendation.
- Assumptions live in `src/config.py` so the scenario can be challenged and rerun without editing modeling logic.
- Example CSVs are committed so the repo can still run even when external public-data fetching fails.

## Project Structure

```text
OGS/
├── README.md
├── requirements.txt
├── docs/
│   └── methodology.md
├── data/
│   ├── raw/
│   │   ├── README.md
│   │   ├── example_united_2020_21.csv
│   │   └── example_united_2021_22_ole.csv
│   └── processed/
├── outputs/
│   ├── figures/
│   └── tables/
├── notebooks/
│   ├── 01_exploration.ipynb
│   └── 02_counterfactual_model.ipynb
└── src/
    ├── __init__.py
    ├── analysis.py
    ├── clean_data.py
    ├── config.py
    ├── data_loader.py
    ├── features.py
    ├── main.py
    ├── plotting.py
    ├── simulation.py
    └── utils.py
```

## Data Requirements

The pipeline is designed around local CSV inputs in `data/raw/`. It does not assume fragile scraping.

Expected files:

- `data/raw/united_2020_21.csv`
- `data/raw/united_2021_22_ole.csv`
- `data/raw/united_2021_22_full.csv`

If those files do not exist, the project falls back to the included example CSVs:

- `data/raw/example_united_2020_21.csv`
- `data/raw/example_united_2021_22_ole.csv`
- `data/raw/example_united_2021_22_full.csv`

Minimum required columns:

- `date`
- `opponent`
- `venue`
- `goals_for`
- `goals_against`
- `xg`
- `xga`
- `shots_for`
- `shots_against`

Recommended optional columns:

- `competition`
- `manager`
- `notes`

See `data/raw/README.md` for the exact schema.

## How To Run

From the project root:

```bash
python src/fetch_understat_data.py
python src/main.py
python src/render_article.py
python src/build_combined_article.py
```

If you open the notebooks in VS Code or Jupyter, select a Python environment with the packages in `requirements.txt`.

Optional fallback if you ever want a self-contained environment later:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py
python3 src/render_article.py
python3 src/build_combined_article.py
```

PDF generation uses the HTML article as the source of truth and renders it through headless Chrome/Chromium. If Chrome is not installed in a standard location, set:

```bash
export CHROME_PATH="/path/to/chrome-or-chromium"
```

## What Gets Produced

Processed datasets are written to `data/processed/`.

Tables are written to `outputs/tables/`, including:

- executive summary
- season summary
- pre/post Ronaldo summary
- scenario assumptions
- simulation summary
- match-level win/draw/loss probabilities

Figures are written to `outputs/figures/`, including:

- rolling xG difference
- defensive fragility trend
- actual vs expected points
- pre/post comparison
- scenario comparison
- simulation distribution
- full-season actual vs counterfactual points

Supporting documents live in `docs/`, including:

- `executive_summary.md`
- `methodology.md`
- `article_brief.md`
- `sample_article.html`
- `sample_article.pdf`
- `united_control_article.html`
- `united_control_article.pdf`

Application memo:

- `memo/Karan_Moza_Manchester_United_Control_Memo.pdf`

Sample article PDF:

- `docs/sample_article.pdf`, rendered directly from `docs/sample_article.html` so the PDF matches the HTML article.

Combined United control article:

- `docs/united_control_article.html`
- `docs/united_control_article.pdf`, rendered directly from the HTML article and combining the Ole counterfactual with the Casemiro replacement screen.

## Assumptions

The counterfactual is intentionally simple and editable:

- attacking output is slightly reduced without Ronaldo
- defensive stability is improved by a defensive midfielder profile
- shot concession is reduced
- the model converts those team-level changes into match-level scoring distributions

All assumptions live in `src/config.py`, so you can revise them later for your own article.

## Why This Project Is Useful

This is not primarily a football-fandom exercise. It is a resource-allocation case study.

The underlying management question is:

Did Manchester United use elite spending power to solve the most visible problem instead of the most structurally important one?

## Limitations

- This is a modeled counterfactual, not proof of causal truth.
- The automated final run in this project uses real Understat match data, while FBref remains a supported manual import format.
- Transfer behavior, dressing-room effects, and tactical knock-on effects are represented only through team-level proxies.

## Interpretation Note

The project is designed to answer:

"Given observed team performance and a transparent set of squad-level assumptions, what range of outcomes becomes plausible under a more control-oriented midfield profile?"

That is a disciplined analytics question. It is not the same as claiming certainty about what "would have happened."
