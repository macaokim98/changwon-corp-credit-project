## Changwon Corporate Credit – Doosan Enerbility

Python pipeline that fetches three years of actual financial statements for Doosan Enerbility (034020) from FnGuide, normalizes them into a local analytics warehouse (CSV/Parquet/SQLite), and produces a markdown credit memo aligned with the guide in `가이드.md`.

### Key Features
- **Direct web fetch** of income, balance sheet, and cash-flow statements (FnGuide `SVD_Finance` endpoint).
- **Deterministic ETL** that stores raw CSV snapshots, curated Parquet tables, and an analytics-ready SQLite database.
- **Credit analytics layer** that calculates leverage, liquidity, profitability, and cash-coverage metrics plus heuristics for strengths/risks.
- **Risk metrics pack** (ROIC, DSCR, Altman Z, PD/LGD proxies, FCF/부채, OCF 마진) + NH 기준 시나리오 스트레스테스트.
- **Markdown + Plotly visuals** that produce banker-friendly memo plus high-res charts (실적/커버리지/Altman/시나리오) under `reports/figures/`.
- **Interactive Dash dashboard** (`python -m changwon_credit.dash_app`) for live exploration of FCF/DSCR/PD trends and scenario sliders.
- **CLI & tests** so the workflow can run end-to-end or step-by-step (`changwon-credit run`).

### Quick Start
```bash
# 1. Install deps
pip install --break-system-packages -e .

# 2. Run the pipeline (fetch -> transform -> report)
changwon-credit --config config/config.yaml

# 3. Inspect artifacts
ls data_raw           # raw FnGuide snapshots (CSV)
ls data_processed     # parquet tables + SQLite db
cat reports/doosan_credit.md
```

### Typst PDF & Dashboard
- `changwon-credit --config config/config.yaml` now additionally writes `reports/<code>_credit_report.typ` and tries to compile a PDF via Typst (install Typst CLI for auto-PDF).
- To view the interactive dashboard: `python -m changwon_credit.dash_app` (auto-fetches latest data and serves on http://127.0.0.1:8050).
- To open the dark-themed mobile Streamlit UI, run `streamlit run src/changwon_credit/streamlit_mobile_app.py`.
- To smoke-test your Streamlit install without running the full ETL, run `streamlit run src/changwon_credit/streamlit_test.py`.

### Configuration
`config/config.yaml` controls the company, time horizon (default: latest 3 annual periods), and output paths. Adjust the YAML to point at another 창원 상장사 and rerun the CLI—no code changes needed.

### Data Source & Units
- Source: FnGuide `SVD_Finance` (public HTML tables scraped with `pandas.read_html`).
- Scope: Latest three December fiscal years (annual consolidated, IFRS).
- Units: Original data is in KRW 100M; the pipeline converts to KRW billion for readability.

### Testing
```bash
pytest
```
