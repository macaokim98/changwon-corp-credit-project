from __future__ import annotations

import argparse
import os
import socket
from pathlib import Path

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, dcc, html

from .glossary import GLOSSARY
from .models import CreditConfig, load_config
from .visuals import _coverage_chart, _performance_chart, _risk_chart, _scenario_chart
from .etl import run_pipeline
from .analytics import compute_credit_metrics, build_scenarios


def create_app(metrics: pd.DataFrame, scenarios: pd.DataFrame, config: CreditConfig) -> Dash:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
    app.layout = dbc.Container(
        [
            html.H2(f"{config.company_name} Interactive Credit Dashboard"),
            html.P(
                "Explore 실적, 커버리지, Altman Z/PD, 스트레스 시나리오를 Plotly 인터랙션으로 확인합니다."
            ),
            html.Hr(),
            html.H4("영어 약어 쉬운 해설"),
            html.P(
                "중학생도 이해할 수 있도록 각 지표가 무엇을 뜻하고 어디에 쓰이는지, 한 줄 설명을 덧붙였습니다."
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                html.H5(item.code, className="card-title"),
                                html.P(item.meaning, className="small mb-1"),
                                html.P(f"실무 활용: {item.usage}", className="small mb-1"),
                                html.P(
                                    f"쉬운 설명: {item.kid_friendly}",
                                    className="text-muted small mb-0",
                                ),
                            ],
                            body=True,
                            className="mb-3 h-100",
                        ),
                        md=4,
                        sm=6,
                        xs=12,
                    )
                    for item in GLOSSARY
                ],
                className="mb-4 g-3",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("시나리오 민감도(±%)"),
                            dcc.Slider(
                                id="scenario-shock",
                                min=5,
                                max=20,
                                step=1,
                                value=10,
                                marks={5: "5%", 10: "10%", 15: "15%", 20: "20%"},
                            ),
                        ],
                        width=4,
                    ),
                ],
                className="my-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="perf-chart"), md=6),
                    dbc.Col(dcc.Graph(id="coverage-chart"), md=6),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="risk-chart"), md=6),
                    dbc.Col(dcc.Graph(id="scenario-chart"), md=6),
                ]
            ),
        ],
        fluid=True,
    )

    @app.callback(
        Output("perf-chart", "figure"),
        Output("coverage-chart", "figure"),
        Output("risk-chart", "figure"),
        Output("scenario-chart", "figure"),
        Input("scenario-shock", "value"),
    )
    def update_figures(shock_percent: int):
        shock = shock_percent / 100
        perf_fig = _performance_chart(metrics, config)
        coverage_fig = _coverage_chart(metrics)
        risk_fig = _risk_chart(metrics)
        new_scenarios = build_scenarios(metrics, shock=shock)
        scenario_fig = _scenario_chart(new_scenarios)
        return perf_fig, coverage_fig, risk_fig, scenario_fig

    return app


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the interactive Dash dashboard.")
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Listening host (default: 0.0.0.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8050")),
        help="Preferred port (default: 8050).",
    )
    parser.add_argument(
        "--max-port",
        type=int,
        default=int(os.environ.get("PORT_MAX", "8100")),
        help="If the preferred port is busy, keep trying sequential ports up to this value.",
    )
    parser.add_argument(
        "--no-debug",
        action="store_true",
        help="Disable Dash debug mode (default: debug on).",
    )
    return parser.parse_args()


def _pick_available_port(host: str, start_port: int, max_port: int) -> int:
    port = start_port
    while port <= max_port:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                port += 1
                continue
        return port
    raise RuntimeError(f"No available port between {start_port} and {max_port}")


def main() -> None:
    args = _parse_args()
    config_path = Path("config/config.yaml")
    cfg = load_config(config_path)
    merged = run_pipeline(cfg)
    metrics = compute_credit_metrics(merged)
    scenarios = build_scenarios(metrics)
    app = create_app(metrics, scenarios, cfg)
    host = args.host
    requested_port = args.port
    max_port = max(requested_port, args.max_port)
    debug_mode = not args.no_debug
    chosen_port = _pick_available_port(host, requested_port, max_port)

    if chosen_port != requested_port:
        print(f"Port {requested_port} busy, switched to {chosen_port}")

    print(f"Dash dashboard listening on http://{host}:{chosen_port} (debug={debug_mode})")
    app.run(debug=debug_mode, host=host, port=chosen_port, use_reloader=False)


if __name__ == "__main__":
    main()
