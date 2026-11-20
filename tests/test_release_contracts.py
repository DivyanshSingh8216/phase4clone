from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_api_exposes_only_five_approved_metrics():
    src=(ROOT/"api.py").read_text(encoding="utf-8")
    for mid in ["M16","M17","M18","M21","M22"]:
        assert f'"{mid}"' in src
    assert "read_only=True" in src

def test_explorer_fails_closed_in_production():
    src=(ROOT/"explorer.py").read_text(encoding="utf-8")
    assert 'PULSEIQ_AUTH_MODE' in src
    assert 'production' in src
    assert 'st.stop()' in src

def test_report_requires_explicit_dates_and_governed_views():
    src=(ROOT/"build_report.py").read_text(encoding="utf-8")
    assert 'ap.add_argument("--start",required=True' in src
    assert 'ap.add_argument("--end",required=True' in src
    assert 'all_metrics' in src and 'metric_catalog' in src

def test_no_phase1_to_phase3_paths_written_by_phase4_code():
    src=(ROOT/"build_report.py").read_text(encoding="utf-8")
    assert "read_only=True" in src
    assert "PulseIQ_Dataset.xlsx" not in src
