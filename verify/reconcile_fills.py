"""Compute your own Hyperliquid trading P&L from public on-chain data.

Give it a wallet address and a date range. It fetches every perpetual futures
fill and funding payment for that address from Hyperliquid's public info API
(https://api.hyperliquid.xyz/info) and prints:

  closed P&L       realised profit or loss on positions closed in the range
  fees             trading fees paid (including any builder fees)
  funding          funding received (+) or paid (-)
  net trading P&L  closed P&L - fees + funding
  unrealised P&L   open positions, valued now
  account equity   current value of the perpetuals account

Deposits, withdrawals and transfers are listed separately and excluded from
P&L, so the result measures trading only. No keys are needed.

Use it to check your own AlphaNet results against AlphaNet's published
record. Compare over the same period and the same venue: the published figures
are model strategy returns measured from each strategy's start date, not the
returns of any one customer account, and an account's result also depends on
when it started, its allocation and any manual trades.

Usage:
    python verify/reconcile_fills.py 0xYourAddress --start 2026-10-01 --end 2026-11-01
    python verify/reconcile_fills.py 0xYourAddress --start 2026-10-01 --csv fills.csv
"""

import argparse
import json
from datetime import datetime, timezone

import pandas as pd
import requests

INFO_URL = "https://api.hyperliquid.xyz/info"
MAX_FILLS = 10_000


def post(body):
    r = requests.post(INFO_URL, json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all(kind, user, start_ms, end_ms):
    """Page through a time-ranged info query. Each call returns at most a few
    thousand rows, oldest first, so restart from the last timestamp seen and
    drop rows already collected."""
    rows, seen = [], set()
    while start_ms <= end_ms:
        page = post({"type": kind, "user": user, "startTime": start_ms, "endTime": end_ms})
        new = [x for x in page if json.dumps(x, sort_keys=True) not in seen]
        if not new:
            break
        rows += new
        seen.update(json.dumps(x, sort_keys=True) for x in new)
        start_ms = max(x["time"] for x in page)
    return rows


def account_equity(user, state):
    """Account equity in USDC. In Hyperliquid's unified and portfolio-margin
    modes, collateral sits in the spot USDC balance, so equity is that balance
    plus unrealised P&L. In manual mode it is the perpetuals account value."""
    if post({"type": "userAbstraction", "user": user}) in ("unifiedAccount", "portfolioMargin"):
        spot = post({"type": "spotClearinghouseState", "user": user})
        usdc = sum(float(b["total"]) for b in spot["balances"] if b["coin"] == "USDC")
        return usdc + sum(float(p["position"]["unrealizedPnl"]) for p in state["assetPositions"])
    return float(state["marginSummary"]["accountValue"])


def to_ms(day):
    return int(datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("address", help="Hyperliquid account address (0x...)")
    parser.add_argument("--start", required=True, help="start date, YYYY-MM-DD (UTC)")
    parser.add_argument("--end", help="end date, YYYY-MM-DD (UTC, exclusive); default now")
    parser.add_argument("--csv", help="also write every fill to this CSV file")
    args = parser.parse_args()

    user = args.address.lower()
    start = to_ms(args.start)
    end = to_ms(args.end) - 1 if args.end else int(datetime.now(timezone.utc).timestamp() * 1000)

    fills = pd.DataFrame(fetch_all("userFillsByTime", user, start, end))
    funding = fetch_all("userFunding", user, start, end)
    ledger = fetch_all("userNonFundingLedgerUpdates", user, start, end)
    state = post({"type": "clearinghouseState", "user": user})

    if fills.empty:
        closed = fees = 0.0
    else:
        for col in ("closedPnl", "fee", "builderFee"):
            fills[col] = pd.to_numeric(fills[col], errors="coerce").fillna(0.0) if col in fills else 0.0
        closed = fills["closedPnl"].sum()
        fees = fills["fee"].sum() + fills["builderFee"].sum()
    funding_total = sum(float(x["delta"]["usdc"]) for x in funding)
    unrealised = sum(float(p["position"]["unrealizedPnl"]) for p in state["assetPositions"])
    equity = account_equity(user, state)

    flows = {}
    for x in ledger:
        d = x["delta"]
        amount = d.get("usdc") or d.get("usdcValue") or d.get("amount")
        if amount is not None:
            flows[d["type"]] = flows.get(d["type"], 0.0) + float(amount)

    print(f"Address: {user}")
    print(f"Period:  {datetime.fromtimestamp(start / 1000, timezone.utc):%Y-%m-%d} to "
          f"{datetime.fromtimestamp(end / 1000, timezone.utc):%Y-%m-%d %H:%M} UTC")
    print(f"Fills:   {len(fills)}   Funding payments: {len(funding)}")
    if len(fills) >= MAX_FILLS:
        print(f"Warning: Hyperliquid serves only about the {MAX_FILLS:,} most recent fills per address, "
              "so older fills in this period may be missing. Use a shorter, more recent period.")
    print()
    rows = [
        ("Closed P&L", closed),
        ("Fees", -fees),
        ("Funding", funding_total),
        ("Net trading P&L", closed - fees + funding_total),
        ("Unrealised P&L (now)", unrealised),
        ("Account equity (now)", equity),
    ]
    for label, value in rows:
        print(f"  {label:<24}{value:>16,.2f} USDC")
    if flows:
        print("\nExcluded from P&L (deposits, withdrawals, transfers):")
        for kind, value in sorted(flows.items()):
            print(f"  {kind:<24}{value:>16,.2f} USDC")

    if args.csv and not fills.empty:
        fills["time"] = pd.to_datetime(fills["time"], unit="ms", utc=True)
        fills.to_csv(args.csv, index=False)
        print(f"\nWrote {len(fills)} fills to {args.csv}")


if __name__ == "__main__":
    main()
