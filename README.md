## Known limitations

## Backtest evaluation

The model is replayed on a fixed window (2026-08-27 to 2026-10-22, DE_LU, 1,342 hours) and compared with ENTSO-E day-ahead prices. `SHORTAGE` hours are valued at a fixed CAP of 250 EUR/MWh so that errors can be computed on all hours.

Baseline: SHORTAGE 46 %, MAE 57.0 EUR/MWh (naive benchmark 59.7), bias +45 EUR/MWh.

See [Backtest evaluation](docs/backtest_evaluation.md) for the method, the full results and the CAP sensitivity.

* **Wind generation:** Onshore (100 clusters) and offshore (25 clusters) wind are geographically clustered, with Hellmann hub-height and air-density corrections. Onshore production does not converge cleanly as the number of clusters increases (5–10% variation between K=25 and K=200), so K=100 was chosen pragmatically. The source dataset covers approximately 92% of ENTSO-E onshore capacity and 91% of offshore capacity; cluster capacities are scaled uniformly to ENTSO-E totals.
* **Solar generation:** Solar is geographically clustered (25 clusters), but the source dataset mainly covers ground-mounted installations (about 21 GW versus 104 GW reported by ENTSO-E). Cluster capacities are scaled uniformly to the national total, which may over-represent regions with many ground-mounted plants (e.g. Bavaria) and does not capture the spatial distribution of rooftop PV.
* **Gas:** The model represents the entire ENTSO-E installed gas capacity as a single plant with 93% random availability (seeded with `random.seed(42)` so backtest results are reproducible). Consequently, a simulated outage can remove the whole gas fleet at once. Gas and CO₂ prices are daily rather than hourly.
* **Market:** The model covers a single bidding zone (DE_LU) and does not explicitly model cross-border market coupling. With the current technology mix and cost assumptions, simulated prices are largely driven by renewable availability and the gas marginal cost.
* **SHORTAGE pricing:** the CAP of 250 EUR/MWh was chosen from prices observed in the same window, so it slightly favours the model.
