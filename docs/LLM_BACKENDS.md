# LLM Backends — NL message generation

## Version 1.0 | 2026-06-25

The Cop & Thief match requires each move to carry a short **natural-language
message** ("Moving north cautiously"). This text is **cosmetic** — our actor
(`HeuristicActor` / `QTableActor`) decides the move; the LLM only narrates it.
So a small **free** model is more than enough, and none of our tests or offline
training need an LLM at all. An LLM is only needed for a live
`run_match.py --mode actor` (or `--mode llm`) run.

## Where the LLM is called

The submodule's `Gatekeeper`
(`agent-orchestration-course-t6-common/src/game/shared/gatekeeper.py`) is the
single LLM entry point. It selects a backend **at construction**:

- `ANTHROPIC_API_KEY` set → Anthropic cloud API (`anthropic` SDK).
- otherwise → **Ollama** at `POST {OLLAMA_BASE_URL}/api/chat` (native Ollama
  protocol: no auth header, reply read from `data["message"]["content"]`).

`run_match.py` builds `Gatekeeper(model=os.environ.get("LLM_MODEL") or None)`, so
**`LLM_MODEL`** picks the model and **`OLLAMA_BASE_URL`** picks the endpoint.

## The three options

| Backend | Cost | Local install | API key | Submodule support |
|---------|------|---------------|---------|-------------------|
| **Ollama** | free | yes (model download) | no | native |
| **OpenRouter** | free tier | no | yes | via our adapter |
| **Anthropic** | paid | no | yes | native |

Pick **one**. They are mutually exclusive providers for the same job.

### Option A — Ollama (e.g. local laptop or an AWS/VPS)

No adapter needed. Install Ollama, pull a small model, then set in `.env`:

```
OLLAMA_BASE_URL=http://localhost:11434      # or http://<vps-host>:11434
LLM_MODEL=llama3.2
# leave ANTHROPIC_API_KEY unset
```

`ollama pull llama3.2` once. On a VPS, run `ollama serve` and open the port (or
SSH-tunnel it); point `OLLAMA_BASE_URL` at the host.

### Option B — OpenRouter (free cloud models, no local model)

OpenRouter is OpenAI-format with Bearer auth, which the submodule can't call
directly. Our **adapter** (`scripts/openrouter_adapter.py`) presents an
Ollama-compatible `POST /api/chat` and forwards to OpenRouter — **no submodule
change**.

1. Start the adapter (reads `OPENROUTER_API_KEY` from your environment / `.env`):

   ```bash
   uv run python scripts/openrouter_adapter.py
   # listening on http://localhost:11500/api/chat
   ```

2. Point the submodule at it in `.env`:

   ```
   OLLAMA_BASE_URL=http://localhost:11500
   LLM_MODEL=meta-llama/llama-3.2-3b-instruct:free   # any OpenRouter model id
   OPENROUTER_API_KEY=sk-or-...
   # leave ANTHROPIC_API_KEY unset
   ```

3. Run the match as usual (`run_match.py --mode actor ...`).

Adapter env vars: `OPENROUTER_API_KEY` (required), `OPENROUTER_BASE_URL`
(default `https://openrouter.ai/api/v1`), `ADAPTER_PORT` (default `11500`, kept
distinct from Ollama's `11434` so both backends can coexist).

### Option C — Anthropic (paid, native)

```
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-opus-4-8     # optional; this is the Gatekeeper default
```

## Troubleshooting

- **Match hangs at "waiting for servers"** — that's the MCP server health check,
  not the LLM. Check the server subprocess logs.
- **`OPENROUTER_API_KEY is not set`** from the adapter — export it before
  starting the adapter, or put it in the `.env` you load.
- **Anthropic used unexpectedly** — `ANTHROPIC_API_KEY` is set; unset it to fall
  back to the Ollama/adapter path.
- **OpenRouter 4xx** — the adapter forwards OpenRouter's error body and status;
  check the model id is a valid OpenRouter slug and your key has access.
- **Wrong model on Ollama** — `LLM_MODEL` must name a model you've `ollama pull`ed.
