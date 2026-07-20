# Goal Description

The goal of this phase is to retrain and evaluate the MA-ROPE policy under the `manuscript_calibrated` queue environment. 
Previous phases isolated and corrected the queueing delay behavior to match the deterministic baseline targets (AllOffload and NoOffload) from the paper. This confirmed that the manuscript used an active-task queue assignment and a `DELAY_PER_UNIT_MS` scalar of roughly 35 ms.

Now we will test whether this new environment state allows the DRL agent to discover the proper energy-scaling behavior and close the remaining discrepancy in MA-ROPE's Energy metric at $N=32$.

## Proposed Changes

### Scripts
#### [NEW] [evaluate_marope_calibrated.py](file:///Users/aryaveersingh/Projects/Antrigravity_Projects/projects/vehicular-simulation-MAROPE-recreation/scripts/evaluate_marope_calibrated.py)
A new targeted sweep script that:
- Runs training for `ma-rope` using 5 seeds under `manuscript_calibrated` mode for both $N=8$ and $N=32$.
- Also runs `alloffload` and `nooffload` for context (since deterministic, only needs to evaluate, no training).
- Uses the `FederatedCoordinator` and `V2XEnv` classes as previously established.
- Aggregates metrics (U_PRR, U_OTR, Energy, Latency, PRR, Fleet OTR) and writes a markdown report comparing the results against the original manuscript targets.

## Verification Plan

### Automated Tests
- Run `python3 scripts/evaluate_marope_calibrated.py` in the background.

### Manual Verification
- Review the generated report (`MANUSCRIPT_CALIBRATED_POLICY_REPORT.md`) to verify if the retrained MA-ROPE energy profile falls back into alignment with the manuscript's target (~0.7057 J for N=32).
