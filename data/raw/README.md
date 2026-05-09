# Raw Data Guide

Place your local CSV files in this folder.

Preferred filenames:

- `united_2020_21.csv`
- `united_2021_22_ole.csv`
- `united_2021_22_full.csv`

If those files are absent, the pipeline automatically uses:

- `example_united_2020_21.csv`
- `example_united_2021_22_ole.csv`
- `example_united_2021_22_full.csv`

## Recommended FBref Path

The easiest real-data workflow is to export Manchester United team match logs from FBref and save them here as CSV files.

Good candidates:

- Scores & Fixtures style exports for `date`, `opponent`, `venue`, `GF`, `GA`, `xG`, `xGA`
- Team match logs or schedule-style exports that include `Sh` for shots

This project now supports common FBref-style columns directly, including:

- `Date`
- `Opponent`
- `Venue`
- `GF`
- `GA`
- `xG`
- `xGA`
- `Sh`
- `Comp`

If an FBref export does not include opponent shot totals, the pipeline will transparently impute `shots_against` from `xGA` as a first-pass proxy and flag that in `notes`.

## Minimum Required Columns

| Column | Description |
| --- | --- |
| `date` | Match date in `YYYY-MM-DD` format |
| `opponent` | Opposing team name |
| `venue` | `H` or `A` |
| `goals_for` | Manchester United goals |
| `goals_against` | Opponent goals |
| `xg` | Manchester United expected goals |
| `xga` | Opponent expected goals / United expected goals against |
| `shots_for` | Manchester United shots |
| `shots_against` | Opponent shots, or leave absent and let the pipeline impute from `xGA` |

## Optional Columns

| Column | Description |
| --- | --- |
| `competition` | For example `Premier League` |
| `manager` | For example `Ole Gunnar Solskjaer` |
| `notes` | Any free-text note |

## Notes

- The current project assumes league matches for the main comparison and simulation.
- FBref-style exports are now supported directly through alias mapping.
- If your file includes repeated header rows or `Home` / `Away` text instead of `H` / `A`, the cleaning step now normalizes that too.
- If your source uses different names like `home_away` or `gf`, the cleaning step can standardize them, but the closer you stay to the schema above, the easier the rerun will be.
- Richer public datasets can be used later without changing the core project structure.
