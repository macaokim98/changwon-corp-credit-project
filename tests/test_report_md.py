from pathlib import Path

import pandas as pd

from changwon_credit.models import CreditConfig, CreditStory
from changwon_credit.report_md import render_markdown


def test_render_markdown_contains_sections(tmp_path):
    cfg = CreditConfig(
        company_name="TestCo",
        company_code="000000",
        industry="Test",
        years=3,
        data_source="TestSource",
        raw_dir=Path("raw"),
        processed_dir=Path("processed"),
        sqlite_path=Path("processed/db.sqlite"),
        report_path=tmp_path / "report.md",
        analyst="QA",
        currency="KRW bn",
        bank_view="Test Bank",
    )
    metrics = pd.DataFrame(
        {
            "year": [2021, 2022, 2023],
            "revenue": [100.0, 120.0, 140.0],
            "operating_income": [10.0, 12.0, 14.0],
            "operating_cash_flow": [9.0, 11.0, 13.0],
            "ebitda": [12.0, 14.0, 16.0],
            "net_income": [8.0, 9.0, 10.0],
            "free_cash_flow": [5.0, 6.0, 7.0],
            "debt_to_equity": [1.0, 0.9, 0.8],
            "current_ratio": [2.0, 1.8, 1.9],
            "interest_coverage": [3.0, 3.5, 4.0],
            "dscr": [1.4, 1.5, 1.6],
            "roic": [0.11, 0.12, 0.13],
            "debt_to_ebitda": [8.0, 7.0, 6.0],
            "net_debt_to_ebitda": [6.0, 5.5, 5.0],
            "ocf_margin": [0.09, 0.09, 0.09],
            "ocf_to_debt": [0.1, 0.11, 0.12],
            "fcf_to_debt": [0.05, 0.06, 0.07],
            "ocf_to_capex": [2.0, 2.2, 2.4],
            "altman_z_score": [2.5, 2.6, 2.8],
            "pd_estimate": [0.03, 0.028, 0.025],
            "lgd_proxy": [0.4, 0.38, 0.36],
            "capex_ratio": [0.04, 0.045, 0.05],
            "op_margin": [0.1, 0.1, 0.1],
            "ebitda_margin": [0.12, 0.12, 0.12],
            "fcf_margin": [0.05, 0.05, 0.05],
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
            "scenario": ["보수", "기준", "낙관"],
            "revenue": [90.0, 100.0, 110.0],
            "operating_income": [9.0, 10.0, 12.0],
            "ebitda": [11.0, 12.0, 14.0],
            "free_cash_flow": [4.0, 5.0, 6.0],
            "interest_coverage": [2.5, 3.0, 3.5],
            "dscr": [1.2, 1.4, 1.6],
            "fcf_margin": [0.04, 0.05, 0.055],
            "pd_estimate": [0.04, 0.03, 0.02],
        }
    )

    figures = [
        {"title": "Chart 1", "path": "figures/chart1.png"},
        {"title": "Chart 2", "path": "figures/chart2.png"},
    ]

    md = render_markdown(cfg, metrics, story, scenarios, figures)
    assert "# TestCo 여신분석 리포트" in md
    assert "## 5. 여신관점 스토리라인" in md
    assert "Test rec" in md
    assert "## 7. 시각화" in md
    assert "figures/chart1.png" in md
