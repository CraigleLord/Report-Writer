"""
PEMFC Monthly Intelligence Report Writer
========================================
Standalone script to generate and publish a PEMFC intelligence report.
Requires an Anthropic API key and a GitHub PAT with write access to the reports repo.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY="sk-ant-..."
    export GITHUB_TOKEN="github_pat_..."
    export GITHUB_REPO="CraigleLord/PEMFC-Industry-Reports"  # optional override
    python report_writer.py
"""

import os
import base64
import json
import datetime
import urllib.request
import urllib.error
import sys

import anthropic

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "CraigleLord/PEMFC-Industry-Reports")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SEARCH_QUERIES = [
    "PEMFC proton exchange membrane fuel cell industry news {month} {year}",
    "PEMFC catalyst ORR durability research breakthroughs {month} {year}",
    "hydrogen fuel cell vehicle market {month} {year}",
    "platinum alloy HEA intermetallic catalyst PEMFC {year}",
    "Fe-N-C single atom catalyst oxygen reduction {year}",
    "Toyota Hyundai Honda fuel cell vehicle news {month} {year}",
    "Ballard Power Plug Power ITM Power fuel cell news {month} {year}",
    "EU US DOE hydrogen policy funding {month} {year}",
    "PEMFC membrane MEA degradation durability research {year}",
    "non-PGM PGM-free catalyst PEMFC {year}",
]

REPORT_PROMPT = """
You are compiling a monthly PEMFC (Proton Exchange Membrane Fuel Cell) Intelligence Report
for a KAIST MASc researcher specializing in PEMFC catalysts.

Today is {date}. This report covers {month} {year}.

Using the web search results provided below, compile a comprehensive ~10-page Markdown report.
The catalyst research section (§6) should be the most detailed — the reader is a PEMFC catalyst
researcher and wants specific data (current densities, potentials, cycle numbers, DOE targets).

## Web Search Results
{search_results}

## Report Structure

Write the report in this exact format:

# PEMFC Monthly Intelligence Report
## {month} {year} | Issue #{issue_num}

---

## Table of Contents
1. Executive Summary
2. Market Outlook
3. OEM & Vehicle Platform News
4. Industry Player Updates
5. Policy & Funding Landscape
6. Catalyst Research Highlights
7. Membrane & MEA Durability Research
8. Emerging Trends to Watch
9. Sources

---

## 1. Executive Summary
[2-3 paragraphs covering key themes of the month]

## 2. Market Outlook
### Global PEMFC Market
[Include a table with market size, CAGR, projections, segment shares]
### Fuel Cell Vehicle (FCV) Market
[Stats and regional breakdown: Asia-Pacific, Europe, US]

## 3. OEM & Vehicle Platform News
[Toyota, Hyundai, Honda, BMW, GM, etc. — new vehicles, partnerships, JVs]

## 4. Industry Player Updates
[Ballard Power, Plug Power, ITM Power, FuelCell Energy, Cummins, PowerCell, etc.]

## 5. Policy & Funding Landscape
### European Union
### United States
### Asia

## 6. Catalyst Research Highlights
### 6.1 Durable Pt-Based Catalysts
[Alloying, HEAs, intermetallics, core@shell, support engineering — with specific data]
### 6.2 Non-PGM Catalysts: Fe-N-C, SACs, DACs
[Progress vs US DOE NPM targets; key barriers]
### 6.3 Catalyst Morphology Innovations
[0D/1D/2D/3D structured catalysts]
### 6.4 Notable Catalyst Breakthroughs

## 7. Membrane & MEA Durability Research

## 8. Emerging Trends to Watch
[Table: Trend | Signal Strength (★) | Notes]

## 9. Sources
[All sources as markdown hyperlinks, grouped by category]

---
*Report compiled: {date} | Next issue: following month*
*Researcher: KAIST MASc — PEMFC Catalyst Group*
"""


def get_issue_number():
    """Count existing reports in the GitHub repo to determine issue number."""
    if not GITHUB_TOKEN:
        return 1
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{GITHUB_REPO}/contents/",
            headers={"Authorization": f"token {GITHUB_TOKEN}"}
        )
        with urllib.request.urlopen(req) as resp:
            files = json.loads(resp.read())
            count = sum(1 for f in files if f["name"].startswith("PEMFC_Report"))
            return count + 1
    except Exception:
        return 1


def search_web(client, query):
    """Use Claude with web search tool to gather results for a query."""
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": f"Search for: {query}\n\nSummarize the key findings in detail, including specific data points, company names, dates, and links."}]
        )
        result = ""
        for block in response.content:
            if hasattr(block, "text"):
                result += block.text + "\n"
        return result
    except Exception as e:
        return f"[Search failed for '{query}': {e}]"


def generate_report(client, search_results, month, year, issue_num, date_str):
    """Generate the full report using Claude."""
    prompt = REPORT_PROMPT.format(
        date=date_str,
        month=month,
        year=year,
        issue_num=issue_num,
        search_results=search_results
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def push_to_github(content, filename, month, year):
    """Push the report to the GitHub reports repository."""
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN set — skipping push.")
        return None

    encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
    data = json.dumps({
        "message": f"Add {month} {year} PEMFC Intelligence Report",
        "content": encoded
    }).encode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            return result["content"]["html_url"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"GitHub push failed ({e.code}): {body}")
        return None


def main():
    if not ANTHROPIC_API_KEY:
        print("ERROR: Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    now = datetime.datetime.utcnow()
    month = now.strftime("%B")
    year = now.strftime("%Y")
    date_str = now.strftime("%B %d, %Y")
    filename = f"PEMFC_Report_{month}_{year}.md"

    print(f"Generating PEMFC Intelligence Report for {month} {year}...")
    print(f"Target repo: {GITHUB_REPO}")
    print(f"Output file: {filename}\n")

    issue_num = get_issue_number()
    print(f"Issue number: #{issue_num}\n")

    print("Running web searches...")
    all_results = []
    for i, query_template in enumerate(SEARCH_QUERIES, 1):
        query = query_template.format(month=month, year=year)
        print(f"  [{i}/{len(SEARCH_QUERIES)}] {query}")
        result = search_web(client, query)
        all_results.append(f"### Search {i}: {query}\n{result}")

    search_results_text = "\n\n".join(all_results)

    print("\nCompiling report...")
    report = generate_report(client, search_results_text, month, year, issue_num, date_str)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved locally: {filename}")

    print("Pushing to GitHub...")
    url = push_to_github(report, filename, month, year)
    if url:
        print(f"SUCCESS: {url}")
    else:
        print("Push failed. Report content printed below:\n")
        print(report)


if __name__ == "__main__":
    main()
