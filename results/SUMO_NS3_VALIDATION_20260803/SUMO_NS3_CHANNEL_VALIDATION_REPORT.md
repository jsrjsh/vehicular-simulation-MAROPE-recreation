# SUMO vs ns-3 Channel Model Validation Report

This report validates the analytical `env/channel.py` physical layer model against an ns-3.41 simulation containing WiFi-6 (MEC) and LTE (CLOUD) modules.

## Module Setup
> [!NOTE]
> Option (B) was selected: ITS-G5 and 5G-NR are currently deferred as the `wave` and `5G-LENA` modules are not installed in the current ns-3 tree.

## Provenance
- **Execution Date**: 2026-08-03 16:58:12
- **ns-3 modules**: core, network, mobility, internet, wifi, lte, propagation
- **Run command**: `./ns3 run "scratch/channel-validation --strategy=1 --traceFile=../mobility.tcl --csvFile=../simulation_results_channel_validation.csv"`
- **Raw CSV paths**: `/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/vehicular-simulation/simulation_results_channel_validation.csv`
- **Comparison script**: `/Users/aryaveersingh/Projects_Claude/01_Engineering/vehicular-simulation-MAROPE-recreation/_claude_workspace/scripts/validate_ns3_channel.py`

## RAT: LTE (CLOUD)
**Mean Divergence (MAE across distance bins)**: 0.9934

| Distance (m) | Count | Empirical Prob | Analytical Prob | Divergence |
|---|---|---|---|---|
| 325.0 | 671 | 0.0015 | 0.9959 | 0.9945 |
| 375.0 | 288 | 0.0000 | 0.9955 | 0.9955 |
| 425.0 | 1850 | 0.0043 | 0.9954 | 0.9911 |
| 475.0 | 766 | 0.0000 | 0.9947 | 0.9947 |
| 525.0 | 781 | 0.0038 | 0.9949 | 0.9910 |
| 575.0 | 1474 | 0.0014 | 0.9944 | 0.9930 |
| 625.0 | 292 | 0.0000 | 0.9941 | 0.9941 |

## RAT: WiFi-6 (MEC)
**Mean Divergence (MAE across distance bins)**: 0.9114

| Distance (m) | Count | Empirical Prob | Analytical Prob | Divergence |
|---|---|---|---|---|
| 75.0 | 3593 | 0.0000 | 0.9114 | 0.9114 |

