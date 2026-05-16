---
title: AI Sales Agent
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.34.2
app_file: app.py
pinned: false
---

# AI Sales Agent

A small multi-agent AI sales email project.

Three sales agents generate different cold email drafts for a fictional AI product. A sales manager agent compares the drafts, selects the best one, and sends it via SendGrid.

## Product

The demo product is **SynthPilot**, a fictional AI tool that helps software teams analyze user feedback, detect product pain points, and generate prioritized feature recommendations.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate