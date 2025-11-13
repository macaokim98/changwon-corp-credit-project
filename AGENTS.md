# Repository Guidelines

## Project Structure & Module Organization
- `src/changwon_credit/`: Core package (ETL, analytics, reports, Dash UI, templates). Key files include `cli.py`, `report_md.py`, `report_typst.py`, `dash_app.py`, and `templates/credit_report.typ`.
- `config/`: Runtime configuration (`config.yaml`) controlling company metadata, paths, and Typst output options.
- `data_raw/`, `data_processed/`: Generated during pipeline runs; contain CSV, Parquet, and SQLite outputs.
- `reports/`: Generated Markdown (`doosan_credit.md`), Typst/PDF (`034020_credit_report.*`), and Plotly figures.
- `docs/`: Run books and tutorials; `docs/run_commands.md` captures operational quick-start steps.
- `tests/`: Pytest suite focusing on report rendering, chart generation, and pipeline plumbing.

## Build, Test, and Development Commands
- `pip install --break-system-packages -e .[dev]`: Install dependencies in editable mode (run inside each environment or venv).
- `changwon-credit --config config/config.yaml`: Full pipeline—fetch FnGuide data, compute metrics, emit Markdown + Typst outputs.
- `typst compile reports/034020_credit_report.typ reports/034020_credit_report.pdf`: Rebuild PDF only after editing story text.
- `python -m changwon_credit.dash_app [--port 8050 --no-debug]`: Launch Dash dashboard; auto-picks a free port if the requested one is busy.
- `pytest`: Run all tests; required before any PR.

## Coding Style & Naming Conventions
- Follow PEP 8 (4-space indentation, snake_case functions, PascalCase classes). Keep modules small; prefer helper functions in `src/changwon_credit`.
- Markdown/Typst files use human-readable headings; keep tables aligned and encoded in UTF-8.
- Avoid reformatting generated data files; treat anything under `data_*` and `reports/` as build artifacts.

## Testing Guidelines
- Pytest with `tests/` mirror modules (e.g., `test_report_typst.py`). Name tests `test_<behavior>` and use fixtures/tmp_path for filesystem work.
- Run `pytest` locally before opening a PR; ensure Typst CLI is installed so rendering tests succeed.
- Add regression tests when touching analytics math, Typst templating, or Dash callbacks.

## Commit & Pull Request Guidelines
- Follow conventional, action-oriented commit messages (`feat: add glossary cards`, `fix: escape typst recommendation text`).
- Each PR should include: purpose summary, linked issues (if any), test evidence (`pytest`), and screenshots for UI/Dash changes or generated reports.
- Keep PRs focused; split large refactors into reviewable chunks. Update docs (`docs/*.md`, `AGENTS.md`) whenever behavior or commands change.
