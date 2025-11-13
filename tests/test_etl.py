import pandas as pd

from changwon_credit.etl import merge_statements
from changwon_credit.models import FinancialStatements


def test_merge_statements_aligns_years():
    statements = FinancialStatements(
        income=pd.DataFrame({"year": [2022, 2023], "revenue": [100.0, 110.0]}),
        balance=pd.DataFrame({"year": [2022, 2023], "total_assets": [200.0, 210.0]}),
        cashflow=pd.DataFrame({"year": [2022, 2023], "operating_cash_flow": [10.0, 12.0]}),
    )
    merged = merge_statements(statements, "000000")
    assert list(merged["company_code"].unique()) == ["000000"]
    assert "revenue" in merged.columns and "total_assets" in merged.columns
