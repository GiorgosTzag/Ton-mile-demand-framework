"""
tonmile_engine.py  —  Tanker ton-mile demand engine (2025 baseline)
===================================================================
Ton-mile demand = cargo x distance = the real driver of tanker demand.

TWO physical levers, each a mechanism you cannot reproduce by editing one cell:

  1. RED SEA rerouting (distance, 0-1)  -- Bab el-Mandeb / Suez is a TRANSIT
        chokepoint you can AVOID by sailing around the Cape of Good Hope. Only
        Suez-transiting (Europe-bound) lanes are affected. The lever is the SHARE
        of exposed vessels diverting: 0 = none, 1 = all. Distance rises toward the
        Cape figure in proportion. Same barrels, longer voyage, MORE ton-miles.

  2. HORMUZ / net Gulf export loss (volume, 0-1)  -- Hormuz is the ONLY exit from
        the Persian Gulf; there is no reroute. This lever is the NET share of
        Gulf-origin cargo lost from the seaborne market (a physical closure is not
        1:1 with export loss: Saudi/UAE pipelines can bypass ~3.5-5.5 mb/d). It
        REMOVES Gulf-origin barrels, so it LOWERS ton-miles. Note: the 2026 rate
        explosion did NOT come from this demand channel -- it came from supply
        disruption, fleet inefficiency and war-risk premia, which a demand-only
        model cannot see. This is the demand half of the rate, not the rate.

"Geography beats volume" is shown by hand: edit two volume cells (move a lane's
barrels from a short haul to a long one) and watch ton-miles rise while barrels
stay flat. It needs no lever.

Usage:
    python tonmile_engine.py
    python tonmile_engine.py --redsea            # full diversion (share = 1.0)
    python tonmile_engine.py --redsea 0.5        # half of exposed vessels divert
    python tonmile_engine.py --hormuz-loss 0.5   # 50% of Gulf-origin cargo lost

Volumes/distances are illustrative approximations of major lanes (Energy Institute /
IEA / EIA order of magnitude, 2025 baseline). Distances are one-way laden nautical
miles. This is a SELECTED-lane sample (~72% of Hormuz oil flows), not the whole
market -- shares are shares of modelled ton-miles. Refresh & lock to one base year
before interview use.
"""

import csv
import argparse
from pathlib import Path

DATA = Path(__file__).with_name("trade_lanes.csv")
DAYS = 365


def load_lanes(path=DATA):
    lanes = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            r["volume_mbd"] = float(r["volume_mbd"])
            r["dist_base_nm"] = float(r["dist_base_nm"])
            r["dist_cape_nm"] = float(r["dist_cape_nm"])
            r["bbl_per_t"] = float(r["bbl_per_t"])
            r["red_sea"] = r["red_sea_exposed"].strip().upper() == "Y"
            r["hormuz"] = r["hormuz_exposed"].strip().upper() == "Y"
            lanes.append(r)
    return lanes


def tonne_miles_bn(volume_mbd, distance_nm, bbl_per_t):
    tonnes_yr = volume_mbd * 1e6 * DAYS / bbl_per_t
    return tonnes_yr * distance_nm / 1e9


def compute(lanes, redsea=0.0, hormuz_loss=0.0):
    """Apply the two levers and return per-lane results.
    redsea:      share (0-1) of exposed vessels rerouting via the Cape.
    hormuz_loss: share (0-1) of Gulf-origin cargo lost from the seaborne market.
    """
    rows = []
    for L in lanes:
        vol = L["volume_mbd"]
        if hormuz_loss and L["hormuz"]:
            vol *= (1.0 - hormuz_loss)
        vol = max(0.0, vol)
        if redsea and L["red_sea"]:
            dist = L["dist_base_nm"] + redsea * (L["dist_cape_nm"] - L["dist_base_nm"])
        else:
            dist = L["dist_base_nm"]
        rows.append({**L, "eff_volume": vol, "eff_distance": dist,
                     "tm_bn": tonne_miles_bn(vol, dist, L["bbl_per_t"])})
    return rows


def summarize(rows):
    total = sum(r["tm_bn"] for r in rows)
    by_segment, by_trade = {}, {}
    for r in rows:
        by_segment[r["segment"]] = by_segment.get(r["segment"], 0) + r["tm_bn"]
        by_trade[r["trade"]] = by_trade.get(r["trade"], 0) + r["tm_bn"]
    return total, by_segment, by_trade


def report(redsea=0.0, hormuz_loss=0.0):
    lanes = load_lanes()
    rows = compute(lanes, redsea, hormuz_loss)
    total, by_segment, by_trade = summarize(rows)
    base_total, _, _ = summarize(compute(lanes))

    print("=" * 66)
    print("TANKER TON-MILE DEMAND  —  2025 baseline, major lanes (illustrative)")
    print(f"Levers: Red Sea rerouting={redsea:.0%} | net Gulf export loss={hormuz_loss:.0%}")
    print("=" * 66)
    print(f"Scenario ton-mile demand: {total:,.0f} bn tonne-nm/yr")
    print(f"Baseline (levers off):    {base_total:,.0f} bn tonne-nm/yr")
    if redsea or hormuz_loss:
        print(f"  Delta:                  {total-base_total:+,.0f} bn   ({(total/base_total-1)*100:+.1f}%)")
    print()

    print("By segment (share of modelled ton-miles):")
    for seg, v in sorted(by_segment.items(), key=lambda x: -x[1]):
        print(f"  {seg:<8} {v:>9,.0f} bn   {v/total*100:>5.1f}%")
    print("\nCrude vs clean (share of modelled ton-miles):")
    for t, v in sorted(by_trade.items(), key=lambda x: -x[1]):
        print(f"  {t:<8} {v:>9,.0f} bn   {v/total*100:>5.1f}%")
    print()

    print("Top 8 lanes by ton-mile demand:")
    for r in sorted(rows, key=lambda r: -r["tm_bn"])[:8]:
        lane = f"{r['origin']}->{r['destination']}"
        print(f"  {lane[:32]:<33}{r['segment']:<8}{r['eff_volume']:>5.1f}mb/d"
              f"{r['eff_distance']:>8,.0f}nm{r['tm_bn']:>8,.0f}bn")
    print()

    rs, _, _ = summarize(compute(lanes, redsea=1.0))
    clo, _, _ = summarize(compute(lanes, hormuz_loss=0.5))
    print("-" * 66)
    print("Lesson deltas (vs baseline):")
    print(f"  1. Red Sea full diversion (Cape):       {(rs/base_total-1)*100:+.1f}%  distance -> MORE ton-miles")
    print(f"  2. Net Gulf export loss, 50%:           {(clo/base_total-1)*100:+.1f}%  volume  -> LESS ton-miles (!)")
    print("  The rate SPIKE in a real closure comes from supply disruption + risk")
    print("  premia this demand model does not capture. This is the demand half only.")
    print("-" * 66)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--redsea", nargs="?", const=1.0, type=float, default=0.0,
                    help="share of exposed vessels rerouting via Cape (0-1); bare flag = 1.0")
    ap.add_argument("--hormuz-loss", type=float, default=0.0, dest="hormuz_loss",
                    help="net share of Gulf-origin cargo lost from the market (0-1)")
    a = ap.parse_args()
    report(redsea=a.redsea, hormuz_loss=a.hormuz_loss)
