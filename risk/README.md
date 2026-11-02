# Risk limits

AlphaNet's risk limits are enforced at portfolio level, outside the trading models. They are calculated from account equity, strategy allocations and manual net-position notional. New or increased deployments must stay within 3× account equity. If the ratio reaches 6×, AlphaNet strategies stop and their positions close; stopped strategies do not restart automatically.

Manual positions are never changed by AlphaNet: they stay user-managed, though they count toward both ratios. `leverage_check.py` shows the same calculation from public on-chain data, using total open position notional divided by account equity.
