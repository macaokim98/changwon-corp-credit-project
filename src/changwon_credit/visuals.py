from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .models import CreditConfig


def build_charts(
    metrics: pd.DataFrame,
    scenarios: pd.DataFrame,
    config: CreditConfig,
) -> List[dict]:
    """Create Plotly charts that mirror NH 여신 심사 스토리라인."""

    output_dir = config.report_path.parent / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    artifacts = []
    artifacts.append(
        _save_figure(
            _performance_chart(metrics, config),
            output_dir / "01_performance.png",
            "실적·현금흐름 추세",
        )
    )
    artifacts.append(
        _save_figure(
            _coverage_chart(metrics),
            output_dir / "02_coverage.png",
            "DSCR & Interest Coverage",
        )
    )
    artifacts.append(
        _save_figure(
            _risk_chart(metrics),
            output_dir / "03_altman_pd.png",
            "Altman Z vs PD",
        )
    )
    artifacts.append(
        _save_figure(
            _scenario_chart(scenarios),
            output_dir / "04_scenario.png",
            "Stress Scenario DSCR/PD",
        )
    )
    return artifacts


def _performance_chart(metrics: pd.DataFrame, config: CreditConfig) -> go.Figure:
    df = metrics.sort_values("year")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["year"],
            y=df["revenue"],
            name="매출",
            marker_color="#2E86AB",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["operating_income"],
            name="영업이익",
            mode="lines+markers",
            line={"color": "#F18F01", "width": 3},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["free_cash_flow"],
            name="FCF",
            mode="lines+markers",
            line={"color": "#A23B72", "dash": "dot", "width": 3},
        )
    )
    fig.update_layout(
        title=f"{config.company_name} 실적/현금흐름",
        xaxis_title="연도",
        yaxis_title=f"금액 ({config.currency})",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def _coverage_chart(metrics: pd.DataFrame) -> go.Figure:
    df = metrics.sort_values("year")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["year"],
            y=df["dscr"],
            name="DSCR",
            marker_color="#3C6773",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["interest_coverage"],
            name="이자보상배율",
            mode="lines+markers",
            line={"color": "#F29F05", "width": 3},
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="DSCR & Interest Coverage",
        xaxis_title="연도",
        yaxis_title="DSCR (배)",
        yaxis2=dict(
            title="이자보상배율 (배)",
            overlaying="y",
            side="right",
        ),
        template="plotly_white",
    )
    fig.add_hline(y=1.5, line_dash="dot", line_color="#B80C09", annotation_text="NH 기준 1.5x")
    return fig


def _risk_chart(metrics: pd.DataFrame) -> go.Figure:
    df = metrics.sort_values("year")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["year"],
            y=df["altman_z_score"],
            name="Altman Z",
            marker_color="#5E548E",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["year"],
            y=df["pd_estimate"] * 100,
            name="PD(%)",
            mode="lines+markers",
            line={"color": "#EE6352", "width": 3},
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Altman Z vs PD 추정",
        xaxis_title="연도",
        yaxis_title="Altman Z",
        yaxis2=dict(
            title="PD ( % )",
            overlaying="y",
            side="right",
        ),
        template="plotly_white",
    )
    fig.add_hline(y=1.8, line_dash="dot", line_color="#F7A072", annotation_text="Distress 1.8")
    return fig


def _scenario_chart(scenarios: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=scenarios["scenario"],
            y=scenarios["dscr"],
            name="DSCR",
            marker_color="#2A9D8F",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=scenarios["scenario"],
            y=scenarios["pd_estimate"] * 100,
            name="PD(%)",
            mode="lines+markers",
            line={"color": "#E76F51", "width": 3},
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="시나리오별 DSCR & PD",
        xaxis_title="시나리오",
        yaxis_title="DSCR",
        yaxis2=dict(
            title="PD ( % )",
            overlaying="y",
            side="right",
        ),
        template="plotly_white",
    )
    fig.add_hline(y=1.5, line_dash="dot", line_color="#B80C09", annotation_text="NH 기준 1.5x")
    return fig


def _save_figure(fig: go.Figure, path: Path, title: str) -> dict:
    fig.write_image(path, width=900, height=540, scale=2)
    rel_path = Path("figures") / path.name
    return {"title": title, "path": str(rel_path)}
