# Tanker Ton-Mile Demand Model

A small, transparent model of tanker **ton-mile demand**, a core metric of tanker demand, with two geopolitical scenario levers (Red Sea rerouting and Strait of Hormuz / Gulf-export disruption). Built in Python and Excel from a single dataset, so every output traces back to one source of truth.

> **Ton-miles = cargo × distance.** Tanker demand is not "how much oil moves" but "how much oil moves *and how far*." Where a barrel is sourced can matter more than whether the world burns more of them.

---

## The one idea

Tankers are paid to move cargo over distance, so the demand for ships is measured in **ton-miles** (tonnes × nautical miles), not barrels. A short, high-volume lane can need *fewer* ships than a long, lower-volume one:

| Lane | Volume | One-way distance | Ton-mile demand |
|---|---|---|---|
| Middle East Gulf → India | 2.0 mb/d | ~1,500 nm | ~149 bn |
| West Africa → China | 1.8 mb/d | ~10,500 nm | ~941 bn |

Fewer barrels, ~6× the ship demand — because the oil travels ~7× as far. That inversion is the whole point of thinking in ton-miles.

## The two levers

Each lever models a distinct physical mechanism and propagates consistently across every exposed trade lane.

1. **Red Sea rerouting (distance, 0–100%).** Bab el-Mandeb / Suez is a *transit* chokepoint you can avoid by sailing around the Cape of Good Hope. Only Suez-transiting (Europe-bound) lanes are affected. The lever is the *share* of exposed vessels diverting; distance rises toward the Cape figure in proportion. Same barrels, longer voyage → **more** ton-miles.

2. **Net Gulf export loss (volume, 0–100%).** The Strait of Hormuz is the *only* sea exit from the Persian Gulf — there is no reroute. This lever is the net share of Gulf-origin cargo lost from the seaborne market (a physical closure is not 1:1 with export loss: Saudi/UAE pipelines can bypass ~3.5–5.5 mb/d). It removes Gulf-origin barrels → **fewer** ton-miles.

**The counter-intuitive result worth understanding:** a large Gulf export loss *lowers* modelled ton-mile demand (less oil sailing), yet real-world 2026 tanker rates spiked to record highs during the Hormuz disruption. That gap is the lesson — the rate explosion lived in *supply* disruption, fleet repositioning and war-risk premia, none of which a demand-only model captures. **This model is the demand half of the rate, not the rate.**

## What's in here

| File | What it is |
|---|---|
| `trade_lanes.csv` | The canonical dataset — 25 major crude & product lanes with volume, distances, exposure flags. **Single source of truth.** |
| `tonmile_engine.py` | Python engine: loads the CSV, computes ton-mile demand, runs the two levers from the command line. |
| `build_outputs.py` | Regenerates the Excel model and the HTML one-pager from the same data. |
| `tonmile_model.xlsx` | Live Excel model: edit the yellow lever cells and every calculation + the Baseline/Scenario/Δ block recomputes. Flag-driven formulas (one identical formula per row). |
| `tonmile_map.html` | Visual one-pager: top lanes, segment shares, the two levers. Open in any browser. |
| `README.md` | This file. |

## Quickstart

```bash
# Base case
python tonmile_engine.py

# Half of exposed vessels reroute via the Cape
python tonmile_engine.py --redsea 0.5

# 50% of Gulf-origin cargo lost from the market
python tonmile_engine.py --hormuz-loss 0.5

# Both together
python tonmile_engine.py --redsea 1.0 --hormuz-loss 0.5

# Rebuild the Excel model and one-pager from the CSV
python build_outputs.py
```

Requires Python 3 and `openpyxl` (`pip install openpyxl`). Or just open `tonmile_model.xlsx` and edit the two yellow lever cells; open `tonmile_map.html` in a browser.

## Headline outputs (2025 baseline)

| Scenario | Ton-mile demand | vs baseline |
|---|---|---|
| Baseline (levers off) | 8,534 bn tonne-nm/yr | — |
| Red Sea full diversion | 9,001 bn | **+5.5%** (distance) |
| Net Gulf export loss, 50% | 6,670 bn | **−21.8%** (volume) |
| Both (full reroute + 50% loss) | 6,970 bn | **−18.3%** |

Within the modelled sample the split is roughly 85% crude / 15% clean and ~64% VLCC — **but see the caveat below: that is the split of this sample, not of the global tanker market.**

## Data & methodology

These are **selected major trade lanes**, chosen for transparency and directional commercial insight, not a bottom-up reconstruction of global tanker trade. Volumes are order-of-magnitude figures anchored on public sources (Energy Institute Statistical Review, IEA, EIA), reflecting a **2025 baseline**; distances are approximate one-way laden nautical miles; barrel→tonne conversion is 7.33 (crude) / 8.0 (clean).

Coverage, for honesty: the Hormuz-flagged lanes here total ~14.3 mb/d against an IEA/EIA 2025 Strait-of-Hormuz figure of ~20 mb/d (~15 crude / ~5 products) — so this captures **~72% of Hormuz oil flows**, and it skews to crude (captures ~80% of Hormuz crude but only ~half of Hormuz products). The Red Sea distance assumption (MEG→Europe ~6,400 nm via Suez vs ~11,100 nm via the Cape) is consistent with EIA voyage-day estimates. Alternative-route bypass capacity of 3.5–5.5 mb/d is the IEA figure.

**Methodology statement (the honest one-liner):** *these are selected major trade lanes, not a complete bottom-up reconstruction of global tanker trade; the goal is transparency and directional commercial insight, not false precision.*

## Scope & limitations

- **Demand half only — not freight rates.** This measures the cargo-work component of demand. Turning it into fleet utilisation or rates needs ballast distance, speed, port time and vessel supply (the planned supply-side extension).
- **A sample, not the market.** Segment and crude/clean shares are shares of *modelled* ton-miles. Do not present them as the global tanker market.
- **First-order physical shock.** The Gulf-loss lever removes barrels; it does not (yet) endogenise substitution — e.g. China replacing Gulf crude with US Gulf / Brazil / West Africa barrels, which would partially restore volume while *increasing* average voyage distance. That is a deliberate second-stage extension (partial- vs market-equilibrium).
- **Illustrative volumes.** Refresh and lock to a single sourced base year before any serious use.

## Roadmap

- **Supply side** — fleet, orderbook, scrapping, EEXI/CII — to move from demand → utilisation → rates.
- **Source-locked volumes** — replace illustrative figures with cited data locked to one base year.
- **Endogenous substitution** — turn the first-order shock into a market-equilibrium response.

## Disclaimer

Educational / illustrative project. Not investment advice and not a freight-rate forecast. Figures are approximate and should be independently verified before any decision.
