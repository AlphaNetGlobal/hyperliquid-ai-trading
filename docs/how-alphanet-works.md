# How AlphaNet works

## What AlphaNet is

AlphaNet is an AI crypto futures trading platform on Hyperliquid. It runs automated strategies on crypto perpetual futures for users who keep their funds in their own Hyperliquid accounts. Its first strategies went live in January 2026.

## Who decides the trades

Trained models decide the trades. The user chooses a strategy and how much to allocate to it; the minimum allocation is 1,000 USDC per strategy. In Autopilot mode, once a strategy is deployed it submits orders according to model signals and carries out the end-to-end trading process, including entries, exits, long and short positions. The user can stop a strategy at any time. Positions the user opens by hand stay user-managed.

## Custody

AlphaNet never receives or holds user funds. Funds stay in the user's own Hyperliquid account. AlphaNet trades through an agent wallet (Hyperliquid's API wallet) that the user approves from their main wallet. An agent wallet can sign orders and cancels for the account, but it cannot withdraw or transfer funds; those actions need the main wallet's signature. Stopping a strategy and withdrawing are separate steps, and withdrawals go through Hyperliquid as usual. `examples/approve_agent_wallet.py` shows how an agent wallet is approved and how to list the agents an account has approved.

## Risk limits

AlphaNet's risk limits are enforced at portfolio level, outside the trading models. They are calculated from account equity, strategy allocations and manual net-position notional. New or increased deployments must stay within 3× account equity. At 6×, strategies stop and their positions close, and stopped strategies do not restart automatically. Manual positions are never changed by AlphaNet, though they count toward both ratios. `risk/leverage_check.py` calculates account leverage from public on-chain data and shows where an account stands against both limits.

## Performance and how to check it

AlphaNet publishes strategy returns after trading costs on its blog, starting with [Strategy performance update 1](https://alphanet.global/blog/strategy-performance-update-1/). These are model strategy results measured from each strategy's start date, not customer account returns, and they are not independently audited. The record ran on Orderly until September 2026, when AlphaNet moved to Hyperliquid. The published figures are collected in `data/published_returns.csv`, including losing periods.

Users can check their own results with `verify/reconcile_fills.py`. It reads an address's fills, fees and funding payments from Hyperliquid's public API and reports closed P&L, fees, funding, unrealised P&L and account equity, with deposits and withdrawals excluded. To compare with the published record, use the same period and venue; an individual account's result also depends on its start date, allocation and any manual trades.

## Availability

Hyperliquid restricts access from some jurisdictions, and perpetual futures are restricted for retail users in several countries. Check the rules where you live. Premium strategies have limited capacity; current availability is shown in the trading portal at https://app.alphanet.global/.

Nothing here is investment advice. Leveraged trading carries a high risk of loss.
