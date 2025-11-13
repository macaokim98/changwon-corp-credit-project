from pathlib import Path

import pandas as pd

from changwon_credit.dash_app import create_app
from changwon_credit.models import CreditConfig


def test_create_app_layout(tmp_path):
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
            "revenue": [100, 120, 130],
            "operating_income": [10, 12, 13],
            "ebitda": [12, 14, 15],
            "free_cash_flow": [5, 6, 7],
            "interest_expense": [2, 2, 2],
            "total_liabilities": [80, 85, 90],
            "equity": [60, 65, 70],
            "current_assets": [40, 42, 45],
            "current_liabilities": [20, 21, 22],
            "operating_cash_flow": [8, 9, 10],
            "investment_outflows": [4, 4, 4],
            "altman_z_score": [2.6, 2.7, 2.8],
            "pd_estimate": [0.03, 0.028, 0.027],
            "dscr": [1.5, 1.6, 1.7],
            "interest_coverage": [3.0, 3.2, 3.4],
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
    app = create_app(metrics, scenarios, cfg)
    assert app.layout is not None
