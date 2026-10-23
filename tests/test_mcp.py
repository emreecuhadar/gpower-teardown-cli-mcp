"""
MCP Sunucusu Entegrasyon Testleri.
Kural: CLI ile MCP'nin aynı girdide aynı çıktıyı verdiğini doğrular.
"""

import sys
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_PATH = PROJECT_ROOT / "src" / "cli.py"

from src.mcp_server import handle_tool_call

def run_cli_json(args_list):
    cmd = [sys.executable, str(CLI_PATH)] + args_list
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, f"CLI hatası: {proc.stderr}"
    return json.loads(proc.stdout.strip())

def test_mcp_and_cli_identical_output_a_priori():
    """A-priori modunda CLI ile MCP aynı çıktıyı vermelidir."""
    # 1. Test durumu: Canonical
    cli_out = run_cli_json([
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", "2",
        "--d", "0.5",
        "--alpha", "0.05",
        "--power", "0.95",
        "--ratio", "1"
    ])

    mcp_out = handle_tool_call("calculate_sample_size_t2_indep", {
        "tails": 2,
        "d": 0.5,
        "alpha": 0.05,
        "power": 0.95,
        "ratio": 1.0
    })

    assert cli_out == mcp_out, f"Fark bulundu!\nCLI: {cli_out}\nMCP: {mcp_out}"

    # 2. Test durumu: Eşit olmayan grup (ratio=1.5, d=0.8, power=0.80)
    cli_out2 = run_cli_json([
        "--test", "t2-indep",
        "--mode", "a-priori",
        "--tails", "2",
        "--d", "0.8",
        "--alpha", "0.05",
        "--power", "0.80",
        "--ratio", "1.5"
    ])

    mcp_out2 = handle_tool_call("calculate_sample_size_t2_indep", {
        "tails": 2,
        "d": 0.8,
        "alpha": 0.05,
        "power": 0.80,
        "ratio": 1.5
    })

    assert cli_out2 == mcp_out2

def test_mcp_and_cli_identical_output_post_hoc():
    """Post-hoc modunda CLI ile MCP aynı çıktıyı vermelidir."""
    cli_out = run_cli_json([
        "--test", "t2-indep",
        "--mode", "post-hoc",
        "--tails", "2",
        "--d", "0.5",
        "--alpha", "0.05",
        "--n1", "64",
        "--n2", "64"
    ])

    mcp_out = handle_tool_call("calculate_power_t2_indep", {
        "tails": 2,
        "d": 0.5,
        "alpha": 0.05,
        "n1": 64,
        "n2": 64
    })

    assert cli_out == mcp_out, f"Fark bulundu!\nCLI: {cli_out}\nMCP: {mcp_out}"
