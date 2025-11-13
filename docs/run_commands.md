# 실행 명령 모음

Changwon corporate credit 프로젝트에서 자주 쓰는 명령들을 한곳에 모았습니다. 새 환경을 구성하거나 리포트를 다시 만들 때 순서대로 실행하면 됩니다.

## 1. 파이썬 의존성 설치

```bash
pip install --break-system-packages -e .[dev]
```

## 2. Typst CLI 설치 (Linux x86_64 예시)

```bash
TMP_DIR=$(mktemp -d)
curl -L -o "$TMP_DIR/typst.tar.xz" https://github.com/typst/typst/releases/download/v0.14.0/typst-x86_64-unknown-linux-musl.tar.xz
tar -xf "$TMP_DIR/typst.tar.xz" -C "$TMP_DIR"
install -m 755 "$(find "$TMP_DIR" -name typst -type f -perm -111 | head -n 1)" ~/.local/bin/typst
rm -rf "$TMP_DIR"
typst --version
```

## 3. 전체 파이프라인 실행 (Markdown + Typst PDF)

```bash
changwon-credit --config config/config.yaml
```

## 4. Typst만 수동 재컴파일

```bash
typst compile reports/034020_credit_report.typ reports/034020_credit_report.pdf
```

## 5. Dash 대시보드

```bash
# 기본: 비어 있는 포트를 자동으로 찾아 실행
python -m changwon_credit.dash_app

# 특정 포트를 강제로 지정하고 싶다면
python -m changwon_credit.dash_app --port 8060

# 디버그 끄기 또는 호스트 지정
python -m changwon_credit.dash_app --no-debug --host 127.0.0.1
```

## 6. Streamlit 모바일 앱

```bash
streamlit run src/changwon_credit/streamlit_mobile_app.py --server.address 0.0.0.0 --server.port 8050
```

- 보라색 그라데이션 다크 테마를 적용한 모바일 친화 UI입니다.
- 사이드바에서 메뉴와 시나리오 슬라이더를 조정할 수 있습니다.

## 7. Streamlit 테스트 페이지

```bash
streamlit run src/changwon_credit/streamlit_test.py
```

- 샘플 데이터만 사용하므로 FnGuide 호출이나 ETL을 돌리지 않아도 됩니다.
- Streamlit 위젯/그래프가 정상 작동하는지 빠르게 확인할 때 활용하세요.

## 8. 테스트

```bash
pytest
```
