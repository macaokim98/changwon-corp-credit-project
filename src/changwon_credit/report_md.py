from __future__ import annotations

from typing import Sequence

import pandas as pd

from .glossary import GLOSSARY, Acronym
from .models import CreditConfig, CreditStory


def render_markdown(
    config: CreditConfig,
    metrics: pd.DataFrame,
    story: CreditStory,
    scenarios: pd.DataFrame,
    figures: list[dict] | None = None,
) -> str:
    years = metrics["year"].tolist()
    coverage = f"{int(min(years))}~{int(max(years))}"

    perf_cols = [
        ("year", "연도"),
        ("revenue", "매출"),
        ("operating_income", "영업이익"),
        ("ebitda", "EBITDA"),
        ("net_income", "순이익"),
        ("free_cash_flow", "FCF"),
    ]
    ratio_cols = [
        ("debt_to_equity", "부채비율(x)"),
        ("current_ratio", "유동비율(x)"),
        ("interest_coverage", "이자보상배율(x)"),
        ("dscr", "DSCR(x)"),
        ("roic", "ROIC"),
        ("debt_to_ebitda", "부채/EBITDA"),
        ("net_debt_to_ebitda", "NetDebt/EBITDA"),
        ("ocf_margin", "OCF마진"),
        ("ocf_to_debt", "OCF/총부채"),
        ("fcf_to_debt", "FCF/총부채"),
        ("ocf_to_capex", "OCF/CAPEX"),
        ("altman_z_score", "알트만Z"),
        ("pd_estimate", "PD(모형추정)"),
        ("lgd_proxy", "LGD Proxy"),
        ("capex_ratio", "CAPEX/매출"),
        ("op_margin", "영업이익률"),
        ("ebitda_margin", "EBITDA마진"),
        ("fcf_margin", "FCF마진"),
    ]
    perf_table = _mk_table(metrics, perf_cols)
    ratio_table = _mk_table(
        metrics,
        ratio_cols,
        is_ratio=True,
        percent_keys={
            "op_margin",
            "ebitda_margin",
            "fcf_margin",
            "roic",
            "ocf_margin",
            "pd_estimate",
            "lgd_proxy",
            "capex_ratio",
        },
    )
    scenario_table = _mk_scenario_table(scenarios)

    lines = [
        f"# {config.company_name} 여신분석 리포트",
        "",
        f"- 커버리지: {coverage} (최근 {config.years}개 연도)",
        f"- 데이터 출처: {config.data_source}",
        f"- 재무제표 기준: 연결, IFRS, 단위: {config.currency}",
        f"- 목적: {config.bank_view} 관점의 기업여신 심사 참고",
        "",
        "## 0. 핵심 영어 약어 & 활용 맥락",
        "",
        _mk_glossary_table(GLOSSARY),
        "",
        "## 1. 실행 요약",
    ]
    lines += [f"- {item}" for item in story.highlights]
    lines += [
        "",
        "## 2. 실적 및 현금흐름",
        "",
        perf_table,
        "",
        "## 3. 레버리지·커버리지 지표",
        "",
        ratio_table,
        "",
        "## 4. 시나리오 스트레스 체크",
        "",
        scenario_table,
        "",
        "NH농협 내부 기준(DSCR ≥ 1.5x, 모형 PD < 5%) 대비 여신여력 변화를 시뮬레이션.",
        "",
        "## 5. 여신관점 스토리라인",
        "",
        "**강점**",
    ]
    strengths = story.strengths or ["정량 지표에서 도드라지는 강점이 제한적입니다. (추가 데이터 확보 필요)"]
    lines += [f"- {item}" for item in strengths]
    lines += ["", "**리스크**"]
    lines += [f"- {item}" for item in story.risks]
    lines += [
        "",
        "## 6. 제언",
        f"- {story.recommendation}",
        "",
    ]

    if figures:
        lines += [
            "## 7. 시각화",
            "Plotly 차트를 통해 주요 지표 변화를 직관적으로 확인:",
        ]
        for fig in figures:
            lines.append(f"![{fig['title']}]({fig['path']})")
        lines.append("")

    lines.append(f"_작성: {config.analyst}, 뷰: {config.bank_view}_")
    return "\n".join(lines)


def _mk_table(
    metrics: pd.DataFrame,
    columns: Sequence[tuple[str, str]],
    is_ratio: bool = False,
    percent_keys: set[str] | None = None,
) -> str:
    percent_keys = percent_keys or set()
    headers = ["연도"] + [label for key, label in columns if key != "year"]
    rows = []
    for _, row in metrics.sort_values("year").iterrows():
        cells = [str(int(row["year"]))]
        for key, label in columns:
            if key == "year":
                continue
            value = row.get(key)
            if pd.isna(value):
                cells.append("n/a")
                continue
            if "margin" in key or "마진" in label or key in percent_keys:
                cells.append(f"{value * 100:.1f}%")
            elif is_ratio:
                cells.append(f"{value:.2f}")
            else:
                cells.append(f"{value:,.1f}")
        rows.append("| " + " | ".join(cells) + " |")
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    return "\n".join([header_line, separator, *rows])


def _mk_scenario_table(scenarios: pd.DataFrame) -> str:
    columns = [
        ("scenario", "시나리오"),
        ("revenue", "매출"),
        ("operating_income", "영업이익"),
        ("ebitda", "EBITDA"),
        ("free_cash_flow", "FCF"),
        ("interest_coverage", "이자보상배율(x)"),
        ("dscr", "DSCR(x)"),
        ("fcf_margin", "FCF마진"),
        ("pd_estimate", "PD(모형추정)"),
    ]
    headers = [label for _, label in columns]
    rows = []
    for _, row in scenarios.iterrows():
        cells = []
        for key, label in columns:
            value = row.get(key)
            if pd.isna(value):
                cells.append("n/a")
                continue
            if key == "scenario":
                cells.append(str(value))
            elif "마진" in label or "margin" in key:
                cells.append(f"{value * 100:.1f}%")
            elif key in {"interest_coverage", "dscr"}:
                cells.append(f"{value:.2f}")
            elif key == "pd_estimate":
                cells.append(f"{value * 100:.1f}%")
            else:
                cells.append(f"{value:,.1f}")
        rows.append("| " + " | ".join(cells) + " |")
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    return "\n".join([header_line, separator, *rows])


def _mk_glossary_table(items: list[Acronym]) -> str:
    headers = ["약어", "풀네임·정의", "현업 활용"]
    header_line = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    rows = [f"| **{item.code}** | {item.meaning} | {item.usage} |" for item in items]
    return "\n".join([header_line, separator, *rows])
