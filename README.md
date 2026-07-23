# CoinBucha MCP — Bitcoin signal intelligence for AI agents

> **Signal-first Bitcoin intelligence over MCP.** Leading, *non-price* indicators —
> sovereign adoption, hiring velocity, network hashrate, ETF flows, corporate treasuries —
> each as a 0–100 strength, a direction, a one-line `why`, and primary sources.
>
> **Information, not financial advice.** No tool returns a buy/sell/hold recommendation.

This is the public MCP interface for **[CoinBucha](https://coinbucha.com)**. The hosted server
reads the same live signal data the dashboard renders, so the machine face and the human face
never diverge.

## Connect (hosted — recommended, no install)

The server is remote and speaks **Streamable HTTP**. Point any MCP client at:

```
https://coinbucha.com/api/mcp
```

**Claude Desktop / Claude Code** — add a custom connector with that URL, or in
`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coinbucha": {
      "type": "streamable-http",
      "url": "https://coinbucha.com/api/mcp"
    }
  }
}
```

**Cursor / other clients** — add an MCP server with transport `streamable-http` and the URL above.

Free tier is open (IP rate-limited). Higher limits are available with an API key via the
`Authorization: Bearer <key>` header — see [coinbucha.com](https://coinbucha.com).

## Connect (local stdio — offline/dev)

The bundled `server.py` exposes the same tools and fetches the live public snapshots from
`coinbucha.com`, so it needs no local data pipeline.

```bash
pip install -r requirements.txt
python3 server.py            # stdio transport
# inspect: uv run mcp dev server.py
```

```json
{
  "mcpServers": {
    "coinbucha": { "command": "python3", "args": ["server.py"] }
  }
}
```

## Tools

| Tool | Returns |
|------|---------|
| `scan_signals` | Ranked composite signal feed (filter by `min_strength`, `direction`, `signal_types`) — the money tool |
| `get_hiring_signal` | Bitcoin/crypto-infra hiring velocity: open roles + 30/90-day deltas from live ATS boards |
| `get_sovereign_reserves` | Sovereign Bitcoin holdings, ranked (filter by `country` or `tier`) |
| `get_treasury_holdings` | Corporate Bitcoin treasury holdings: total BTC held by public companies + top holders |
| `get_etf_flows` | Spot Bitcoin ETF net flows (latest day + trailing 5/30-day) |
| `get_network_signal` | Bitcoin network hashrate level + 30/90-day trend |
| `get_daily_brew` | Today's machine-readable signal digest (the CoinBucha Daily Brew) |

**Resource** `coinbucha://methodology` — how every signal is computed (see [`docs/methodology.md`](./docs/methodology.md)).
**Prompt** `morning_bitcoin_brief` — one-shot template to render the Daily Brew from live signals.

Every response carries an `as_of` timestamp, a `why`, and a `disclaimer`.

## Example

Call `scan_signals` with `{ "min_strength": 60, "direction": "tailwind" }` → the strongest
structural tailwinds right now, ranked, each with its rationale and sources. Or run the
`morning_bitcoin_brief` prompt for a written digest.

## Methodology & guardrail

Signals are **leading, non-price** indicators rendered as `signal_strength` (0–100), a
`direction`, and a `why`. The full, versioned methodology is public — see
[`docs/methodology.md`](./docs/methodology.md) — because an auditable method is the point.

CoinBucha's public and MCP surfaces are self-audited against MiCA / FCA / GDPR. **No surface
presents a signal as advice.**

## Links

- Dashboard: <https://coinbucha.com>
- MCP endpoint: <https://coinbucha.com/api/mcp>
- Discovery manifest: <https://coinbucha.com/.well-known/mcp.json>

## License

MIT — see [`LICENSE`](./LICENSE). This repository is the public MCP interface and
methodology; the signal-collection pipeline is maintained separately.
