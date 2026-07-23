#!/usr/bin/env python3
"""
CoinBucha MCP server (local stdio edition).

Exposes Bitcoin-pure, alternative-signal intelligence to AI agents as MCP tools,
a resource, and a prompt. This standalone server reads the SAME live, public
signal snapshots the dashboard serves at https://coinbucha.com — so it stays in
sync with the site and needs no local data pipeline.

Tools:
    scan_signals             ranked composite signal feed (the money tool)
    get_hiring_signal        BTC-native hiring velocity
    get_sovereign_reserves   sovereign BTC holdings
    get_treasury_holdings    corporate BTC treasury holdings
    get_etf_flows            spot BTC ETF net flows (when configured)
    get_network_signal       network hashrate level + 30/90-day trend
    get_daily_brew           today's machine-readable signal digest
Resource:
    coinbucha://methodology  how every signal is computed (public credibility moat)
Prompt:
    morning_bitcoin_brief    one-shot template to render the Brew

GUARDRAIL: every response is data + `why`. No tool returns buy/sell advice.

Prefer the hosted server (no install): connect any MCP client over Streamable HTTP
to  https://coinbucha.com/api/mcp  . This local server is for offline/dev use.

Run (dev):
    pip install -r requirements.txt
    python3 server.py                  # stdio transport
Inspect:
    uv run mcp dev server.py
"""

import json
import os
import urllib.request
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Live, public signal snapshots (the same files the dashboard renders).
DATA_BASE = os.environ.get("COINBUCHA_DATA_URL", "https://coinbucha.com").rstrip("/")
DOCS_DIR = Path(__file__).resolve().parent / "docs"

DISCLAIMER = (
    "Information, not financial advice. CoinBucha signals describe observable "
    "conditions, not recommendations to buy, sell, or hold any asset."
)

mcp = FastMCP("coinbucha")


def _load(name: str) -> dict:
    """Fetch a public signal snapshot from coinbucha.com (no cache)."""
    req = urllib.request.Request(
        f"{DATA_BASE}/{name}",
        headers={"User-Agent": "coinbucha-mcp/0.1"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


# ─── Tools ────────────────────────────────────────────────────────────────────
@mcp.tool()
def scan_signals(min_strength: int = 0, direction: str | None = None,
                 signal_types: list[str] | None = None) -> dict:
    """Ranked composite feed of Bitcoin signals.

    Args:
        min_strength: only return signals with signal_strength >= this (0-100).
        direction: filter by 'tailwind', 'headwind', or 'neutral'.
        signal_types: filter by type, e.g. ['sovereign_adoption','hiring_velocity'].
    """
    data = _load("signals.json")
    signals = data["signals"]
    if signal_types:
        signals = [s for s in signals if s["type"] in signal_types]
    if direction:
        signals = [s for s in signals if s["direction"] == direction]
    signals = [s for s in signals if s["signal_strength"] >= min_strength]
    signals = sorted(signals, key=lambda s: s["signal_strength"], reverse=True)
    return {
        "as_of": data["meta"]["generated_at"],
        "btc_price_usd": data["meta"].get("btc_price_usd"),
        "count": len(signals),
        "signals": signals,
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_hiring_signal(company: str | None = None) -> dict:
    """Bitcoin-native hiring velocity (open roles + 30/90-day deltas).

    Args:
        company: optional company name filter (case-insensitive substring).
    """
    hiring = _load("hiring.json")
    companies = hiring["companies"]
    if company:
        q = company.lower()
        companies = [c for c in companies if q in c["company"].lower()]
    enriched = []
    for c in companies:
        d30 = c["open_roles"] - c["open_roles_30d_ago"]
        d90 = c["open_roles"] - c["open_roles_90d_ago"]
        enriched.append({
            **c,
            "delta_30d": d30,
            "delta_90d": d90,
            "pct_30d": round(d30 / c["open_roles_30d_ago"] * 100, 1) if c["open_roles_30d_ago"] else None,
        })
    return {
        "as_of": hiring["meta"]["generated_at"][:10],
        "companies": enriched,
        "note": hiring["meta"].get("note"),
        "why": "Teams staff up before they ship and grow; rising open-role counts are an early demand tell.",
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_sovereign_reserves(country: str | None = None, tier: int | None = None) -> dict:
    """Sovereign Bitcoin holdings, ranked.

    Args:
        country: optional country name/code filter (case-insensitive substring).
        tier: optional tier filter (1 = largest holders).
    """
    sov = _load("sovereigns.json")
    rows = sov["sovereigns"]
    if country:
        q = country.lower()
        rows = [r for r in rows if q in r["country_name"].lower() or q == r.get("country_code", "").lower()]
    if tier is not None:
        rows = [r for r in rows if r.get("tier") == tier]
    rows = sorted(rows, key=lambda r: r["holdings_btc"], reverse=True)
    return {
        "as_of": sov["meta"]["generated_at"],
        "btc_price_usd": sov["meta"].get("btc_price_usd"),
        "count": len(rows),
        "sovereigns": rows,
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_treasury_holdings() -> dict:
    """Corporate Bitcoin treasury holdings: total BTC held by public companies + top holders."""
    t = _load("treasury.json")
    return {
        "as_of": t.get("as_of"),
        "total_btc": t.get("total_btc"),
        "company_count": t.get("company_count"),
        "total_value_usd": t.get("total_value_usd"),
        "top": t.get("top"),
        "why": "Corporate treasury accumulation is structural institutional demand.",
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_etf_flows() -> dict:
    """Spot Bitcoin ETF net flows (latest day + trailing 5/30-day) — institutional demand."""
    try:
        etf = _load("etf.json")
    except Exception:
        return {"available": False, "note": "ETF flow data not yet configured.", "disclaimer": DISCLAIMER}
    return {
        "as_of": etf.get("latest_date"),
        "latest_flow_usd": etf.get("latest_flow_usd"),
        "net_flow_5d_usd": etf.get("net_flow_5d_usd"),
        "net_flow_30d_usd": etf.get("net_flow_30d_usd"),
        "why": "Net ETF creations/redemptions are a direct read on institutional demand.",
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_network_signal() -> dict:
    """Bitcoin network hashrate level and 30/90-day trend (miner conviction / security)."""
    net = _load("network.json")
    return {
        "as_of": net.get("as_of"),
        "hashrate_eh": net.get("hashrate_eh"),
        "pct_30d": net.get("pct_30d"),
        "pct_90d": net.get("pct_90d"),
        "why": "Rising hashrate reflects growing miner commitment and network security.",
        "disclaimer": DISCLAIMER,
    }


@mcp.tool()
def get_daily_brew() -> dict:
    """Today's machine-readable signal digest (the CoinBucha Daily Brew)."""
    data = _load("signals.json")
    return data["daily_brew"]


# ─── Resource ─────────────────────────────────────────────────────────────────
@mcp.resource("coinbucha://methodology")
def methodology() -> str:
    """How every CoinBucha signal is computed. Public = credibility moat."""
    path = DOCS_DIR / "methodology.md"
    if path.exists():
        return path.read_text()
    return "Methodology document not found."


# ─── Prompt ───────────────────────────────────────────────────────────────────
@mcp.prompt()
def morning_bitcoin_brief() -> str:
    """One-shot template to render the CoinBucha Daily Brew from live signals."""
    return (
        "You are CoinBucha's signal desk. Call get_daily_brew and scan_signals, then "
        "write a tight morning brief titled 'CoinBucha Daily Brew'. For each signal give "
        "the strength, direction, and the one-line `why`. Lead with the strongest signal. "
        "End with the disclaimer verbatim. Do NOT give buy/sell advice — describe conditions only."
    )


if __name__ == "__main__":
    mcp.run()
