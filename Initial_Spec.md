# CreditBubble: Private Credit Stress Intelligence System
## Initial Specification — May 2026

---

## INTENT - THIS IS THE AUTHORS INTENT for INTENT.md

This system replicates the analytical process used by top trading desks (e.g., Millennium, Citadel) to systematically read SEC filings and identify stress signals before they are widely recognized. The goal is to generate actionable long/short trading signals by detecting deterioration in large organizations books.  The specific area of current interest
is Private Credit Organizations — specifically Business Development Companies (BDCs) and alternative asset managers — using publicly available data.

We would like to replicate some business rules that top analysts use when discussing what has been revealed in the filings.  The interesting point is that they focused on 
particular parts of the filings and could extrapolate on credit quality at financial institutions based on behavior.  

This project is to read the filings.  

Phase 1 core thesis: private credit funds mark illiquid assets quarterly using internal models with every incentive to be optimistic. Stress signals appear in the filings many quarters before a fund cuts its distribution, caps redemptions, or faces a regulatory investigation. While true analyists will for sure know the market better than we can do, these signals will certainly beat most investors - few humans have the time to read and analyze these documents - investment companies do - and i want a private trading algorithm  with signals and analytics over time... 

There may be some document model training but i would like to have that done as much as possible preprocessing in python to minimize context.  Use other techniques to minimize LLM context as large documents will lower accuracy and cost more. 

---

## Target Universe

### Tier 1 — Publicly Traded BDCs (Primary Focus)
These file 10-Qs with EDGAR and are the richest data sources.

| Ticker | Name | Manager | Notes |
|--------|------|---------|-------|
| ARCC | Ares Capital Corporation | Ares Management | Largest BDC by AUM |
| MFIC | MidCap Financial Investment Corp | Apollo Global | Already showing NAV decline |
| TCPC | BlackRock TCP Capital Corp | BlackRock | Under DOJ investigation, 19% NAV cut Jan 2026 |
| FSCO | FS Credit Opportunities Corp | FS Investments | User's benchmark — closed-end, no redemption risk |
| OBDC | Blue Owl Capital Corporation | Blue Owl | Large retail-distributed BDC |
| BXSL | Blackstone Secured Lending Fund | Blackstone | Listed Blackstone BDC |
| CGBD | TCG BDC (Carlyle) | Carlyle | Mid-size BDC |
| TPVG | TriplePoint Venture Growth | TriplePoint | Tech-focused, higher risk |

### Tier 2 — Management Company Stocks (Potential Shorts)
These are the parent managers. Stress in Tier 1 funds eventually damages their fee income, fundraising ability, and reputation.

| Ticker | Name | Key Exposure |
|--------|------|-------------|
| APO | Apollo Global Management | MidCap Financial, AAPL credit, $3B fund sale signal |
| ARES | Ares Management | ARCC, direct lending, capped redemptions at 5% |
| BX | Blackstone | BCRED, BXSL, BREIT — massive retail private credit |
| BLK | BlackRock | TCPC under DOJ investigation |
| OWL | Blue Owl Capital | OBDC, heavy BDC origination |
| KKR | KKR & Co | Infrastructure credit, private lending |

### Tier 3 — Non-Traded / Interval Funds (Limited Direct Data, Monitored via 8-Ks)
| Fund | Manager | Red Flag Status |
|------|---------|----------------|
| BCRED | Blackstone | $3.2B in redemptions, non-accruals 0.6% to 2.4% in one quarter |
| Ares Direct Lending | Ares | Capped redemptions at 5%, requests at 11.6% |
| Apollo Direct Lending | Apollo | Weighing $3B fund sale |

---

## Data Sources and Download Process

### Primary Source: SEC EDGAR

All BDC filings are publicly available via EDGAR. The system must download and parse:

1. 10-Q (quarterly reports) — filed within 45 days of quarter end. Primary data source.
2. 10-K (annual reports) — filed within 60-75 days of fiscal year end. Includes audited financials and full portfolio schedule.
3. 8-K (material events) — filed within 4 business days. Critical for catching distribution cuts, NAV announcements, and redemption cap announcements in real time.
4. N-2 / N-CEN (for registered investment companies) — supplemental data for some funds.

### EDGAR API Endpoints

# Get all filings for a company by CIK number
https://data.sec.gov/submissions/CIK{10-digit-CIK}.json

# Search for recent filings by ticker
https://efts.sec.gov/LATEST/search-index?q=%22{TICKER}%22&dateRange=custom&startdt={DATE}&enddt={DATE}&forms=10-Q

# Full text search across all filings
https://efts.sec.gov/LATEST/search-index?q=%22payment+in+kind%22&forms=10-Q&dateRange=custom&startdt=2025-01-01

# Get specific filing index
https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={TICKER}&type=10-Q&dateb=&owner=include&count=10

# Direct filing content (HTML)
https://www.sec.gov/Archives/edgar/data/{CIK}/{accession-number}/{primary-document}.htm

### CIK Numbers for Target Universe

| Ticker | CIK |
|--------|-----|
| ARCC | 0001278752 |
| MFIC | 0001655888 |
| TCPC | 0001452936 |
| FSCO | 0001552198 |
| OBDC | 0001655888 |
| BXSL | 0001822928 |
| APO | 0001858681 |
| ARES | 0001555280 |
| BX | 0001393818 |
| BLK | 0001364742 |
| OWL | 0001823584 |

Note: Verify all CIKs against EDGAR before first run. CIKs are permanent and do not change.

### Download Protocol

For each ticker in target universe:
  1. GET submissions JSON from EDGAR API
  2. Extract accession numbers for all 10-Q filings from past 8 quarters
  3. For each accession number:
     a. GET filing index page
     b. Identify primary document (usually the .htm file)
     c. Download and store raw HTML
     d. Parse using extraction logic (see below)
  4. Also monitor 8-K feed daily for material events
  5. Store all raw files locally with timestamp and filing
