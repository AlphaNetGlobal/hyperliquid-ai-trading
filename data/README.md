# Published returns

`published_returns.csv` holds every strategy return AlphaNet has published on alphanet.global, after trading costs, as stated in [Strategy performance update 1](https://alphanet.global/blog/strategy-performance-update-1/) (21 October 2026); losing periods are included. These are model strategy returns measured from each strategy's start date, not customer account returns, and they are not independently audited.

Columns: `strategy`, `asset`, `window` (since start, latest 90/30 days or 3 weeks), `period_start`, `period_end`, `return_pct_after_costs`, `approximate` (yes where the source says "approximately"), `live_since`, `venue`, `source`. The file is updated in the same commit as each website performance update.
