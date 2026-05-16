# AI Sales Agent

A multi-agent AI outbound workflow application built with:

- OpenAI Agents SDK
- Gradio
- SendGrid
- Python
- uv

The application simulates a small AI sales organization:
three specialized sales agents generate competing cold outreach emails, an AI evaluation agent selects the strongest version and explains its reasoning, and a separate sending agent executes the approved email after human confirmation.

---

# Features

## Multi-Agent Workflow

The app contains several cooperating AI agents:

| Agent | Responsibility |
|---|---|
| Professional Sales Agent | Writes enterprise-style outreach |
| Engaging Sales Agent | Writes witty/high-engagement outreach |
| Busy Sales Agent | Writes concise outreach |
| Sales Picker Agent | Evaluates drafts and selects the strongest email |
| Send Manager Agent | Sends the approved email via SendGrid |

---

## Human-in-the-Loop Approval

The workflow intentionally separates:

1. AI generation
2. AI evaluation
3. Human review
4. Final AI execution

The email is **not sent automatically** after generation.
The user must explicitly confirm the send action.

This mirrors real-world enterprise AI workflow patterns.

---

## UI

Built with Gradio.

The interface allows users to:

- Generate 3 competing cold email drafts
- Review all generated drafts
- View AI reasoning for the selected email
- Review the final selected email
- Manually confirm sending
- Send the approved email via SendGrid

---

# Product

The demo product is **SynthPilot**,
a fictional AI platform that helps software teams:

- analyze user feedback
- detect product pain points
- generate prioritized feature recommendations

---

# Tech Stack

- Python
- OpenAI Agents SDK
- Gradio
- SendGrid
- asyncio
- uv

---

# Setup

## Install uv

Mac:

```bash
brew install uv