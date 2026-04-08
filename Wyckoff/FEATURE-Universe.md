# Feature: Asset Universe

**Purpose:** Define the proxy ETF (or futures ticker) per asset class bucket. Selection criterion: largest AUM within the asset class — institutional money flows are detectable in volume because large funds use these instruments.

## Phase 1 Universe (11 buckets — equity sectors only)

Phase 1 starts here for signal discovery. The XL series is uniform, liquid, and has 25+ years of history.

| Bucket | Ticker | ETF Name | Approx AUM |
|--------|--------|----------|------------|
| Technology | XLK | Technology Select Sector SPDR | ~$74B |
| Financials | XLF | Financial Select Sector SPDR | ~$42B |
| Healthcare | XLV | Health Care Select Sector SPDR | ~$39B |
| Energy | XLE | Energy Select Sector SPDR | ~$38B |
| Industrials | XLI | Industrial Select Sector SPDR | ~$21B |
| Consumer Discretionary | XLY | Consumer Discretionary SPDR | ~$20B |
| Utilities | XLU | Utilities Select Sector SPDR | ~$16B |
| Communication Services | XLC | Communication Services SPDR | ~$14B |
| Consumer Staples | XLP | Consumer Staples Select Sector SPDR | ~$14B |
| Materials | XLB | Materials Select Sector SPDR | ~$7B |
| Real Estate | XLRE | Real Estate Select Sector SPDR | ~$6B |

**Benchmark (non-tradeable, required for cross-sectional calculations):**

| Role | Ticker | Name | Approx AUM |
|------|--------|------|------------|
| US Broad Market | SPY | SPDR S&P 500 ETF | ~$580B |

## Phase 2 Universe (full ~40 buckets)

### Fixed Income

| Bucket | Ticker | ETF Name | Approx AUM | Notes |
|--------|--------|----------|------------|-------|
| Broad US Bond | AGG | iShares Core U.S. Aggregate Bond | ~$110B | Largest bond ETF |
| Investment Grade Corporate | LQD | iShares iBoxx Investment Grade Corp | ~$35B | |
| Long Treasury | TLT | iShares 20+ Year Treasury Bond | ~$50B | |
| Mid Treasury | IEF | iShares 7-10 Year Treasury Bond | ~$30B | |
| High Yield Corporate | HYG | iShares iBoxx High Yield Corp | ~$16B | |
| TIPS | TIP | iShares TIPS Bond | ~$20B | |
| Short Treasury | SHY | iShares 1-3 Year Treasury Bond | ~$20B | |

### Commodities

| Bucket | Ticker | ETF Name | Approx AUM | Notes |
|--------|--------|----------|------------|-------|
| Gold | GLD | SPDR Gold Shares | ~$65B | Largest commodity ETF by far |
| Silver | SLV | iShares Silver Trust | ~$12B | |
| Broad Commodities | PDBC | Invesco Optimum Yield Diversified Commodity | ~$4B | |
| Oil (WTI) | USO | United States Oil Fund | ~$2B | Smaller; WTI futures (CL=F) more liquid |
| Copper | CPER | United States Copper Index Fund | ~$300M | Small; COPX (miners, ~$2B) is alternative |
| Natural Gas | UNG | United States Natural Gas Fund | ~$500M | Small; NG=F futures more liquid |

**Note on commodities:** ETF AUM is smaller than equity ETFs because institutional commodity exposure is primarily via futures, not ETFs. Volume and open interest on GC=F (gold futures) and CL=F (oil futures) far exceeds ETF volume. Consider supplementing ETF price data with futures volume where available.

### International Equity

| Bucket | Ticker | ETF Name | Approx AUM | Notes |
|--------|--------|----------|------------|-------|
| Developed Markets ex-US | VEA | Vanguard FTSE Developed Markets | ~$110B | Larger than EFA (~$50B) |
| Emerging Markets | VWO | Vanguard FTSE Emerging Markets | ~$80B | Larger than EEM (~$20B) |
| China | FXI | iShares China Large-Cap | ~$5B | |

### Forex

| Bucket | Ticker | Name | Notes |
|--------|--------|------|-------|
| USD Index | UUP | Invesco DB US Dollar Index Bullish | ~$700M; DXY is the reference but not directly tradeable |
| Euro | FXE | Invesco CurrencyShares Euro Trust | ~$600M |
| Japanese Yen | FXY | Invesco CurrencyShares Japanese Yen | ~$300M |
| British Pound | FXB | Invesco CurrencyShares British Pound | ~$100M |

**Note on forex:** Currency ETF AUM is small relative to the actual FX market. Forex volume signal is less reliable from ETF data; futures tickers (6E=F, 6J=F) have more representative volume but shorter yfinance history.

### Crypto

| Bucket | Ticker | ETF Name | Approx AUM | Notes |
|--------|--------|----------|------------|-------|
| Bitcoin | IBIT | iShares Bitcoin Trust | ~$50B | Launched Jan 2024; use BTC-USD for pre-2024 history |
| Ethereum | ETHA | iShares Ethereum Trust | ~$5B | Launched Jul 2024; use ETH-USD for pre-2024 history |

**Note on crypto:** Spot ETFs launched in 2024 — historical data before that date requires direct crypto tickers (BTC-USD, ETH-USD). Signal engine should handle the ticker swap automatically.

### Alternatives

| Bucket | Ticker | ETF Name | Approx AUM | Notes |
|--------|--------|----------|------------|-------|
| REITs | VNQ | Vanguard Real Estate ETF | ~$30B | Much larger than XLRE (~$6B) |
| Infrastructure | PAVE | Global X US Infrastructure Development | ~$8B | |
| Volatility | ^VIX | CBOE VIX Index | N/A | Index only; not tradeable — used as macro signal input |

## Configuration

The universe is stored in `config/universe.yaml`. Phase 1 ships with only the 11 equity sector ETFs active. All Phase 2 tickers are defined in the file but `is_active: false`. Operator activates additional buckets via the Settings page without code changes.

## Open Questions

- Copper: CPER (pure commodity futures exposure, small) vs COPX (copper miners, larger but equity-like) — depends on whether operator wants pure commodity price signal or industry signal
- Natural gas: UNG is small and has roll-cost issues as a futures ETF; NG=F futures may be a better raw signal source
