from pathlib import Path

from changwon_credit.models import load_config


def test_load_config(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(
        """
company:
  name: TestCo
  code: 000000
  industry: Test
data:
  years: 2
  source: TestSource
paths:
  raw_dir: raw
  processed_dir: processed
  sqlite_path: processed/db.sqlite
  report_path: reports/test.md
report:
  analyst: QA
  currency: KRW bn
  bank_view: Test Bank
""",
        encoding="utf-8",
    )

    cfg = load_config(cfg_path)
    assert cfg.company_name == "TestCo"
    assert cfg.company_code == "000000"
    assert cfg.industry == "Test"
    assert cfg.years == 2
    assert cfg.data_source == "TestSource"
    assert cfg.report_path == Path("reports/test.md")
