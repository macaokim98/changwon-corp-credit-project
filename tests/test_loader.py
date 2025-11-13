import pandas as pd

from changwon_credit.loader import (
    INCOME_METRICS,
    _select_annual_columns,
    _tidy_statement,
)


def test_select_annual_columns():
    cols = ["IFRS(연결)", "2020/12", "2021/12", "2022/12", "전년동기"]
    assert _select_annual_columns(cols, 2) == ["2021/12", "2022/12"]


def test_tidy_statement_converts_units():
    df = pd.DataFrame(
        {
            "IFRS(연결)": ["매출액", "영업이익", "당기순이익"],
            "2021/12": [1000, 100, 50],
            "2022/12": [1200, 140, 60],
            "2023/12": [1400, 160, 80],
            "전년동기": [0, 0, 0],
        }
    )
    tidy = _tidy_statement(df, INCOME_METRICS, years=2)
    assert list(tidy["year"]) == [2022, 2023]
    # 1000 억 -> 100 KRW bn
    assert tidy.loc[tidy["year"] == 2022, "revenue"].iloc[0] == 120.0
    assert "net_income" in tidy.columns
