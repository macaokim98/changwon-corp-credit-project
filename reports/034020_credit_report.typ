#set page(paper: "a4", margin: 1in)
#set text(font: "Noto Sans CJK KR")
#show heading: it => block(spacing: 0.6cm, it)

= 두산에너빌리티 여신 리포트

== 1. 실행 요약
- 두산에너빌리티 posted 16233.1 KRW bn revenue in 2024 with an operating margin of 6.3%.
- EBITDA coverage at 1.8x, ROIC 5.9%, DSCR 0.2x and estimated PD 18.4% ground repayment views.

== 2. 실적 및 현금흐름
#table(columns: (auto, auto, auto, auto, auto, auto), [연도],
  [매출],
  [영업이익],
  [EBITDA],
  [순이익],
  [FCF],
  [2022],
  [15,421.1],
  [1,106.1],
  [3,488.1],
  [-453.2],
  [-715.8],
  [2023],
  [17,589.9],
  [1,467.3],
  [3,014.7],
  [517.5],
  [1,014.4],
  [2024],
  [16,233.1],
  [1,017.6],
  [2,361.8],
  [394.7],
  [-872.2])

== 3. 레버리지·커버리지
#table(columns: (auto, auto, auto, auto, auto, auto, auto, auto), [연도],
  [DSCR],
  [부채/EBITDA],
  [NetDebt/EBITDA],
  [OCF/총부채],
  [FCF/총부채],
  [Altman Z],
  [PD(%)],
  [2022],
  [0.51],
  [3.72],
  [3.32],
  [0.05],
  [-0.06],
  [1.13],
  [18.4%],
  [2023],
  [2.40],
  [4.58],
  [3.71],
  [0.15],
  [0.07],
  [1.23],
  [17.8%],
  [2024],
  [0.18],
  [6.20],
  [4.98],
  [0.02],
  [-0.06],
  [1.11],
  [18.4%])

== 4. 스트레스 시나리오
#table(columns: (auto, auto, auto, auto, auto), [시나리오],
  [매출],
  [EBITDA],
  [DSCR],
  [PD(%)],
  [보수],
  [14,609.8],
  [2,125.6],
  [0.16],
  [19.0%],
  [기준],
  [16,233.1],
  [2,361.8],
  [0.18],
  [18.4%],
  [낙관],
  [17,856.4],
  [2,598.0],
  [0.20],
  [17.9%])

== 5. 여신관점 스토리라인
=== 강점
- Top-line compounded at 2.6% across the review window.
=== 리스크
- Free cash flow margin is negative, implying reliance on external funding.
- Altman Z-score at 1.1 signals heightened default sensitivity.
- DSCR has slipped below 1.2x threshold, pressuring debt service headroom.
- Model-implied PD 18.4% suggests elevated risk tier.

== 6. 제언
- Maintain exposure with covenants on leverage (\<2.0x) and interest coverage (\>2.5x), and tie limits to project milestone cash-in milestones.

== 7. 시각화
#figure(image("figures/01_performance.png", width: 100%), caption: [실적·현금흐름 추세])

#figure(image("figures/02_coverage.png", width: 100%), caption: [DSCR \& Interest Coverage])

#figure(image("figures/03_altman_pd.png", width: 100%), caption: [Altman Z vs PD])

#figure(image("figures/04_scenario.png", width: 100%), caption: [Stress Scenario DSCR/PD])
