# Methodology Note

## Why This Is A Counterfactual

Manchester United did sign Cristiano Ronaldo in August 2021. That means we can never observe the true alternate world in which the club instead signed a strong defensive midfielder and kept the rest of the season unchanged.

Because of that, this project does not claim to identify causal truth. It builds a transparent scenario model.

## Plain-English Statistical Logic

1. Use match-level team data from the relevant periods.
2. Describe how United's profile changed from the 2020/21 Ole baseline to the 2021/22 start.
3. Build a configurable squad-adjustment scenario:
   - slightly less attacking volume or finishing upside
   - better defensive control
   - fewer shots conceded
4. Translate those adjusted match profiles into expected scoring rates.
5. Simulate many versions of the 2021/22 run to Ole's exit using Poisson goal models.
6. Compare the actual-profile distribution with the counterfactual-profile distribution.

## Why Poisson

Poisson models are simple, common in football analytics, and interpretable. They are not perfect, but they are a practical way to convert xG-style team rates into scoreline distributions.

## Main Assumptions

The model assumes a generic defensive midfielder would:

- improve defensive stability more than attacking output
- reduce expected goals against
- reduce shots conceded
- slightly reduce or reshape attacking output without Ronaldo's finishing presence

These assumptions are configurable in `src/config.py`.

The mild, base, and strong cases are not claimed as empirically estimated coefficients. They are judgment-based scenario bands designed to reflect three plausible versions of the same football idea:

- `Mild`: a midfielder who improves ball security and defensive protection, but only at the margins
- `Base`: a strong first-team-level solution that meaningfully improves chance prevention and midfield balance
- `Strong`: an upper-end fit where the midfielder is both tactically ideal and immediately impactful

The point of these bands is not to claim exact truth. It is to test whether the overall conclusion survives once the assumptions are relaxed or strengthened.

## Robustness Check

To avoid relying on a single exact assumption set, the project also runs a simple sensitivity analysis with three generic CDM cases:

- `Mild`: small defensive and control improvement
- `Base`: the main scenario used throughout the article
- `Strong`: a more aggressive but still plausible control-first scenario

On the real-data full-season run, those cases produced:

- `Mild`: `58.45` points
- `Base`: `61.16` points
- `Strong`: `64.56` points

Against the observed `58`-point season, that means the modeled uplift ranges from roughly `+0.45` to `+6.56` points.

This does not validate the assumptions as “true,” but it does show that the broader conclusion is not entirely dependent on one exact parameter choice.

## Main Caveats

- Team tactics are more complex than a single-parameter adjustment.
- Ronaldo's influence was not only about finishing.
- Opponent adaptation is not modeled.
- The scenario assumes the same schedule and broad tactical context.
- The sensitivity analysis is still assumption-driven rather than empirically estimated from a transfer-market sample.

This is best interpreted as a disciplined scenario exercise rather than a definitive historical claim.
