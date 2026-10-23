"""
CLI Arayüzü Entegrasyon Testleri (gpower-clone).
CLI Sözleşmesini (CLI Contract) ve tek satır JSON çıktısını test eder.
"""

import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = PROJECT_ROOT / "src" / "cli.py"

def run_cli(args_list):
    cmd = [sys.executable, str(CLI_PATH)] + args_list
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def test_cli_canonical_success():
    """Ödevdeki örnek çağrı başarıyla tek satır JSON dönmelidir."""
    code, stdout, stderr = run_cli([
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", "2",
        "--d", "0.5",
        "--alpha", "0.05",
        "--power", "0.95",
        "--ratio", "1"
    ])
    assert code == 0, f"CLI hata verdi: {stderr}"
    
    # Çıktı tek satır olmalı
    assert "\n" not in stdout
    data = json.loads(stdout)
    assert data["n1"] == 105
    assert data["n2"] == 105
    assert data["n_total"] == 210
    assert data["df"] == 208
    assert abs(data["critical"] - 1.9714) <= 0.0001
    assert abs(data["ncp"] - 3.6228) <= 0.0001
    assert abs(data["actual_power"] - 0.9501) <= 0.0001

def test_cli_post_hoc_success():
    """CLI post-hoc modunda doğru alanları ve değerleri dönmelidir."""
    code, stdout, stderr = run_cli([
        "--test", "t2-indep",
        "--mode", "post-hoc",
        "--tails", "2",
        "--d", "0.5",
        "--alpha", "0.05",
        "--n1", "64",
        "--n2", "64"
    ])
    assert code == 0
    data = json.loads(stdout)
    assert data["df"] == 126
    assert abs(data["actual_power"] - 0.8015) <= 0.0001

def test_cli_invalid_input_returns_error_json_and_nonzero_exit():
    """Geçersiz parametrede JSON error dönmeli ve exit code != 0 olmalıdır."""
    code, stdout, stderr = run_cli([
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", "2",
        "--d", "-0.5",  # Hatalı d
        "--alpha", "0.05",
        "--power", "0.95"
    ])
    assert code != 0
    data = json.loads(stdout)
    assert "error" in data
    assert "Effect size d must be > 0" in data["error"]
