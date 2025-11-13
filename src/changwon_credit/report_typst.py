from __future__ import annotations

import subprocess
from importlib import resources
from pathlib import Path
from typing import Optional

import pandas as pd

from .models import CreditConfig, CreditStory


def render_typst_report(
    config: CreditConfig,
    metrics: pd.DataFrame,
    story: CreditStory,
    scenarios: pd.DataFrame,
    figures: list[dict] | None = None,
    *,
    template_path: Path | None = None,
    output_dir: Path | None = None,
    compile_pdf: bool = True,
) -> tuple[Path, Optional[Path]]:
    """Render a Typst report (source + optional PDF)."""

    template_source = (
        Path(template_path)
        if template_path
        else resources.files("changwon_credit").joinpath("templates/credit_report.typ")
    )
    template = template_source.read_text(encoding="utf-8")

    perf_table = _format_table(
        ["연도", "매출", "영업이익", "EBITDA", "순이익", "FCF"],
        [
            [
                str(int(row["year"])),
                _fmt_currency(row["revenue"]),
                _fmt_currency(row["operating_income"]),
                _fmt_currency(row["ebitda"]),
                _fmt_currency(row["net_income"]),
                _fmt_currency(row["free_cash_flow"]),
            ]
            for _, row in metrics.sort_values("year").iterrows()
        ],
    )

    ratio_headers = [
        "연도",
        "DSCR",
        "부채/EBITDA",
        "NetDebt/EBITDA",
        "OCF/총부채",
        "FCF/총부채",
        "Altman Z",
        "PD(%)",
    ]
    ratio_rows = []
    for _, row in metrics.sort_values("year").iterrows():
        ratio_rows.append(
            [
                str(int(row["year"])),
                _fmt_number(row.get("dscr")),
                _fmt_number(row.get("debt_to_ebitda")),
                _fmt_number(row.get("net_debt_to_ebitda")),
                _fmt_number(row.get("ocf_to_debt")),
                _fmt_number(row.get("fcf_to_debt")),
                _fmt_number(row.get("altman_z_score")),
                _fmt_percentage(row.get("pd_estimate")),
            ]
        )
    ratio_table = _format_table(ratio_headers, ratio_rows)

    scenario_table = _format_table(
        ["시나리오", "매출", "EBITDA", "DSCR", "PD(%)"],
        [
            [
                row["scenario"],
                _fmt_currency(row["revenue"]),
                _fmt_currency(row["ebitda"]),
                _fmt_number(row["dscr"]),
                _fmt_percentage(row["pd_estimate"]),
            ]
            for _, row in scenarios.iterrows()
        ],
    )

    summary = _bullet_lines(story.highlights)
    strengths = _bullet_lines(story.strengths)
    risks = _bullet_lines(story.risks)
    if story.recommendation:
        recommendation = f"- {_escape_text(story.recommendation)}"
    else:
        recommendation = "- TBD"
    figure_block = _figures_block(figures or [])

    output_root = Path(output_dir) if output_dir else config.report_path.parent
    output_root.mkdir(parents=True, exist_ok=True)
    typst_path = output_root / f"{config.company_code}_credit_report.typ"
    pdf_path = typst_path.with_suffix(".pdf")

    content = (
        template.replace("[[COMPANY_NAME]]", config.company_name)
        .replace("[[SUMMARY_LIST]]", summary)
        .replace("[[PERF_TABLE]]", perf_table)
        .replace("[[RATIO_TABLE]]", ratio_table)
        .replace("[[SCENARIO_TABLE]]", scenario_table)
        .replace("[[STRENGTH_LIST]]", strengths)
        .replace("[[RISK_LIST]]", risks)
        .replace("[[RECOMMENDATION]]", recommendation)
        .replace("[[FIGURE_BLOCK]]", figure_block or "자료: Plotly Charts")
    )
    typst_path.write_text(content, encoding="utf-8")

    pdf_created: Optional[Path]
    if compile_pdf:
        try:
            subprocess.run(
                ["typst", "compile", str(typst_path), str(pdf_path)],
                check=True,
                capture_output=True,
            )
            pdf_created = pdf_path
        except (FileNotFoundError, subprocess.CalledProcessError):
            pdf_created = None
    else:
        pdf_created = None

    return typst_path, pdf_created


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    columns = ", ".join("auto" for _ in headers)
    cells = [f"[{header}]" for header in headers]
    for row in rows:
        cells.extend(f"[{cell}]" for cell in row)
    body = ",\n  ".join(cells)
    return f"#table(columns: ({columns}), {body})"


def _bullet_lines(items: list[str]) -> str:
    if not items:
        return "- 자료 준비 중"
    return "\n".join(f"- {_escape_text(item)}" for item in items)


def _fmt_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:,.1f}"


def _fmt_number(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _fmt_percentage(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def _figures_block(figures: list[dict]) -> str:
    blocks = []
    for fig in figures:
        blocks.append(
            f'#figure(image("{fig["path"]}", width: 100%), caption: [{_escape_text(fig["title"])}])'
        )
    return "\n\n".join(blocks)


def _escape_text(text: str) -> str:
    """Escape Typst control characters."""
    replacements = {
        "\\": "\\\\",
        "<": "\\<",
        ">": "\\>",
        "&": "\\&",
    }
    for target, replacement in replacements.items():
        text = text.replace(target, replacement)
    return text
