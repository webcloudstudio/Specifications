# Ideas: Wyckoff

Raw observations and improvement ideas. Not yet actionable.
Process with the command: "process ideas" in an interactive session.

## Inbox

- (add ideas here)

## Phase 2 Roadmap

**Polygon.io paid data** — Replace yfinance with Polygon.io Starter (~$29/month) for reliable EOD data and options flow. Options unusual activity scanner is a stronger institutional leading indicator than equity volume alone. Trigger: operator subscribes.

**Sub-industry granularity** — Expand from 11 sector ETFs to ~74 industry-level ETFs (iShares, SPDR, VanEck). Minimum volume threshold needed to filter illiquid ETFs. Signal engine already works — just more rows. Trigger: Phase 1 signals validated.

**Individual security signals** — Run Wyckoff signal engine per holding, not just sector proxies. Requires Finviz or yfinance for constituent sector mapping (~slow for >100 tickers). UI adds "Holdings" tab. Trigger: operator wants per-holding analysis.

**ML signal refinement** — Walk-forward logistic regression + random forest to optimize composite score weights per asset class. scikit-learn + optuna. Constraint: small dataset (~10k rows Phase 1) — prefer simple models; regularization mandatory. Trigger: 1+ year of feature matrix history.

**Automated weekly report** — Scheduled PDF/email summary: top sell signals, phase changes, flow shifts. Jinja2 → HTML → PDF (weasyprint). Email via SMTP. Trigger: operator wants offline delivery.

**Multi-timeframe analysis** — Weekly and monthly signal aggregation alongside daily. Higher-timeframe signals more reliable for position-level decisions. UI adds timeframe toggle.

**Sector constituent aggregation** — Replace ETF proxies with true industry aggregations from constituent data (~500–2,000 stocks). Requires overnight batch and careful rate management (or paid Polygon). Heaviest lift in roadmap.
