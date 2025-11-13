from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml

KRW_100M_TO_BN = 0.1  # Convert 억 KRW to billion KRW


@dataclass(slots=True)
class CreditConfig:
    company_name: str
    company_code: str
    industry: str
    years: int
    data_source: str
    raw_dir: Path
    processed_dir: Path
    sqlite_path: Path
    report_path: Path
    analyst: str
    currency: str
    bank_view: str
    typst_enabled: bool = True
    typst_compile_pdf: bool = True
    typst_output_dir: Path | None = None
    typst_template: Path | None = None


@dataclass(slots=True)
class FinancialStatements:
    income: pd.DataFrame
    balance: pd.DataFrame
    cashflow: pd.DataFrame


@dataclass(slots=True)
class CreditStory:
    highlights: List[str]
    strengths: List[str]
    risks: List[str]
    recommendation: str


def load_config(path: str | Path) -> CreditConfig:
    config_path = Path(path)
    with config_path.open(encoding="utf-8") as fp:
        raw_cfg: Dict[str, Any] = yaml.safe_load(fp)

    company = raw_cfg.get("company", {})
    data = raw_cfg.get("data", {})
    paths = raw_cfg.get("paths", {})
    report = raw_cfg.get("report", {})

    code_value = company.get("code", "")
    if isinstance(code_value, int):
        company_code = f"{code_value:06d}"
    else:
        company_code = str(code_value)

    typst_cfg = report.get("typst", {})
    output_dir = typst_cfg.get("output_dir")
    template_path = typst_cfg.get("template")

    return CreditConfig(
        company_name=company.get("name", "Unknown Company"),
        company_code=company_code,
        industry=company.get("industry", ""),
        years=int(data.get("years", 3)),
        data_source=data.get("source", "FnGuide SVD_Finance"),
        raw_dir=Path(paths.get("raw_dir", "data_raw")),
        processed_dir=Path(paths.get("processed_dir", "data_processed")),
        sqlite_path=Path(paths.get("sqlite_path", "data_processed/credit.db")),
        report_path=Path(paths.get("report_path", "reports/credit.md")),
        analyst=report.get("analyst", "Analyst"),
        currency=report.get("currency", "KRW billion"),
        bank_view=report.get("bank_view", "Credit Review"),
        typst_enabled=bool(typst_cfg.get("enabled", True)),
        typst_compile_pdf=bool(typst_cfg.get("compile_pdf", True)),
        typst_output_dir=Path(output_dir) if output_dir else None,
        typst_template=Path(template_path) if template_path else None,
    )
