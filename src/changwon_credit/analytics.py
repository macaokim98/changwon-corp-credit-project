from __future__ import annotations

import math
from typing import List

import numpy as np
import pandas as pd

from .models import CreditStory


def compute_credit_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Derive the full NH 여신 정량 팩(현금·레버리지·PD/LGD proxy) from the merged statements."""

    metrics = df.copy()

    # EBITDA와 FCF는 이자/상환 능력의 기초 체력이다.
    metrics["ebitda"] = (
        metrics["operating_income"]
        + metrics.get("non_cash_expense", 0).fillna(0)
        - metrics.get("non_cash_income", 0).fillna(0)
    )
    metrics["free_cash_flow"] = metrics["operating_cash_flow"] - metrics["investment_outflows"]

    # 기본 재무 안전성 지표 (Basel Pillar 2 공시 항목과 유사)
    metrics["debt_to_equity"] = _safe_div(metrics["total_liabilities"], metrics["equity"])
    metrics["current_ratio"] = _safe_div(metrics["current_assets"], metrics["current_liabilities"])
    metrics["interest_coverage"] = _safe_div(metrics["ebitda"], metrics["interest_expense"])

    # 수익성/현금 마진. IFRS 손익만으로는 여신 설명이 어려워 OCF/FCF 마진을 병행한다.
    metrics["op_margin"] = _safe_div(metrics["operating_income"], metrics["revenue"])
    metrics["ebitda_margin"] = _safe_div(metrics["ebitda"], metrics["revenue"])
    metrics["net_margin"] = _safe_div(metrics["net_income"], metrics["revenue"])
    metrics["fcf_margin"] = _safe_div(metrics["free_cash_flow"], metrics["revenue"])
    metrics["ocf_margin"] = _safe_div(metrics["operating_cash_flow"], metrics["revenue"])

    # 투자자본 기반 수익성 (ROIC)과 운전자본 추출
    metrics["working_capital"] = metrics["current_assets"] - metrics["current_liabilities"]
    metrics["invested_capital"] = metrics["total_assets"] - metrics["current_liabilities"]
    metrics["roic"] = _safe_div(metrics["operating_income"], metrics["invested_capital"])

    # 누적 이익은 Altman Z 계산을 위해 필요하므로 회사별 시계열 누적으로 생성한다.
    metrics = metrics.sort_values(["company_code", "year"]).reset_index(drop=True)
    metrics["retained_earnings_proxy"] = metrics.groupby("company_code")["net_income"].cumsum()
    metrics["altman_z_score"] = _altman_z(metrics)

    # 부채 대비 현금창출력: NH IRB 심사 시 FCF/부채와 OCF/부채를 함께 본다.
    metrics["fcf_to_debt"] = _safe_div(metrics["free_cash_flow"], metrics["total_liabilities"])
    metrics["ocf_to_debt"] = _safe_div(metrics["operating_cash_flow"], metrics["total_liabilities"])

    # 레버리지 stress용 추가 지표
    metrics["debt_to_ebitda"] = _safe_div(metrics["total_liabilities"], metrics["ebitda"])
    metrics["net_debt"] = metrics["total_liabilities"] - metrics.get("ending_cash", 0).fillna(0)
    metrics["net_debt_to_ebitda"] = _safe_div(metrics["net_debt"], metrics["ebitda"])

    # CAPEX 관련 비율 (투자 부담 vs OCF 커버리지 체크)
    metrics["capex_ratio"] = _safe_div(metrics["investment_outflows"], metrics["revenue"])
    metrics["ocf_to_capex"] = _safe_div(metrics["operating_cash_flow"], metrics["investment_outflows"])

    # DSCR 계산을 위해 원리금 상환액을 근사(부채 감소분을 원금 상환으로 가정)한다.
    principal_proxy = (
        metrics.groupby("company_code")["total_liabilities"]
        .diff()
        .mul(-1)
        .clip(lower=0)
        .fillna(0)
    )
    metrics["debt_service"] = metrics["interest_expense"] + principal_proxy
    metrics["dscr"] = _safe_div(metrics["operating_cash_flow"], metrics["debt_service"])

    # LGD/EAD proxy: 단기자산 비중이 낮을수록 담보 회수율 저하 → (1 – 유동자산/총자산)
    metrics["lgd_proxy"] = (1 - _safe_div(metrics["current_assets"], metrics["total_assets"])).clip(
        lower=0, upper=1
    )
    metrics["ead_proxy"] = metrics["total_liabilities"]

    # Altman Z 기반 구간형 PD 추정 (chapter에서 언급된 “부도확률” 활용)
    metrics["pd_estimate"] = _pd_from_altman(metrics["altman_z_score"])

    # 성장성/자산 확장 추세 (IRB 모형 가중치용)
    metrics = metrics.sort_values("year").reset_index(drop=True)
    metrics["revenue_growth"] = metrics["revenue"].pct_change()
    metrics["operating_income_growth"] = metrics["operating_income"].pct_change()
    metrics["net_income_growth"] = metrics["net_income"].pct_change()
    metrics["asset_growth"] = metrics["total_assets"].pct_change()
    return metrics


def build_credit_story(metrics: pd.DataFrame, company_name: str) -> CreditStory:
    """Translate metric table into banker-friendly 하이라이트/강점/리스크 문장."""

    ordered = metrics.sort_values("year")
    latest = ordered.iloc[-1]
    first = ordered.iloc[0]
    periods = max(len(ordered) - 1, 1)
    revenue_cagr = _cagr(first["revenue"], latest["revenue"], periods)
    leverage_trend = ordered["debt_to_equity"].mean()
    roic_latest = latest.get("roic")
    altman_latest = latest.get("altman_z_score")
    dscr_latest = latest.get("dscr")
    pd_latest = latest.get("pd_estimate")
    net_debt_to_ebitda = latest.get("net_debt_to_ebitda")
    capex_ratio = latest.get("capex_ratio")

    highlights = [
        f"{company_name} posted {latest['revenue']:.1f} KRW bn revenue in {int(latest['year'])} "
        f"with an operating margin of {_fmt_pct(latest['op_margin'])}.",
        f"EBITDA coverage at {_fmt_num(latest['interest_coverage'])}x, ROIC {_fmt_pct(roic_latest)}, "
        f"DSCR {_fmt_num(dscr_latest)}x and estimated PD {_fmt_pct(pd_latest)} ground repayment views.",
    ]

    strengths: List[str] = []
    if revenue_cagr > 0:
        strengths.append(
            f"Top-line compounded at {_fmt_pct(revenue_cagr)} across the review window."
        )
    if latest["interest_coverage"] > 2:
        strengths.append(
            f"Interest coverage remains healthy at {_fmt_num(latest['interest_coverage'])}x."
        )
    if latest["free_cash_flow"] > 0:
        strengths.append(
            f"Latest-year free cash flow stayed positive at {latest['free_cash_flow']:.1f} KRW bn."
        )
    if _is_valid(roic_latest) and roic_latest > 0.08:
        strengths.append(f"ROIC held at {_fmt_pct(roic_latest)} signaling efficient invested capital use.")
    if _is_valid(dscr_latest) and dscr_latest >= 1.5:
        strengths.append(f"DSCR {_fmt_num(dscr_latest)}x comfortably exceeds NH농협 내부 기준(1.5x).")
    if _is_valid(net_debt_to_ebitda) and net_debt_to_ebitda < 4:
        strengths.append(f"Net Debt/EBITDA {_fmt_num(net_debt_to_ebitda)}x keeps leverage manageable.")

    risks: List[str] = []
    if leverage_trend > 1.5:
        risks.append(
            f"Average debt-to-equity is elevated at {_fmt_num(leverage_trend)}x, "
            "leaving sensitivity to order volatility."
        )
    if latest["operating_cash_flow"] < 0:
        risks.append(
            "Operating cash flow turned negative in the latest period due to working capital swings."
        )
    if latest["fcf_margin"] < 0:
        risks.append("Free cash flow margin is negative, implying reliance on external funding.")
    if _is_valid(altman_latest) and altman_latest < 1.8:
        risks.append(
            f"Altman Z-score at {_fmt_num(altman_latest)} signals heightened default sensitivity."
        )
    if _is_valid(dscr_latest) and dscr_latest < 1.2:
        risks.append("DSCR has slipped below 1.2x threshold, pressuring debt service headroom.")
    if _is_valid(pd_latest) and pd_latest > 0.05:
        risks.append(f"Model-implied PD {_fmt_pct(pd_latest)} suggests elevated risk tier.")
    if _is_valid(net_debt_to_ebitda) and net_debt_to_ebitda > 5:
        risks.append(f"Net leverage stretched to {_fmt_num(net_debt_to_ebitda)}x EBITDA.")
    if _is_valid(capex_ratio) and capex_ratio > 0.08:
        risks.append("CAPEX intensity exceeds 8% of sales, limiting internal deleveraging.")

    if not risks:
        risks.append("Monitor large-project execution risk and energy policy sensitivity.")

    recommendation = (
        "Maintain exposure with covenants on leverage (<2.0x) and interest coverage (>2.5x), "
        "and tie limits to project milestone cash-in milestones."
    )

    return CreditStory(
        highlights=highlights,
        strengths=strengths,
        risks=risks,
        recommendation=recommendation,
    )


def build_scenarios(metrics: pd.DataFrame, shock: float = 0.1) -> pd.DataFrame:
    """Return downside/base/upside coverage summary for the latest year."""

    latest = metrics.sort_values("year").iloc[-1]
    scenarios = []
    definitions = [
        ("보수", 1 - shock),
        ("기준", 1.0),
        ("낙관", 1 + shock),
    ]
    for label, factor in definitions:
        # 매출·현금흐름을 가중치로 조정해 DSCR/PD 변화 민감도를 본다.
        revenue = latest["revenue"] * factor
        ebitda = latest["ebitda"] * factor
        operating_income = latest["operating_income"] * factor
        free_cash_flow = latest["free_cash_flow"] * factor
        ocf = latest["operating_cash_flow"] * factor
        interest_expense = latest["interest_expense"]
        debt_service = latest["debt_service"]
        coverage = _safe_div(pd.Series([ebitda]), pd.Series([interest_expense])).iloc[0]
        dscr = _safe_div(pd.Series([ocf]), pd.Series([debt_service])).iloc[0]
        fcf_margin = _safe_div(pd.Series([free_cash_flow]), pd.Series([revenue])).iloc[0]
        pd_case = _pd_from_altman(pd.Series([latest["altman_z_score"] * factor])).iloc[0]
        scenarios.append(
            {
                "scenario": label,
                "revenue": revenue,
                "operating_income": operating_income,
                "ebitda": ebitda,
                "free_cash_flow": free_cash_flow,
                "interest_coverage": coverage,
                "dscr": dscr,
                "fcf_margin": fcf_margin,
                "pd_estimate": pd_case,
            }
        )
    return pd.DataFrame(scenarios)


def _cagr(start: float, end: float, periods: int) -> float:
    if start <= 0 or end <= 0 or periods <= 0:
        return 0.0
    return (end / start) ** (1 / periods) - 1


def _fmt_pct(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    return f"{value * 100:.1f}%"


def _fmt_num(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    return f"{value:.1f}"


def _safe_div(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denom = denominator.replace(0, pd.NA)
    return numerator / denom


def _is_valid(value: float | None) -> bool:
    return value is not None and not (isinstance(value, float) and math.isnan(value))


def _pd_from_altman(z_scores: pd.Series) -> pd.Series:
    transformed = z_scores.fillna(0)
    safe = transformed >= 3.0
    grey = (transformed >= 1.8) & (transformed < 3.0)
    distress = transformed < 1.8

    pd_values = np.empty(len(transformed), dtype=float)
    pd_values[safe] = 0.01  # Altman Safe Zone → 투자등급 수준으로 가정
    pd_values[grey] = 0.03 + (3.0 - transformed[grey]) * 0.02  # Grey Zone은 3~5% PD 구간
    pd_values[distress] = 0.15 + (1.8 - transformed[distress]) * 0.05  # Distress Zone은 ≥15%로 보수 적용
    return pd.Series(np.clip(pd_values, 0.01, 0.35), index=z_scores.index)


def _altman_z(metrics: pd.DataFrame) -> pd.Series:
    wc_over_assets = _safe_div(metrics["working_capital"], metrics["total_assets"])
    re_over_assets = _safe_div(metrics["retained_earnings_proxy"], metrics["total_assets"])
    ebit_over_assets = _safe_div(metrics["operating_income"], metrics["total_assets"])
    equity_over_liab = _safe_div(metrics["equity"], metrics["total_liabilities"])
    sales_over_assets = _safe_div(metrics["revenue"], metrics["total_assets"])
    return (
        0.717 * wc_over_assets
        + 0.847 * re_over_assets
        + 3.107 * ebit_over_assets
        + 0.420 * equity_over_liab
        + 0.998 * sales_over_assets
    )
