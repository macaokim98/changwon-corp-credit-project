from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

from changwon_credit.analytics import build_scenarios, compute_credit_metrics
from changwon_credit.etl import run_pipeline
from changwon_credit.glossary import GLOSSARY
from changwon_credit.models import CreditConfig, load_config
from changwon_credit.visuals import (
    _coverage_chart,
    _performance_chart,
    _risk_chart,
    _scenario_chart,
)

DEFAULT_CONFIG = Path("config/config.yaml")
MENU_KEYS: tuple[Literal["overview", "charts", "glossary", "downloads"], ...] = (
    "overview",
    "charts",
    "glossary",
    "downloads",
)
MENU_LABELS = {
    "overview": "Dashboard",
    "charts": "Charts",
    "glossary": "Glossary",
    "downloads": "Downloads",
}


def _apply_light_theme() -> None:
    """Inject CSS for a clean white background with dark typography."""

    st.markdown(
        """
        <style>
            :root { color-scheme: light; }
            .stApp {
                background: linear-gradient(180deg, #ffffff 0%, #f7f7f7 60%, #f0f0f5 100%);
                color: #111111;
            }
            section[data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.95);
                color: #111111;
                border-right: 1px solid rgba(0,0,0,0.08);
                box-shadow: 0 0 20px rgba(0,0,0,0.08);
            }
            section[data-testid="stSidebar"] .stRadio > label,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] label {
                color: #111111;
            }
            .stButton>button, .stDownloadButton>button {
                background: #111111;
                color: #fff;
                border: none;
                border-radius: 6px;
            }
            .stButton>button:hover, .stDownloadButton>button:hover {
                background: #333333;
                transform: translateY(-1px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }
            div[data-testid="metric-container"] {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 14px;
                padding: 16px;
                border: 1px solid rgba(0,0,0,0.08);
                box-shadow: 0 8px 16px rgba(0,0,0,0.08);
                color: #111111;
            }
            div[data-testid="stMarkdown"] p {
                color: #202124;
            }
            .stTabs [data-baseweb="tab-list"] { gap: 12px; }
            .stTabs [data-baseweb="tab"] {
                background: rgba(0,0,0,0.04);
                border-radius: 999px;
                color: #202124;
            }
            .stTabs [aria-selected="true"] {
                background: #111111;
                color: #ffffff;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_metrics(config_path: str) -> tuple[pd.DataFrame, CreditConfig]:
    """Run the ETL/analytics pipeline once and cache the result for reruns."""

    cfg = load_config(Path(config_path))
    merged = run_pipeline(cfg)
    metrics = compute_credit_metrics(merged)
    return metrics, cfg


def _latest_row(metrics: pd.DataFrame) -> pd.Series:
    return metrics.sort_values("year").iloc[-1]


def _format_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def _format_multiple(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.1f}x"


def render_summary(metrics: pd.DataFrame, cfg: CreditConfig) -> None:
    latest = _latest_row(metrics)
    st.subheader("Key KPIs")
    kpi_cols = st.columns(3)
    kpi_cols[0].metric(
        label=f"{int(latest['year'])} Revenue ({cfg.currency})",
        value=f"{latest['revenue']:.1f}",
        delta=f"{latest['revenue_growth'] * 100:.1f}% YoY"
        if pd.notna(latest.get("revenue_growth"))
        else None,
    )
    kpi_cols[1].metric(
        label="DSCR",
        value=_format_multiple(latest.get("dscr")),
        delta="Target ≥ 1.5x",
    )
    kpi_cols[2].metric(
        label="PD Estimate",
        value=_format_pct(latest.get("pd_estimate")),
        delta="Altman derived",
    )
    st.caption("Three cards keep the mobile viewport clean and scannable.")


def render_glossary() -> None:
    st.subheader("Glossary")
    for item in GLOSSARY:
        st.markdown(
            f"**{item.code}** — {item.meaning}\n\n"
            f"- Usage: {item.usage}\n"
            f"- Plain language: {item.kid_friendly}"
        )
        st.divider()


def render_charts(metrics: pd.DataFrame, cfg: CreditConfig, shock: float) -> None:
    st.subheader("Plotly Charts")
    perf_tab, coverage_tab, risk_tab, scenario_tab = st.tabs(
        ["Performance", "Coverage", "Risk", "Scenario"]
    )
    perf_tab.plotly_chart(_light_chart(_performance_chart(metrics, cfg)), use_container_width=True)
    perf_tab.caption(
        "성과 탭은 최근 연도별 매출 영업이익 잉여현금흐름 추이를 나란히 보여 주면서 헤드라인 성장률과 실제 현금창출력이 "
        "동시에 움직이는지, 투자나 운전자본 변동 때문에 엇갈리는지 직관적으로 파악하도록 돕습니다."
    )
    coverage_tab.plotly_chart(_light_chart(_coverage_chart(metrics)), use_container_width=True)
    coverage_tab.caption(
        "커버리지 탭은 DSCR 막대와 이자보상배율 선을 겹쳐 배치해 현금 기준 부채 상환 여유와 손익 기준 이자 커버 능력을 동시에 비교하도록 도와 "
        "NH농협 내부 1.5배 목표 대비 어느 해에 여유가 부족했는지 빠르게 설명할 수 있게 합니다."
    )
    risk_tab.plotly_chart(_light_chart(_risk_chart(metrics)), use_container_width=True)
    risk_tab.caption(
        "리스크 탭은 Altman Z 막대와 PD 궤적을 겹쳐 보여 레버리지나 수익성 저하가 어느 순간부터 Grey Zone 또는 Distress Zone 으로 떨어졌는지, "
        "그에 따라 부도확률이 어떻게 급등하는지 스토리화 할 수 있도록 해 줍니다."
    )
    scenarios = build_scenarios(metrics, shock=shock)
    scenario_tab.plotly_chart(
        _light_chart(_scenario_chart(scenarios)),
        use_container_width=True,
    )
    scenario_tab.caption(
        "시나리오 뷰는 슬라이더에서 지정한 충격률을 매출 영업이익 OCF FCF 에 동시에 적용해 DSCR 과 PD 가 얼마나 민감하게 움직이는지 직관적으로 보여 줍니다. "
        "보수 기준 낙관 각각의 막대는 시나리오별 DSCR 추정치를 뜻하고 선형 궤적은 동일 조건에서 재계산된 PD 변화를 나타냅니다. "
        "충격률을 올려 보수 케이스가 1.5 배 아래로 떨어지는 순간을 찾으면 농협 내부 위험 기준을 설명하기 쉽습니다. "
        "낙관 케이스도 함께 비교하면 정상화 속도와 투자 재원 회수 논리를 한 문장으로 정리할 수 있습니다. "
        "또한 3개 시나리오의 FCF 대비 부채 여력 변화를 언급하면 심사역이 질문하기 전에 중요한 포인트를 선제적으로 전달할 수 있고, "
        "사용자 입장에서는 쇼크 버튼을 움직이며 자연스럽게 이야기 구조를 연습하게 됩니다. 매우 유용합니다."
    )


def render_downloads(metrics: pd.DataFrame, cfg: CreditConfig) -> None:
    st.subheader("Downloads")
    st.download_button(
        label="Download metrics CSV",
        data=metrics.to_csv(index=False),
        file_name=f"{cfg.company_code}_credit_metrics.csv",
        mime="text/csv",
    )
    st.markdown(
        "- Full Markdown/Typst reports live under `reports/` after running `changwon-credit --config config/config.yaml`.\n"
        "- Need only a PDF refresh? Run `typst compile reports/<code>_credit_report.typ ...`."
    )


def _light_chart(fig):
    """Apply light theme colors to Plotly figures."""

    return fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#202124"),
    )


def main() -> None:
    st.set_page_config(
        page_title="Changwon Credit Mobile",
        page_icon="📊",
        layout="wide",
    )

    st.title("Changwon Credit Mobile")
    st.caption("A streamlined Streamlit view tuned for mobile bankers.")

    st.sidebar.header("Mobile Menu")
    config_path = st.sidebar.text_input("Config path", value=str(DEFAULT_CONFIG))
    selected_menu = st.sidebar.radio(
        "Navigate",
        options=list(MENU_KEYS),
        format_func=lambda key: MENU_LABELS[key],
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Need external access? Add `--server.address 0.0.0.0`.")

    _apply_light_theme()

    with st.spinner("Fetching FnGuide snapshots and calculating metrics..."):
        metrics, cfg = load_metrics(config_path)

    if selected_menu == "overview":
        render_summary(metrics, cfg)
        st.info("Use pinch zoom or taps to explore Plotly charts on mobile.")
    elif selected_menu == "charts":
        shock_percent = st.sidebar.slider(
            "Scenario sensitivity (±%)", min_value=5, max_value=20, step=1, value=10
        )
        render_charts(metrics, cfg, shock=shock_percent / 100)
    elif selected_menu == "glossary":
        render_glossary()
    elif selected_menu == "downloads":
        render_downloads(metrics, cfg)
    else:
        st.warning("Unknown menu. Please pick again from the sidebar.")


if __name__ == "__main__":
    main()
