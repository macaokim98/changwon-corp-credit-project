from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, slots=True)
class Acronym:
    code: str
    meaning: str
    usage: str
    kid_friendly: str


GLOSSARY: List[Acronym] = [
    Acronym(
        "DSCR",
        "Debt Service Coverage Ratio = OCF / (이자+원금)",
        "은행이 현금흐름으로 빚을 갚을 수 있는지 판단할 때",
        "본업에서 돈을 얼마나 벌어 빚 갚기에 쓰는지 보여주는 비율",
    ),
    Acronym(
        "PD",
        "Probability of Default (부도확률)",
        "여신등급, 한도, 가격결정 등 리스크 판단",
        "회사가 빚을 못 갚을 확률. 숫자가 낮을수록 안전",
    ),
    Acronym(
        "LGD",
        "Loss Given Default",
        "기대손실(ECL)과 충당금 계산",
        "회사가 망했을 때 은행이 잃을 비율",
    ),
    Acronym(
        "EBITDA",
        "Earnings Before Interest, Taxes, Depreciation, Amortization",
        "레버리지 비교, 기업가치 평가",
        "감가상각 같은 비현금 비용을 뺀, 현금에 가까운 이익",
    ),
    Acronym(
        "ROIC",
        "Return on Invested Capital",
        "투자 효율, EVA 분석",
        "투자한 돈 대비 얼마나 벌었는지 보는 비율",
    ),
    Acronym(
        "FCF",
        "Free Cash Flow = OCF – CAPEX",
        "배당·부채상환 여력 검토",
        "설비투자까지 끝낸 뒤 진짜로 남는 현금",
    ),
    Acronym(
        "OCF",
        "Operating Cash Flow",
        "상환 재원 검증",
        "회사가 본업으로 벌어 들인 현금",
    ),
]
