from pathlib import Path

import pandas as pd

from changwon_credit.models import CreditConfig, CreditStory
from changwon_credit.report_typst import render_typst_report


def test_render_typst_report(tmp_path):
    cfg = CreditConfig(
        company_name="TestCo",
        company_code="000000",
        industry="Test",
        years=3,
        data_source="Test",
        raw_dir=Path("raw"),
        processed_dir=Path("processed"),
        sqlite_path=Path("db.sqlite"),
        report_path=tmp_path / "report.md",
        analyst="QA",
        currency="KRW bn",
        bank_view="Test View",
        typst_enabled=True,
        typst_compile_pdf=False,
        typst_output_dir=tmp_path,
        typst_template=None,
    )
    metrics = pd.DataFrame(
        {
            "year": [2021, 2022],
            "company_code": ["000000", "000000"],
            "revenue": [100.0, 120.0],
            "operating_income": [10.0, 12.0],
            "ebitda": [12.0, 14.0],
            "net_income": [8.0, 9.0],
            "free_cash_flow": [5.0, 6.0],
            "interest_expense": [2.0, 2.0],
            "total_liabilities": [80.0, 85.0],
            "equity": [60.0, 65.0],
            "current_assets": [40.0, 42.0],
            "current_liabilities": [20.0, 21.0],
            "operating_cash_flow": [8.0, 9.0],
            "investment_outflows": [4.0, 4.5],
            "debt_to_ebitda": [6.0, 6.2],
            "net_debt_to_ebitda": [5.0, 5.2],
            "ocf_to_debt": [0.1, 0.11],
            "fcf_to_debt": [0.05, 0.06],
            "ocf_to_capex": [2.0, 2.1],
            "altman_z_score": [2.5, 2.6],
            "pd_estimate": [0.03, 0.028],
            "dscr": [1.4, 1.5],
        }
    )
    story = CreditStory(
        highlights=["Test highlight"],
        strengths=["Test strength"],
        risks=["Test risk"],
        recommendation="Test rec",
    )
    scenarios = pd.DataFrame(
        {
            "scenario": ["보수", "기준"],
            "revenue": [90.0, 100.0],
            "operating_income": [9.0, 10.0],
            "ebitda": [11.0, 12.0],
            "free_cash_flow": [4.0, 5.0],
            "interest_coverage": [2.5, 3.0],
            "dscr": [1.2, 1.4],
            "fcf_margin": [0.04, 0.05],
            "pd_estimate": [0.04, 0.03],
        }
    )
    figures = []

    typst_path, pdf_path = render_typst_report(
        cfg,
        metrics,
        story,
        scenarios,
        figures,
        output_dir=cfg.typst_output_dir,
        compile_pdf=cfg.typst_compile_pdf,
    )
    assert typst_path.exists()
    content = typst_path.read_text(encoding="utf-8")
    assert "TestCo" in content
    assert "자료: Plotly Charts" in content
