import pandas as pd

from changwon_credit.analytics import (
    build_credit_story,
    build_scenarios,
    compute_credit_metrics,
)


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "company_code": ["034020"] * 3,
            "year": [2021, 2022, 2023],
            "revenue": [100.0, 120.0, 150.0],
            "gross_profit": [30.0, 32.0, 40.0],
            "operating_income": [10.0, 12.0, 15.0],
            "pretax_income": [8.0, 10.0, 12.0],
            "net_income": [6.0, 7.0, 9.0],
            "interest_expense": [2.0, 2.5, 2.0],
            "total_assets": [200.0, 220.0, 250.0],
            "total_liabilities": [100.0, 110.0, 120.0],
            "equity": [100.0, 110.0, 130.0],
            "current_assets": [80.0, 90.0, 100.0],
            "current_liabilities": [40.0, 45.0, 50.0],
            "noncurrent_assets": [120.0, 130.0, 150.0],
            "noncurrent_liabilities": [60.0, 65.0, 70.0],
            "operating_cash_flow": [8.0, 14.0, 16.0],
            "investing_cash_flow": [-5.0, -6.0, -7.0],
            "financing_cash_flow": [-3.0, -4.0, -5.0],
            "investment_outflows": [4.0, 5.0, 6.0],
            "non_cash_expense": [2.0, 2.0, 2.0],
            "non_cash_income": [0.0, 0.0, 0.0],
            "ending_cash": [20.0, 22.0, 24.0],
        }
    )


def test_compute_credit_metrics_produces_ratios():
    metrics = compute_credit_metrics(_sample_frame())
    latest = metrics.iloc[-1]
    assert latest["ebitda"] == 17.0  # 15 operating + 2 non-cash add-back
    assert round(latest["debt_to_equity"], 2) == 0.92
    assert round(latest["interest_coverage"], 2) == 8.5
    assert "roic" in latest
    assert "altman_z_score" in latest
    assert "dscr" in latest
    assert "pd_estimate" in latest
    assert "ocf_to_debt" in latest
    assert "debt_to_ebitda" in latest
    assert "net_debt_to_ebitda" in latest
    assert "capex_ratio" in latest
    assert "ocf_to_capex" in latest
    assert "revenue_growth" in metrics.columns


def test_build_credit_story_generates_sections():
    metrics = compute_credit_metrics(_sample_frame())
    story = build_credit_story(metrics, "TestCo")
    assert story.highlights
    assert story.recommendation


def test_build_scenarios_outputs_three_cases():
    metrics = compute_credit_metrics(_sample_frame())
    scenarios = build_scenarios(metrics, shock=0.1)
    assert list(scenarios["scenario"]) == ["보수", "기준", "낙관"]
    assert "interest_coverage" in scenarios.columns
    assert "pd_estimate" in scenarios.columns
    assert "dscr" in scenarios.columns
