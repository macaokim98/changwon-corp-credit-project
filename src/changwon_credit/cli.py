from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .analytics import build_credit_story, build_scenarios, compute_credit_metrics
from .etl import run_pipeline
from .models import CreditConfig, load_config
from .report_md import render_markdown
from .report_typst import render_typst_report
from .visuals import build_charts

console = Console()
app = typer.Typer(help="Changwon corporate credit analysis CLI.", invoke_without_command=True)


@app.callback(invoke_without_command=True)
def main(config: Path = typer.Option(Path("config/config.yaml"), "--config", "-c")) -> None:
    """Fetch FnGuide data, build analytics tables, and create the markdown report."""

    cfg = load_config(config)
    console.print(f"[bold]Fetching financials for {cfg.company_name} ({cfg.company_code})[/bold]")
    merged = run_pipeline(cfg)

    console.print("Computing credit metrics...")
    credit_df = compute_credit_metrics(merged)
    story = build_credit_story(credit_df, cfg.company_name)
    scenarios = build_scenarios(credit_df)
    figures = build_charts(credit_df, scenarios, cfg)

    report_text = render_markdown(cfg, credit_df, story, scenarios, figures)
    cfg.report_path.parent.mkdir(parents=True, exist_ok=True)
    cfg.report_path.write_text(report_text, encoding="utf-8")

    console.print(f":white_check_mark: Pipeline complete. Report saved to {cfg.report_path}")

    if cfg.typst_enabled:
        typst_path, pdf_path = render_typst_report(
            cfg,
            credit_df,
            story,
            scenarios,
            figures,
            template_path=cfg.typst_template,
            output_dir=cfg.typst_output_dir,
            compile_pdf=cfg.typst_compile_pdf,
        )
        console.print(f":sparkles: Typst source written to {typst_path}")
        if pdf_path:
            console.print(f":page_facing_up: Typst PDF generated at {pdf_path}")
        elif cfg.typst_compile_pdf:
            console.print(":warning: Typst CLI not found or failed; PDF not generated.")
        else:
            console.print(":information_source: Typst PDF generation disabled via config.")
    else:
        console.print(":information_source: Typst generation disabled via config.")
