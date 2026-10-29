# Backtest evaluation

## Setup

- **Zone:** DE_LU (single bidding zone, no market coupling)
- **Window:** 2026-08-27 to 2026-10-22, 1,342 hourly observations
- **Inputs:** ENTSO-E day-ahead demand and prices; historical weather (Open-Meteo archive) for 150 clusters (25 solar, 100 onshore wind, 25 offshore wind); installed capacities from ENTSO-E
- **Frozen inputs:** gas and CO2 prices are snapshots in `data/` (`gas_snapshot_2026-10-25.csv`, `co2_snapshot_2026-10-25.csv`). The window is fixed in `backtest.py` (`USE_FIXED_WINDOW = True`), and random availability is seeded (`random.seed(42)`). Two runs give identical results, so any change in the metrics comes from a change in the model.
- **Run:** `python3 backtest.py` from the project root

## Treatment of SHORTAGE hours

When installed capacity cannot cover demand, the model returns `SHORTAGE` instead of a price. To evaluate the model on all hours, these missing prices are replaced by a fixed **CAP of 250 EUR/MWh**.

The CAP is an empirical evaluation convention, not a market price or a theoretical equilibrium price. Real ENTSO-E prices during the model's SHORTAGE hours in this window were:

| Statistic | EUR/MWh |
|---|---:|
| Mean | 208 |
| Median | 200 |
| 90th percentile | 264 |

250 lies between the median and the 90th percentile: conservative, but grounded in observed prices. It is fixed and is not recomputed at each run.

Because it was chosen by looking at the same window that is evaluated, it slightly favours the model. Keep it unchanged when comparing model versions.

## Metrics

All metrics compare the model price (or the CAP in SHORTAGE hours) with the real ENTSO-E day-ahead price.

- **Bias:** mean signed error. Positive = the model overestimates.
- **MAE:** mean absolute error, in EUR/MWh.
- **RMSE:** root mean squared error. Penalises large errors more than MAE.
- **Naive MAE:** benchmark that predicts the mean real price of the window for every hour.
- **Correlation and median error (non-SHORTAGE hours only):** describe only the hours where the model produces a price. They are not measures of overall accuracy.

## Baseline results (CAP = 250)

| Metric | Result |
|---|---:|
| Hours evaluated | 1,342 |
| SHORTAGE hours | 46 % |
| Bias (all hours) | +45 EUR/MWh |
| MAE (all hours) | 57.0 EUR/MWh |
| RMSE (all hours) | 73.9 EUR/MWh |
| Naive MAE | 59.7 EUR/MWh |
| Correlation, non-SHORTAGE hours | 0.648 |
| Median error, non-SHORTAGE hours | +39.6 EUR/MWh |

Hours without SHORTAGE follow the direction of the market (correlation 0.65), but at a price level that is too high.

## Sensitivity to the CAP

| CAP (EUR/MWh) | MAE | RMSE |
|---:|---:|---:|
| 200 | 48.0 | 68.4 |
| **250** | **57.0** | **73.9** |
| 300 | 76.3 | 92.4 |
| 400 | 120.5 | 146.7 |

The metrics depend strongly on the CAP, since 46 % of the hours use it. A CAP of 200 is the most favourable to the model (it is the median of real prices in SHORTAGE hours).

To print the SHORTAGE diagnostic and this table, set `SHOW_CAP_ANALYSIS = True` in `backtest.py`.

## Context

- The window covers late summer and autumn only. Results are not representative of winter or of exceptional episodes such as the June 2026 heatwave (price peaks up to 693 EUR/MWh on 2026-06-24).
- Real evening (18-23h) median prices by season over Oct 2025 - Aug 2026 range from 107 (autumn) to 161 EUR/MWh (summer); see `checks/price_history.py`.


## Main limitation

Lignite, hard coal, hydro, biomass and imports are not modelled.