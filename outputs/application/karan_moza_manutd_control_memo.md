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

I used public match-level Premier League data with goals, xG, xGA, shots for, and shots against. A Poisson goal simulation estimated win/draw/loss probabilities under alternative team profiles.

Counterfactual assumption: no Ronaldo, but a control-oriented midfielder improves defensive stability and shot suppression while slightly reducing attacking edge.

**This is a transparent scenario model, not a causal proof.**

## 4. Counterfactual Result

| 2021/22 points scenario | Points |
|---|---:|
| Actual | 58.0 |
| Generic elite CDM | 61.2 |
| Strong fit / Casemiro-style | 64.5 |

The model does not suggest one transfer fixes United. It suggests a control-oriented squad build plausibly improves the team's floor.

**The team tried to raise its ceiling, but failed to protect its floor.**

The conclusion is directional: the uplift depends on scenario assumptions, but the diagnosis is stable across mild/base/strong cases.

## 5. Recruitment Implication

A control-oriented midfielder should receive under pressure, progress play safely, reduce central transition exposure, protect rest defence, improve territorial stability, and reduce the number of defensive duels the back line has to face.

**The next signing should not only win duels. It should prevent some of them from happening.**

## 6. Decision Takeaway

Data should not just measure performance after the fact. It should help define the problem before capital is deployed.

**Before buying output, diagnose the constraint.**
