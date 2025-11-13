from pathlib import Path

import pandas as pd

from changwon_credit.models import CreditConfig
from changwon_credit.visuals import build_charts


def test_build_charts_creates_files(tmp_path):
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
    )
    metrics = pd.DataFrame(
        {
            "year": [2021, 2022, 2023],
            "company_code": ["000000"] * 3,
            "revenue": [100.0, 120.0, 140.0],
            "operating_income": [10.0, 12.0, 14.0],
            "ebitda": [12.0, 14.0, 16.0],
            "free_cash_flow": [5.0, 6.0, 7.0],
            "interest_expense": [2.0, 2.0, 2.0],
            "interest_coverage": [3.0, 3.5, 4.0],
            "total_liabilities": [80.0, 90.0, 95.0],
            "equity": [60.0, 65.0, 70.0],
            "current_assets": [40.0, 45.0, 50.0],
            "current_liabilities": [20.0, 22.0, 25.0],
            "operating_cash_flow": [8.0, 9.0, 10.0],
            "investment_outflows": [4.0, 4.5, 5.0],
            "altman_z_score": [2.5, 2.7, 2.9],
            "pd_estimate": [0.03, 0.028, 0.025],
            "dscr": [1.5, 1.6, 1.7],
        }
    )
    scenarios = pd.DataFrame(
        {
            "scenario": ["보수", "기준", "낙관"],
            "revenue": [90, 100, 110],
            "operating_income": [8, 10, 12],
            "ebitda": [9, 11, 13],
            "free_cash_flow": [3, 5, 6],
            "interest_coverage": [2.5, 3.0, 3.5],
            "dscr": [1.2, 1.5, 1.7],
            "fcf_margin": [0.03, 0.04, 0.05],
            "pd_estimate": [0.04, 0.03, 0.02],
        }
    )

    figures = build_charts(metrics, scenarios, cfg)
    figure_dir = cfg.report_path.parent / "figures"
    for fig in figures:
        path = figure_dir / Path(fig["path"]).name
        assert path.exists()
