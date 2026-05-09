# Manchester United 2021: Solving the Wrong Problem

**A data-led counterfactual on output vs control in squad-building decisions**  
Application memo | Football data analysis | Karan Moza

## 1. The Diagnosis

In 2021, Manchester United added Cristiano Ronaldo to increase attacking output. But the underlying data suggests the team's more urgent issue was not chance creation. It was control: midfield stability, defensive transitions, and the ability to protect the back line.

**United did not buy the wrong player as much as they bought the wrong solution.** United added output when they needed control.

## 2. Evidence Snapshot

| Metric | 2020/21 | 2021/22 full season |
|---|---:|---:|
| Points | 74 | 58 |
| xG difference / match | +0.56 | +0.01 |
| xGA / match | 1.10 | 1.50 |
| Shots against / match | 11.37 | 13.47 |

The decline was not only a table-position story. United lost most of their underlying xG cushion while conceding more chance quality and shot volume.

## 3. Model Approach

Using public match-level Premier League data, I modeled United's attacking and defensive profile through goals, xG, xGA, shots for, and shots against. A Poisson goal simulation then estimated win/draw/loss probabilities under alternative team profiles.

The counterfactual assumes no Ronaldo signing, with a control-oriented midfielder improving defensive stability and shot suppression.

**This is a transparent scenario model, not causal proof.**

## 4. Counterfactual Result

| 2021/22 points scenario | Points |
|---|---:|
| Actual 2021/22 | 58.0 |
| Generic CDM | 61.2 |
| Strong fit / Casemiro-style | 64.5 |

Control improves the expected points profile, but does not transform the team. **The team tried to raise its ceiling, but failed to protect its floor.**

Analytical caution: This is a directional scenario model. The uplift depends on assumptions, but the diagnosis remains stable across mild/base/strong cases.

## 5. Required Midfielder Profile

A control-oriented midfielder should:

- receive under pressure
- progress play safely
- reduce central transition exposure
- protect rest defence
- improve territorial stability
- prevent defensive duels before they happen

**The next signing should not only win duels. It should prevent some of them from happening.**

## 6. Decision Takeaway

**Before buying output, diagnose the constraint.**

Data should not just measure performance after the fact; it should help define the problem before capital is deployed.

Source: OGS counterfactual project outputs; public match-level Premier League data.
