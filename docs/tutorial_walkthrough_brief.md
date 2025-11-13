# Changwon Credit 튜토리얼 (요약판)

이 문서는 `docs/tutorial_walkthrough.md`의 세부 가이드를 약 3분의 1 길이로 압축한 버전입니다. 설치, 실행, 산출물 확인, 문제 해결까지 핵심만 빠르게 훑고 싶을 때 참고하세요.

---

## 1. 프로젝트 한눈에 보기

- **목표**: 두산에너빌리티(034020)의 최근 3년 재무 데이터를 FnGuide에서 자동 수집하고, 은행 여신 심사에 필요한 DSCR, PD, LGD, 시나리오 등을 계산해 Markdown·PNG·Typst·Dash 형태로 제공합니다.
- **흐름**: `run_pipeline`으로 원천 데이터 → CSV/Parquet/SQLite 저장 → `compute_credit_metrics`로 지표 산출 → `render_markdown`/`render_typst_report`로 문서화 → `build_charts`로 Plotly 이미지 생성 → `dash_app`으로 대시보드 제공.
- **설정**: `config/config.yaml`에서 회사 코드, 저장 경로, Typst 옵션(`enabled`, `compile_pdf`, `output_dir`, `template`)을 변경할 수 있어 다른 기업이나 템플릿으로 즉시 확장 가능합니다.

---

## 2. 필수 명령 & 실행 순서

```bash
# 1) 의존성 설치 (venv 또는 시스템 Python)
pip install --break-system-packages -e .[dev]

# 2) Typst CLI 설치 & 확인
./docs/run_commands.md 참고 후 typst --version

# 3) 전체 파이프라인 실행 (데이터~Typst)
changwon-credit --config config/config.yaml

# 4) Typst만 다시 컴파일 (문구만 바꿨을 때)
typst compile reports/034020_credit_report.typ reports/034020_credit_report.pdf

# 5) Dash 대시보드 (자동 포트 선택)
python -m changwon_credit.dash_app        # 필요 시 --port 8080 --no-debug 등 추가

# 6) 테스트
pytest
```

실행 후에는 콘솔에 Markdown·Typst·PDF 경로가 차례로 출력됩니다. Dash는 포트가 겹치면 자동으로 다음 포트로 이동하므로, VS Code Dev Container 기준 Ports 패널에서 해당 포트를 포워딩해 브라우저로 열면 됩니다.

---

## 3. 결과물 & 활용법

| 산출물 | 경로 | 용도 |
|--------|------|------|
| Markdown 리포트 | `reports/doosan_credit.md` | “영어 약어 & 활용 맥락” 섹션 포함. 면접/사내 공유용으로 바로 사용 가능. |
| Plotly 이미지 | `reports/figures/*.png` | 실적 추세, 커버리지, Altman Z/PD, 시나리오 그래프. 슬라이드에 바로 삽입. |
| Typst 소스 & PDF | `reports/034020_credit_report.typ/.pdf` | Noto Sans CJK KR 폰트 적용. 템플릿·출력 위치는 YAML에서 제어. |
| SQLite DB | `data_processed/credit.db` | `analytics_credit` 등 테이블을 BI 도구나 SQL로 추가 분석 가능. |
| Dash 대시보드 | `python -m changwon_credit.dash_app` | 카드 형태의 중학생용 약어 설명 + 그래프 4종 + 시나리오 슬라이더. |

팁: 가상환경을 새로 만들었으면 `pip install -e .[dev]`를 그 안에서도 실행해야 `python -m changwon_credit...`이 모듈을 찾습니다.

---

## 4. 문제 해결 & 다음 단계

- **Typst PDF 미생성**: `typst --version`으로 설치 확인. 특수문자 오류는 최신 코드에서 `_escape_text`가 처리하므로 재발하지 않습니다.
- **Dash 접속 불가**: 콘솔에 출력된 실제 포트를 포워딩하거나, `python -m changwon_credit.dash_app --port 8070`처럼 직접 지정하세요.
- **pyenv/venv 문제**: `python3 -m changwon_credit...`처럼 명시적으로 버전을 지정하고, 해당 인터프리터에 의존성을 다시 설치합니다.
- **다른 기업 적용**: `config/config.yaml`의 `company.code`만 바꿔 재실행하면 보고서·대시보드가 모두 새 데이터로 갱신됩니다.
- **다음 단계 아이디어**: Typst 템플릿에 로고·서명란 추가, Dash에 동종업체 비교 탭 도입, CI에서 자동으로 CLI 실행 후 산출물 배포 등을 고려해 보세요.

이 요약판은 장문의 원본 튜토리얼을 빠르게 훑고 싶은 사람을 위한 버전입니다. 더 깊은 설명이나 배경 지식이 필요하면 언제든 `docs/tutorial_walkthrough.md`를 참고하세요. 😊
