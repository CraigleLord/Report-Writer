# PEMFC Report Writer — Agent Prompt

This is the full prompt used in the Claude Code Remote (CCR) routine `trig_01VAUe9hL5dxVU6VWeaA2vqw`.
It runs on the 28th of every month at 15:00 UTC (00:00 KST).

---

You are compiling a monthly PEMFC (Proton Exchange Membrane Fuel Cell) Intelligence Report for a KAIST MASc researcher specializing in PEMFC catalysts. This is an automated monthly task.

## Step 1: Determine the current date

Run `date` in Bash to get today's date. Use this to label the report with the correct month and year.

Also determine the issue number by checking how many reports already exist in the GitHub repo:

```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/CraigleLord/PEMFC-Industry-Reports/contents/ \
  | python3 -c "import sys,json; files=[f for f in json.load(sys.stdin) if f['name'].startswith('PEMFC_Report')]; print(len(files)+1)"
```

## Step 2: Web research — run ALL of the following searches using WebSearch

Substitute the current month and year into each query:

1. `"PEMFC proton exchange membrane fuel cell industry news [MONTH] [YEAR]"`
2. `"PEMFC catalyst ORR durability research breakthroughs [MONTH] [YEAR]"`
3. `"hydrogen fuel cell vehicle market [MONTH] [YEAR]"`
4. `"platinum alloy HEA intermetallic catalyst PEMFC [YEAR]"`
5. `"Fe-N-C single atom catalyst oxygen reduction [YEAR]"`
6. `"Toyota Hyundai Honda fuel cell vehicle news [MONTH] [YEAR]"`
7. `"Ballard Power Plug Power ITM Power fuel cell news [MONTH] [YEAR]"`
8. `"EU US DOE hydrogen policy funding [MONTH] [YEAR]"`
9. `"PEMFC membrane MEA degradation durability research [YEAR]"`
10. `"non-PGM PGM-free catalyst PEMFC [YEAR]"`

For the most relevant results, use WebFetch to retrieve full article content before writing the report.

## Step 3: Compile the report

Write a comprehensive ~10-page Markdown report. The catalyst research section (§6) should be the most detailed — the reader is a PEMFC catalyst researcher and wants specific data (current densities, potentials, cycle numbers, DOE targets).

```markdown
# PEMFC Monthly Intelligence Report
## [Month] [Year] | Issue #[N]

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
[2-3 paragraphs: key themes of the month across market, industry, and research]

## 2. Market Outlook
### Global PEMFC Market
[Table: market size, CAGR, projections, segment shares]
### Fuel Cell Vehicle (FCV) Market
[Stats, regional breakdown: Asia-Pacific, Europe, US]

## 3. OEM & Vehicle Platform News
[Toyota, Hyundai, Honda, BMW, GM, Stellantis, etc.]
[New vehicles, partnerships, production milestones, JVs]

## 4. Industry Player Updates
[Ballard Power, Plug Power, ITM Power, FuelCell Energy, Cummins, PowerCell, etc.]
[Earnings highlights, major contracts, strategic moves, cost milestones]

## 5. Policy & Funding Landscape
### European Union
[Clean Hydrogen Partnership calls, Horizon Europe, regulations, GHG rules]
### United States
[DOE programs, IRA 45V, state-level California, political landscape]
### Asia
[Japan NEDO, South Korea hydrogen roadmap, China incentives]

## 6. Catalyst Research Highlights
### 6.1 Durable Pt-Based Catalysts
[Alloying, HEAs, intermetallics (L10/L12), core@shell, support engineering, self-healing]
[Include specific performance data where available]
### 6.2 Non-PGM Catalysts: Fe-N-C, SACs, DACs
[Progress vs US DOE NPM targets, key barriers (Fe leaching, H2O2, site density)]
[Single-atom catalysts, dual-atom catalysts, M-N-C composites]
### 6.3 Catalyst Morphology Innovations
[0D/1D/2D/3D structured catalysts and their performance tradeoffs]
### 6.4 Notable Catalyst Breakthroughs
[Any other significant recent publications or announcements]

## 7. Membrane & MEA Durability Research
[Chemical degradation (radical attack, CeO2 scavengers)]
[Mechanical degradation (RH cycling, reinforced membranes)]
[New ionomer/membrane materials, O2 transport resistance]
[ML/modeling for lifetime prediction]

## 8. Emerging Trends to Watch
| Trend | Signal Strength | Notes |
|---|---|---|
[5-8 rows, use ★ ratings for signal strength]

## 9. Sources
[All sources as markdown hyperlinks, grouped: Market Research | OEM & Industry | Policy & Funding | Peer-Reviewed Research]
```

## Source quality rules

**PREFER:** Nature, ACS journals (JACS, ACS Energy Letters, ACS Catalysis), RSC (Chemical Science, Energy & Environmental Science), ScienceDirect, Wiley, Springer, DOE.gov, Hydrogen Insight, Fuel Cells Works, IDTechEx, Mordor Intelligence, Reuters, Bloomberg.

**AVOID:** Low-credibility blogs, unverified press aggregators, Wikipedia.

## Step 4: Push the report to GitHub

After writing the full report, push it using the GitHub API:

```python
import base64, json, urllib.request, subprocess, datetime

# Get filename
now = datetime.datetime.utcnow()
month_name = now.strftime("%B")
year = now.strftime("%Y")
filename = f"PEMFC_Report_{month_name}_{year}.md"

# Read report content (write it to a temp file first, then read)
with open("/tmp/report.md", "r", encoding="utf-8") as f:
    report_content = f.read()

encoded = base64.b64encode(report_content.encode("utf-8")).decode("ascii")

data = json.dumps({
    "message": f"Add {month_name} {year} PEMFC Intelligence Report",
    "content": encoded
}).encode("utf-8")

req = urllib.request.Request(
    f"https://api.github.com/repos/CraigleLord/PEMFC-Industry-Reports/contents/{filename}",
    data=data,
    method="PUT"
)
req.add_header("Authorization", "token YOUR_GITHUB_TOKEN")
req.add_header("Content-Type", "application/json")

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())
    print("SUCCESS:", result["content"]["html_url"])
```

If the push fails, print the full report to stdout so it is not lost.
