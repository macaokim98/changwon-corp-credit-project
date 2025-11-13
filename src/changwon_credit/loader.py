from __future__ import annotations

import logging
import re
from io import StringIO
from typing import Dict, Iterable, List, Tuple

import pandas as pd
import requests

from .models import FinancialStatements, KRW_100M_TO_BN

LOGGER = logging.getLogger(__name__)

FNGUIDE_URL = "https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp"
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Referer": "https://comp.fnguide.com/",
}

INCOME_METRICS = {
    "매출액": "revenue",
    "매출총이익": "gross_profit",
    "영업이익": "operating_income",
    "세전계속사업이익": "pretax_income",
    "당기순이익": "net_income",
    "지배주주순이익": "controlling_net_income",
    "금융원가계산에 참여한 계정 펼치기": "interest_expense",
}

BALANCE_METRICS = {
    "자산": "total_assets",
    "부채": "total_liabilities",
    "자본": "equity",
    "유동자산계산에 참여한 계정 펼치기": "current_assets",
    "유동부채계산에 참여한 계정 펼치기": "current_liabilities",
    "비유동자산계산에 참여한 계정 펼치기": "noncurrent_assets",
    "비유동부채계산에 참여한 계정 펼치기": "noncurrent_liabilities",
}

CASHFLOW_METRICS = {
    "영업활동으로인한현금흐름": "operating_cash_flow",
    "투자활동으로인한현금흐름": "investing_cash_flow",
    "재무활동으로인한현금흐름": "financing_cash_flow",
    "(투자활동으로인한현금유출액)계산에 참여한 계정 펼치기": "investment_outflows",
    "현금유출이없는비용등가산계산에 참여한 계정 펼치기": "non_cash_expense",
    "(현금유입이없는수익등차감)계산에 참여한 계정 펼치기": "non_cash_income",
    "현금및현금성자산의증가": "net_cash_increase",
    "기말현금및현금성자산": "ending_cash",
}


def fetch_statements(
    company_code: str, years: int, session: requests.Session | None = None
) -> Tuple[Dict[str, pd.DataFrame], FinancialStatements]:
    """Download FnGuide tables and normalize them into tidy financial statements."""

    raw_tables = _download_tables(company_code, session=session)
    income = _tidy_statement(raw_tables["income"], INCOME_METRICS, years)
    balance = _tidy_statement(raw_tables["balance"], BALANCE_METRICS, years)
    cashflow = _tidy_statement(raw_tables["cashflow"], CASHFLOW_METRICS, years)

    statements = FinancialStatements(income=income, balance=balance, cashflow=cashflow)
    return raw_tables, statements


def _download_tables(
    company_code: str, session: requests.Session | None = None
) -> Dict[str, pd.DataFrame]:
    code = company_code
    if not code.startswith("A"):
        code = f"A{code}"

    sess = session or requests.Session()
    resp = sess.get(
        FNGUIDE_URL,
        params={"pGB": "1", "gicode": code, "CmpTp": "1"},
        headers=HTTP_HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    dfs = pd.read_html(StringIO(resp.text))
    if len(dfs) < 5:
        raise ValueError("FnGuide response is missing expected tables.")

    LOGGER.info("Fetched %d tables from FnGuide for %s", len(dfs), company_code)
    return {"income": dfs[0], "balance": dfs[2], "cashflow": dfs[4]}


def _tidy_statement(
    df: pd.DataFrame, metric_map: Dict[str, str], years: int
) -> pd.DataFrame:
    """Select the latest `years` annual columns and rename metrics."""

    if df.empty:
        raise ValueError("Received empty DataFrame from FnGuide.")

    data = df.copy()
    first_column = data.columns[0]
    data = data.rename(columns={first_column: "metric"})
    data["metric"] = data["metric"].astype(str).str.strip()
    subset = data[data["metric"].isin(metric_map.keys())].set_index("metric")

    year_columns = _select_annual_columns(subset.columns, years)
    if not year_columns:
        raise ValueError("Unable to locate annual financial columns.")

    numeric_subset = (
        subset[year_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    )
    numeric_subset = numeric_subset.T
    numeric_subset.index = numeric_subset.index.map(
        lambda label: int(re.match(r"(\d{4})", str(label)).group(1))
    )
    numeric_subset.index.name = "year"

    ordered_columns = [metric_map[key] for key in metric_map if key in subset.index]
    renamed = numeric_subset.rename(columns=metric_map)
    renamed = renamed[ordered_columns]
    renamed = renamed.astype(float) * KRW_100M_TO_BN  # convert 억 -> KRW bn
    return renamed.reset_index()


def _select_annual_columns(columns: Iterable[str], years: int) -> List[str]:
    annual = [
        col
        for col in columns
        if isinstance(col, str) and re.match(r"^\d{4}/12$", col.strip())
    ]
    if not annual:
        annual = [
            col for col in columns if isinstance(col, str) and re.match(r"^\d{4}/", col)
        ]
    return annual[-years:]
