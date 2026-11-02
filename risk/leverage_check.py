"""Check a Hyperliquid account's leverage against AlphaNet's two risk limits.

Reads the account's open perpetual positions and equity from Hyperliquid's
public info API and prints account leverage:

    leverage = total position notional / account equity

then compares it with AlphaNet's portfolio-level limits:

    3x  deployment limit: new or increased deployments must stay within 3x
    6x  auto-stop: at 6x, AlphaNet strategies stop and their positions close

This is the on-chain view: it counts every open position, including manual
ones. AlphaNet's own ratios are calculated from account equity, strategy
allocations and manual net-position notional, so the figure shown in the
AlphaNet app can differ. No keys are needed.

Usage:
    python risk/leverage_check.py 0xYourAddress
"""

import argparse

import requests

INFO_URL = "https://api.hyperliquid.xyz/info"
DEPLOYMENT_LIMIT = 3.0
AUTO_STOP = 6.0


def post(body):
    r = requests.post(INFO_URL, json=body, timeout=30)
    r.raise_for_status()
    return r.json()


def account_equity(user, state):
    """Account equity in USDC. In Hyperliquid's unified and portfolio-margin
    modes, collateral sits in the spot USDC balance, so equity is that balance
    plus unrealised P&L. In manual mode it is the perpetuals account value."""
    if post({"type": "userAbstraction", "user": user}) in ("unifiedAccount", "portfolioMargin"):
        spot = post({"type": "spotClearinghouseState", "user": user})
        usdc = sum(float(b["total"]) for b in spot["balances"] if b["coin"] == "USDC")
        return usdc + sum(float(p["position"]["unrealizedPnl"]) for p in state["assetPositions"])
    return float(state["marginSummary"]["accountValue"])


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("address", help="Hyperliquid account address (0x...)")
    args = parser.parse_args()

    user = args.address.lower()
    state = post({"type": "clearinghouseState", "user": user})
    equity = account_equity(user, state)
    positions = [p["position"] for p in state["assetPositions"]]
    notional = sum(abs(float(p["positionValue"])) for p in positions)

    print(f"Address:          {args.address}")
    print(f"Account equity:   {equity:,.2f} USDC")
    print(f"Open positions:   {len(positions)}")
    for p in sorted(positions, key=lambda p: -abs(float(p["positionValue"]))):
        side = "long" if float(p["szi"]) > 0 else "short"
        print(f"  {p['coin']:<10}{side:<7}{abs(float(p['positionValue'])):>16,.2f} USDC")
    print(f"Total notional:   {notional:,.2f} USDC")

    if equity <= 0:
        print("Account equity is zero; leverage is undefined.")
        return
    leverage = notional / equity
    if leverage >= AUTO_STOP:
        status = f"at or above {AUTO_STOP:g}x: AlphaNet strategies would stop and close their positions"
    elif leverage > DEPLOYMENT_LIMIT:
        status = f"above {DEPLOYMENT_LIMIT:g}x: no new or increased AlphaNet deployments allowed"
    else:
        status = f"within {DEPLOYMENT_LIMIT:g}x: new deployments allowed"
    print(f"\nAccount leverage: {leverage:.2f}x  ({status})")


if __name__ == "__main__":
    main()
