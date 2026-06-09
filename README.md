# Global AI Readiness Pipeline

## What it does
End-to-end data pipeline analyzing AI readiness across 47 countries and 16 subregions, 
using Stanford HAI 2026 survey data merged with REST Countries API metadata.

## Data Sources
- Stanford HAI AI Index 2026 (fig 9.1.11) — organizational AI readiness survey
- REST Countries API — subregion metadata

## Metrics analyzed
- AI Strategy and Culture
- Support for AI Literacy  
- Responsible AI Governance

## Key findings
- Southern Asia leads all 3 metrics globally (driven by India)
- Northern/Western Europe scores significantly lower than perceived reputation suggests
- Estonia and Latvia show the largest gap between AI literacy support and governance
- Global south countries (Nigeria, Egypt, UAE) outperform Western Europe on composite score

## How to run
```bash
pip install requests pandas matplotlib numpy
python pipeline.py
```

## Outputs
- `subregion_scores.csv` — average scores per subregion
- `top_countries.csv` — top country per subregion
- `literacy_governance_gap.csv` — biggest literacy vs governance gaps
- `subregion_chart.png` — grouped bar chart by subregion
- `europe_chart.png` — Northern & Western Europe breakdown

<!-- ## Skills demonstrated
- REST API integration with error handling (Day 6)
- Pandas data cleaning and pivot operations (Day 2)
- SQL queries with SQLite (Day 3)
- NumPy composite scoring (Day 1 + 4)
- Matplotlib visualization (Day 2)
- OOP pipeline structure (Day 1)
- Git version control (Day 6) -->