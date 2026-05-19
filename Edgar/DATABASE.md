# DATABASE: myEdgar

| Field       | Value |
|-------------|-------|
| Version     | 20260519 V1 |
| Description | Schema for EDGAR filing storage, metric extraction results, position-level data, alerts, and 8-K events. |

## Tables

### filings
Tracks every downloaded filing.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| ticker | TEXT NOT NULL | |
| cik | TEXT NOT NULL | 10-digit zero-padded |
| filing_type | TEXT NOT NULL | 10-Q, 10-K, 8-K, N-2, N-CEN |
| period_end | DATE NOT NULL | Quarter or fiscal year end |
| filed_date | DATE NOT NULL | SEC filing date |
| accession_number | TEXT NOT NULL | EDGAR accession number |
| raw_html_path | TEXT | Local path to downloaded HTML |
| processed | BOOLEAN DEFAULT FALSE | True after metric extraction |

### metrics
One row per filing per ticker with extracted metric values.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| filing_id | INTEGER FK → filings.id | |
| ticker | TEXT NOT NULL | |
| period_end | DATE NOT NULL | |
| pik_income | DECIMAL | PIK interest income |
| total_investment_income | DECIMAL | |
| pik_pct | DECIMAL | Computed: pik_income / total_investment_income * 100 |
| non_accrual_cost | DECIMAL | At cost basis |
| non_accrual_fair_value | DECIMAL | At fair value |
| total_portfolio_cost | DECIMAL | |
| total_portfolio_fair_value | DECIMAL | |
| non_accrual_cost_pct | DECIMAL | Computed |
| weighted_avg_mark | DECIMAL | portfolio_fair_value / portfolio_cost * 100 |
| nav_per_share | DECIMAL | |
| shares_outstanding | DECIMAL | |
| asset_coverage_ratio | DECIMAL | total_assets / total_borrowings * 100 |
| nii_per_share | DECIMAL | Net investment income per share |
| distributions_per_share | DECIMAL | |
| nii_coverage | DECIMAL | nii_per_share / distributions_per_share |
| unrealized_change | DECIMAL | Net change in unrealized appreciation/depreciation |
| realized_gain_loss | DECIMAL | |
| fee_waiver_amount | DECIMAL | |
| fee_waiver_flag | BOOLEAN DEFAULT FALSE | |
| red_flag_score | INTEGER | Computed Red Flag Index score |
| score_components | TEXT | JSON: per-metric score breakdown |
| extraction_confidence | TEXT | high / medium / low |
| extraction_notes | TEXT | Parser notes and warnings |
| created_at | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | |

### positions
Position-level data from Schedule of Investments.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| filing_id | INTEGER FK → filings.id | |
| ticker | TEXT NOT NULL | BDC ticker (not position ticker) |
| period_end | DATE NOT NULL | |
| company_name | TEXT | Portfolio company name |
| investment_type | TEXT | Senior secured, mezzanine, equity, etc. |
| cost_basis | DECIMAL | |
| fair_value | DECIMAL | |
| mark_pct | DECIMAL | fair_value / cost_basis * 100 |
| is_non_accrual | BOOLEAN DEFAULT FALSE | |
| is_pik | BOOLEAN DEFAULT FALSE | |
| maturity_date | DATE | |
| position_rank | INTEGER | Rank by fair value within filing |

### alerts
Generated alerts when metric thresholds are crossed.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| ticker | TEXT NOT NULL | |
| alert_type | TEXT NOT NULL | pik, non_accrual, nav_decline, fee_waiver, etc. |
| alert_date | DATE NOT NULL | |
| description | TEXT | |
| severity | TEXT | WATCH / ELEVATED / CRITICAL |
| metric_value | DECIMAL | The value that triggered the alert |
| threshold_value | DECIMAL | The threshold that was breached |
| acknowledged | BOOLEAN DEFAULT FALSE | |

### eightk_events
Material events from 8-K filings.

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| ticker | TEXT NOT NULL | |
| filed_date | DATE NOT NULL | |
| item_number | TEXT | 1.01, 5.02, 8.01, etc. |
| event_type | TEXT | distribution_cut, redemption_cap, investigation, etc. |
| description | TEXT | |
| raw_text | TEXT | Extracted relevant passage |
| flagged | BOOLEAN DEFAULT FALSE | True if keyword match |

## CIK Reference

| Ticker | CIK | Notes |
|--------|-----|-------|
| ARCC | 0001278752 | |
| MFIC | 0001655888 | Verify — may conflict with OBDC |
| TCPC | 0001452936 | Under DOJ investigation May 2026 |
| FSCO | 0001552198 | |
| OBDC | 0001655888 | Verify — may conflict with MFIC |
| BXSL | 0001822928 | |
| APO | 0001858681 | |
| ARES | 0001555280 | |
| BX | 0001393818 | |
| BLK | 0001364742 | |
| OWL | 0001823584 | |

**Note:** Verify all CIKs against EDGAR before first run. MFIC and OBDC show the same CIK — this is likely a data error in the initial spec and must be resolved in PreReq 1.

## Open Questions

- Should `score_components` be a TEXT/JSON column or a separate `score_components` table? JSON column is simpler for Phase 1.
- Is `positions` table needed for Phase 1 MVP or only Phase 2? (Spec says Phase 2 adds position-level parsing.)
- Should `eightk_events.raw_text` be stored in the DB or in a separate file (potentially large)?
