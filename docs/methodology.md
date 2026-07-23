# CoinBucha Signal Methodology (v0.1.0)

> Public methodology = credibility moat. Anyone can audit how a signal is computed.

CoinBucha surfaces **leading, non-price indicators** for Bitcoin and renders them as a
`signal_strength` (0–100), a `direction` (tailwind / headwind / neutral), and a one-line
`why`. **Every signal is information, not financial advice** — it describes an observable
condition, never a recommendation to buy, sell, or hold.

## Signal taxonomy

| ID | Signal | Measures | Status |
|----|--------|----------|--------|
| S1 | Sovereign adoption | State BTC holdings + status changes | Live (MVP) |
| S2 | ETF net flows | Spot-BTC-ETF creations/redemptions | Planned |
| S3 | Corporate treasury | Firms adding BTC to balance sheet | Planned |
| S4 | Hiring velocity | Open roles + 30/90-day delta at BTC firms | MVP (seed data) |
| S5 | On-chain accumulation | HODL waves, exchange outflows | Planned |
| S6 | Policy / regulation | Pro/anti-BTC regulatory events | Planned |

## How `signal_strength` is computed (MVP)

- **S1 Sovereign:** `clamp(40 + holder_states*4 + pipeline_states*6)`. More states holding,
  plus an active legislative pipeline, = stronger structural tailwind. Direction is
  `tailwind` when ≥1 state has announced or proposed legislation.
- **S4 Hiring:** `clamp(50 + pct_change_30d * 1.5)`. Direction is `tailwind` above +3%,
  `headwind` below −3%, else `neutral`. Rationale: teams hire before they ship and grow,
  so aggregate open-role momentum at Bitcoin-native firms is an early demand tell.

These formulas are deliberately simple and transparent for v0.1. They will be backtested
(hiring velocity vs. forward BTC price) before being marketed as predictive, and revised
with versioned changes recorded here.

## Sourcing rules

Primary sources first. Each signal carries a `sources[]` array; sovereign data inherits the
Sovereign Bitcoin Reserve Monitor's citation discipline (primary-source confirmation per
holding). Seed/illustrative values are flagged `seed: true` and must be replaced by live
scraper output before any public or paid use.

## Compliance

CoinBucha marketing and signal surfaces are self-audited against MiCA / FCA / GDPR before
launch using the NorthPoint compliance engine. No surface may present a signal as advice.
