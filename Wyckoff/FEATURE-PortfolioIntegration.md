# Feature: Portfolio Integration

**Trigger:** Upload Fidelity positions CSV via Portfolio screen

## Sequence

1. Parse uploaded Fidelity CSV (filename pattern: `Portfolio_Positions_Apr-08-2026.csv`) — match columns by name, not position
2. For each holding, look up ticker in `config/portfolio_mapping.yaml`
3. Unmapped tickers: attempt yfinance sector lookup as fallback; flag for manual review if still unresolved
4. Compute current weight per bucket (sum of holding values / total portfolio value)
5. Load target weights from `target_weights` table (managed via web interface)
6. Compute drift (current % − target %) per bucket
7. Join with current W001 (phase) and composite sell/buy scores (latest date)
8. Apply rebalancing rule: "Trim" if drift >+2% AND sell_score elevated; "Add" if drift <−2% AND buy_score elevated; "Hold" otherwise
9. Compute proposed trades: dollar amount to buy/sell per bucket to reach target weight from current portfolio value
10. Render rebalance table and proposed trades on Portfolio screen

## Fidelity CSV Columns (expected)

Account Number, Account Name, Symbol, Description, Quantity, Last Price, Last Price Change, Current Value, Today's Gain/Loss Dollar, Today's Gain/Loss Percent, Total Gain/Loss Dollar, Total Gain/Loss Percent, Cost Basis Per Share, Cost Basis Total, Type

## Reads

- Uploaded Fidelity CSV
- config/portfolio_mapping.yaml
- target_weights (database table)
- signals (W001, sell score, buy score — latest date per bucket)

## Writes

- No persistent write — rebalance output and proposed trades are display-only
- Manual mapping resolutions saveable to portfolio_mapping.yaml via Settings

## Open Questions

-
