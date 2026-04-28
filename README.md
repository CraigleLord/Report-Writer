# PEMFC Intelligence Report Writer

An automated monthly intelligence report system for PEMFC (Proton Exchange Membrane Fuel Cell) research and industry news. Built for a KAIST MASc PEMFC catalyst researcher.

## What it does

On the 28th of every month, a Claude Code remote agent:
1. Searches the web across 10 topic areas (market, OEM news, catalyst research, policy, membrane science, etc.)
2. Compiles a ~10-page Markdown intelligence report
3. Commits the report to [CraigleLord/PEMFC-Industry-Reports](https://github.com/CraigleLord/PEMFC-Industry-Reports)

## Report structure

Each report covers:
- **Executive Summary**
- **Market Outlook** — PEMFC/FCV market size, CAGR, regional breakdown
- **OEM & Vehicle Platform News** — Toyota, Hyundai, Honda, BMW, GM, etc.
- **Industry Player Updates** — Ballard, Plug Power, ITM Power, FuelCell Energy, etc.
- **Policy & Funding** — EU Clean Hydrogen Partnership, US DOE, Japan/Korea/China
- **Catalyst Research Highlights** — Pt-based durability, non-PGM/Fe-N-C/SAC progress, ORR data vs DOE targets
- **Membrane & MEA Durability Research**
- **Emerging Trends to Watch**
- **Full sourced references**

## Components

| File | Description |
|---|---|
| `README.md` | This file |
| `report_writer.py` | Standalone script — run locally with your Anthropic API key |
| `prompt.md` | The full agent prompt used in the Claude Code Remote routine |
| `routine_config.json` | CCR routine configuration (token redacted) |

## Automated routine

The live scheduled routine runs via Claude Code Remote (CCR):
- **Routine ID:** `trig_01VAUe9hL5dxVU6VWeaA2vqw`
- **Schedule:** 28th of every month at 00:00 KST
- **Manage:** https://claude.ai/code/routines/trig_01VAUe9hL5dxVU6VWeaA2vqw

## Running locally

You can also run `report_writer.py` manually at any time:

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
export GITHUB_TOKEN="your-github-pat-here"
export GITHUB_REPO="CraigleLord/PEMFC-Industry-Reports"
python report_writer.py
```

The script will search for PEMFC news, compile the report, and push it to the reports repo.

## Source quality

The agent is instructed to prefer:
- Academic: Nature, ACS journals, RSC, ScienceDirect, Wiley, Springer
- Industry: Hydrogen Insight, Fuel Cells Works, IDTechEx, Mordor Intelligence
- News: Reuters, Bloomberg, Financial Times
- Policy: DOE.gov, European Commission, Clean Hydrogen Partnership
