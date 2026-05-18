---
title: AI Sales Agent
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
pinned: false
---

# AI Sales Agent

A multi-agent outbound email workflow built with the OpenAI Agents SDK, Gradio, and SendGrid.

Three sales agents draft competing cold emails, a picker agent selects the best one with structured JSON output, and a send manager delivers the human-approved message after explicit confirmation.

## Features

### Multi-agent workflow

| Agent | Responsibility |
| --- | --- |
| Professional Sales Agent | Enterprise-style outreach |
| Engaging Sales Agent | Witty, high-engagement outreach |
| Busy Sales Agent | Concise outreach |
| Sales Picker | Chooses the strongest draft and explains why |
| Send Manager | Sends the approved email via SendGrid |

### Two-step UI

1. **Generate and review** — create drafts, view the picker’s choice and reasoning.
2. **Confirm sending** — send is disabled until generation succeeds; inputs changes invalidate the prior selection.

The email is **not sent automatically** after generation.

### Product context

The demo product is **SynthPilot**, a fictional platform for analyzing user feedback and prioritizing features. Agent instructions define the baseline product; the **Product context** field in the UI adds run-specific detail for each generation.

## Project structure

```
ai-sales-agent/
├── app.py                 # Gradio entrypoint (demo.launch)
├── sales_agent/
│   ├── agents_factory.py  # Lazy agent creation (AgentsBundle)
│   ├── config.py          # App constants and status messages
│   ├── email_service.py   # SendGrid delivery
│   ├── errors.py          # User-facing error helpers
│   ├── flows.py           # Generation and send orchestration
│   ├── messages.py        # Per-run prompt templates
│   ├── prompts.py         # Agent system instructions
│   ├── runner.py          # Injectable AgentRunner (Runner.run)
│   ├── schemas.py         # Pydantic models (SalesPickerOutput, GenerationResult)
│   └── ui.py              # Gradio layout and callbacks
└── tests/                 # pytest suite (mocked agents + SendGrid)
```

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended)

## Setup

### 1. Install dependencies

```bash
uv sync
```

For development (includes pytest):

```bash
uv sync --group dev
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=verified-sender@yourdomain.com
```

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Used by the OpenAI Agents SDK |
| `SENDGRID_API_KEY` | SendGrid API key for outbound mail |
| `SENDGRID_FROM_EMAIL` | Verified sender address in SendGrid |

### 3. Run the app

```bash
uv run python app.py
```

Or:

```bash
uv run gradio app.py
```

## Testing

```bash
uv run pytest
```

Tests mock agent runs (`AgentRunner` injection) and SendGrid; no live API calls are required.

## Tech stack

- Python 3.11+
- OpenAI Agents SDK
- Gradio 6
- SendGrid
- Pydantic
- pytest / pytest-asyncio
- uv
