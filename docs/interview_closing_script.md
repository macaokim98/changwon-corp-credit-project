# 면접 마무리 스크립트 & 여신 분석 용어 정리 (완전 초보자용)

이 문서는 “면접관이 마지막으로 하고 싶은 말이 있냐”고 물어볼 때,
기업여신 분석 자동화 프로젝트를 강조하며 진정성을 보여줄 수 있도록 만든 특별 스크립트입니다.
또한, 면접 중 자주 등장하는 영어 약어(DSCR, PD, LGD 등)와 명령어에 주석을 달아,
이 문서 하나만으로 전체 흐름을 이해할 수 있게 구성했습니다.

---

## 1. 필수 용어 & 약어 (정말 쉬운 버전)

| 약어                                | 풀어쓰기                                                    | 쉬운 설명                                                        |
| ----------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------- |
| **OCF**                       | Operating Cash Flow                                         | 회사가 본업으로 벌어들인 현금. 여신 상환의 1차 원천.             |
| **FCF**                       | Free Cash Flow = OCF – CAPEX                               | 설비투자까지 하고 남는 자유 현금. 채무상환에 직접 사용 가능.     |
| **DSCR**                      | Debt Service Coverage Ratio = OCF / (이자 + 원금 상환)      | 1.5 이상이면 안전. 1.0 이하면 위험.                              |
| **EBITDA**                    | Earnings Before Interest, Taxes, Depreciation, Amortization | 현금에 가까운 이익. 이자 상환 여력 파악에 쓰임.                  |
| **ROIC**                      | Return on Invested Capital = 영업이익 / (투자 자본)         | 투자 대비 얼마를 벌었는지. 높을수록 효율적.                      |
| **Net Debt/EBITDA**           | (부채 – 현금) / EBITDA                                     | 빚을 몇 년 만에 갚을 수 있나 보는 지표. 4배 이상이면 경고.       |
| **Altman Z**                  | 재무건전성 점수(1.8 미만은 위험)                            | 여러 비율을 섞어 파산 위험을 추정.                               |
| **PD**                        | Probability of Default (부도확률)                           | 파산할 확률. %로 표시.                                           |
| **LGD**                       | Loss Given Default                                          | 부도 시 얼마나 손실 날지. 0~100%.                                |
| **Scenario (보수/기준/낙관)** | Stress Test                                                 | 경제가 나쁠 때, 보통일 때, 좋을 때를 가정해 DSCR/PD 변화를 본다. |

> **Tip**: 면접 중 약어가 나오면 풀어 말한 뒤, “이 프로젝트에서는 자동 계산되도록 했다”고 연결하세요.

---

## 2. 명령어 & 주석 (Command Cheatsheet)

```bash
# 1) 의존성 설치 (Python 패키지 + 개발용 툴)
pip install --break-system-packages -e .[dev]

# 2) Typst CLI (PDF 생성기) 확인
typst --version       # 출력되면 설치 완료, 예: typst 0.11.1

# 3) 전체 파이프라인 실행
changwon-credit --config config/config.yaml
# 순서: 웹에서 데이터 받기 -> 가공 -> 분석 -> Markdown/PNG/Typst 보고서

# 4) 인터랙티브 대시보드 실행
python3 -m changwon_credit.dash_app
# 브라우저에서 http://127.0.0.1:8050 열기

# 5) Typst PDF 수동 컴파일 (옵션)
typst compile reports/034020_credit_report.typ reports/034020_credit_report.pdf

# 6) 주요 산출물 경로
ls reports/                 # Markdown, Typst, figures
ls data_processed/          # Parquet + SQLite (credit.db)
```

---

## 3. 프로젝트 기능 요약 (초보자 관점)

1. **데이터 자동 수집**: FnGuide에서 HTML 표를 읽어 파이썬으로 변환.
2. **ETL 저장**: 원본 CSV, 정제 Parquet, 분석용 SQLite까지 한 번에.
3. **여신 지표 계산**: ROIC, DSCR, Net Debt/EBITDA, Altman Z, PD, LGD, 시나리오 등.
4. **리포트**: Markdown 문서 + Plotly 차트 + Typst PDF.
5. **대시보드**: Dash로 만든 인터랙티브 화면 (슬라이더로 시나리오 조정).
6. **커맨드라인 자동화**: `changwon-credit --config ...` 한 번이면 전부 실행.

---

## 4. 면접 마무리 스크립트 (자신감 + 절실함 표현)

> “마지막으로 말씀드리자면, 저는 창원 본사의 두산에너빌리티를 대상으로
> OCF, DSCR, PD 같은 핵심 여신 지표를 자동으로 계산하는 파이썬 파이프라인을 만들었습니다.
> `changwon-credit --config config/config.yaml` 명령 한 번이면 데이터를 수집하고,
> Markdown/Typst 보고서와 Plotly 차트, 대시보드까지 모두 업데이트됩니다.
> 은행 실무에서 가장 중요한 건 **정확한 현금흐름 기반 판단**이라고 생각합니다.
> 이 자동화 툴로, 저는 면접 이후에도 바로 실무에 기여할 준비가 되어 있음을 꼭 보여드리고 싶습니다.”

### 추가 한마디 (선택)

- “PD(부도확률)나 LGD(부도 시 손실률) 같은 수치를 플러그인으로 쉽게 바꿀 수 있어서,다른 기업이나 다른 산업에도 바로 확장할 수 있습니다.”
- “Typst 템플릿과 대시보드는 고객사나 상사에게 바로 전달할 수 있는 형태로 준비되어 있습니다.”

---

## 5. 예시 Q&A 대비

1. **Q: DSCR이 0.9면 어떻게 해석하나요?**A: “본업 현금으로 이자·원금을 다 갚지 못하니 위험 신호입니다. 그래프와 Typst 보고서에 경고를 넣었습니다.”
2. **Q: 다른 기업으로 전환하려면?**A: “`config.yaml`에서 `company.code`를 바꾸고 다시 실행하면 같은 템플릿으로 자동 분석됩니다.”
3. **Q: PD를 어떻게 계산했나요?**
   A: “Altman Z 점수 구간에 따라 단계별 부도확률을 매핑했습니다. 모형이 IRB와 유사하게 행동하도록 설계했습니다.”

---

## 6. 마지막 체크리스트

- [ ] `typst --version` OK
- [ ] `changwon-credit --config config/config.yaml` 실행 후 `reports/`에 새 리포트 생성 확인
- [ ] Dash 대시보드 실행 테스트 (`python -m changwon_credit.dash_app`)
- [ ] 면접 스크립트 크게 소리 내어 연습 (약어 풀어서 설명하기!)

이 문서를 한 번 읽고, 명령어를 직접 쳐보고, 스크립트를 연습하면
면접 마무리 질문에도 자신 있게 답하고, 자동화 역량을 강조할 수 있습니다. 화이팅! 💪
