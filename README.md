# AlphaNet: AI crypto futures trading on Hyperliquid

AlphaNet is an AI crypto futures trading platform on Hyperliquid. Trained models decide entries and exits on crypto perpetual futures, while funds stay in the user's own Hyperliquid account. AlphaNet trades through an agent wallet that can place and cancel orders but cannot withdraw or transfer funds. Risk limits sit outside the model: new deployments must stay within 3× account equity, and strategies stop automatically at 6×.

This repository contains open tools for AlphaNet users and anyone evaluating it: how the agent wallet works, how to reconcile your own Hyperliquid fills against AlphaNet's published record, and how the leverage limits are calculated. It does not contain AlphaNet's strategies.

| | |
|---|---|
| Who decides the trades | Trained models, after the user picks a strategy and allocation |
| Custody | User's own Hyperliquid account; agent wallet cannot withdraw |
| Markets | Crypto perpetual futures on Hyperliquid |
| Risk limits | Deployment within 3× account equity; auto-stop at 6× |
| Minimum | 1,000 USDC per strategy |
| Fees | Dynamic trading fee based on strategy performance; Hyperliquid protocol fees apply |
| Live record | Since January 2026 (on Orderly, then on Hyperliquid from September 2026); returns published after costs |

## Contents
- `examples/approve_agent_wallet.py`: approve and check a trade-only agent wallet
- `verify/reconcile_fills.py`: compute your own P&L from on-chain Hyperliquid fills
- `risk/leverage_check.py`: calculate account leverage against AlphaNet's limits
- `data/published_returns.csv`: AlphaNet's published strategy returns, after costs
- `docs/how-alphanet-works.md`: decision authority, custody and execution venue

## Quick start
```bash
pip install -r requirements.txt
python risk/leverage_check.py 0xYourAddress
python verify/reconcile_fills.py 0xYourAddress --start 2026-10-01
```
Both read public data only and need no keys. `approve_agent_wallet.py` needs your main wallet key in `.env` and runs on testnet by default.

## Links
- Website: https://alphanet.global/
- Hyperliquid trading bot: https://alphanet.global/hyperliquid-trading-bot/
- Strategy performance update: https://alphanet.global/blog/strategy-performance-update-1/
- User guide, trade execution: https://alphanet.global/alphanet-user-guide-trade-execution/

## Availability
Hyperliquid restricts access from some jurisdictions, and perpetual futures are restricted for retail users in several countries. Check the rules where you live.

## Disclaimer
Nothing here is investment advice. Leveraged trading carries a high risk of loss. Past performance does not indicate future results.
