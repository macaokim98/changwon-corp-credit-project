from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict

import pandas as pd

from .loader import fetch_statements
from .models import CreditConfig, FinancialStatements


def run_pipeline(config: CreditConfig) -> pd.DataFrame:
    raw_tables, statements = fetch_statements(config.company_code, config.years)
    _write_raw_tables(raw_tables, config)
    merged = merge_statements(statements, config.company_code)
    persist_processed(statements, merged, config)
    return merged


def merge_statements(statements: FinancialStatements, company_code: str) -> pd.DataFrame:
    merged = statements.income.merge(statements.balance, on="year", how="outer")
    merged = merged.merge(statements.cashflow, on="year", how="outer")
    merged = merged.sort_values("year").reset_index(drop=True)
    merged.insert(0, "company_code", company_code)
    return merged


def persist_processed(
    statements: FinancialStatements, analytics_df: pd.DataFrame, config: CreditConfig
) -> None:
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    statements.income.to_parquet(config.processed_dir / "fs_income.parquet", index=False)
    statements.balance.to_parquet(
        config.processed_dir / "fs_balance.parquet", index=False
    )
    statements.cashflow.to_parquet(
        config.processed_dir / "fs_cashflow.parquet", index=False
    )
    analytics_df.to_parquet(
        config.processed_dir / "credit_profile.parquet", index=False
    )

    with sqlite3.connect(config.sqlite_path) as conn:
        analytics_df.to_sql("analytics_credit", conn, if_exists="replace", index=False)
        statements.income.assign(company_code=config.company_code).to_sql(
            "financials_income", conn, if_exists="replace", index=False
        )
        statements.balance.assign(company_code=config.company_code).to_sql(
            "financials_balance", conn, if_exists="replace", index=False
        )
        statements.cashflow.assign(company_code=config.company_code).to_sql(
            "financials_cashflow", conn, if_exists="replace", index=False
        )
        pd.DataFrame(
            [
                {
                    "company_code": config.company_code,
                    "company_name": config.company_name,
                    "industry": config.industry,
                }
            ]
        ).to_sql("companies", conn, if_exists="replace", index=False)


def _write_raw_tables(
    tables: Dict[str, pd.DataFrame],
    config: CreditConfig,
) -> None:
    config.raw_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        path = config.raw_dir / f"{config.company_code}_{name}.csv"
        df.to_csv(path, index=False)
