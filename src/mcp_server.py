#!/usr/bin/env python3
"""
G*Power MCP Sunucusu (Model Context Protocol Server).
Model Context Protocol standardı üzerinden G*Power hesaplama motorunu LLM'lere ve Ajanlara sunar.

Önemli Kural: Hesap mantığı MCP katmanına kopyalanmaz; motorun (src.engine.solver) ince bir adaptörüdür.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.solver import run_calculation

logging.basicConfig(level=logging.ERROR, stream=sys.stderr)
logger = logging.getLogger("gpower-mcp-server")

TOOLS = [
    {
        "name": "calculate_sample_size_t2_indep",
        "description": "İki bağımsız grup t-testi (t2-indep / ilaç vs plasebo) için a-priori gereken örneklem boyutunu (n1, n2, n_total) hesaplar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "d": {
                    "type": "number",
                    "description": "Cohen's d etki büyüklüğü (örn: 0.5 orta etki, 0.2 küçük etki, 0.8 büyük etki)"
                },
                "alpha": {
                    "type": "number",
                    "description": "Tip I hata / Anlamlılık düzeyi (varsayılan genelde 0.05)"
                },
                "power": {
                    "type": "number",
                    "description": "Hedeflenen istatistiksel güç 1-beta (örn: 0.80 veya 0.95)"
                },
                "tails": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "Hipotez yönü: 1 (tek yönlü) veya 2 (çift yönlü)"
                },
                "ratio": {
                    "type": "number",
                    "description": "Grup 2 / Grup 1 örneklem büyüklüğü oranı (n2/n1, varsayılan: 1.0 eşit gruplar)"
                }
            },
            "required": ["d", "alpha", "power", "tails"]
        }
    },
    {
        "name": "calculate_power_t2_indep",
        "description": "İki bağımsız grup t-testi (t2-indep) için mevcut n1 ve n2 örneklemleriyle elde edilen post-hoc istatistiksel gücü hesaplar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "d": {
                    "type": "number",
                    "description": "Cohen's d etki büyüklüğü"
                },
                "alpha": {
                    "type": "number",
                    "description": "Anlamlılık düzeyi (alfa)"
                },
                "n1": {
                    "type": "integer",
                    "description": "Grup 1 hasta/denek sayısı"
                },
                "n2": {
                    "type": "integer",
                    "description": "Grup 2 hasta/denek sayısı"
                },
                "tails": {
                    "type": "integer",
                    "enum": [1, 2],
                    "description": "Kuyruk sayısı: 1 veya 2"
                }
            },
            "required": ["d", "alpha", "n1", "n2", "tails"]
        }
    }
]

def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """İnce adaptör çağrısı: Hesaplamayı doğrudan çekirdek motora delege eder."""
    if tool_name == "calculate_sample_size_t2_indep":
        return run_calculation(
            test="t2-indep",
            mode="a-priori",
            tails=arguments.get("tails", 2),
            d=float(arguments["d"]),
            alpha=float(arguments["alpha"]),
            power=float(arguments["power"]),
            ratio=float(arguments.get("ratio", 1.0))
        )
    elif tool_name == "calculate_power_t2_indep":
        return run_calculation(
            test="t2-indep",
            mode="post-hoc",
            tails=arguments.get("tails", 2),
            d=float(arguments["d"]),
            alpha=float(arguments["alpha"]),
            n1=int(arguments["n1"]),
            n2=int(arguments["n2"])
        )
    else:
        raise ValueError(f"Bilinmeyen MCP aracı: '{tool_name}'")

def run_stdio_server():
    """Standart I/O üzerinden JSON-RPC 2.0 MCP sunucusu."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            req = json.loads(line)
            req_id = req.get("id")
            method = req.get("method")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "gpower-cleanroom-mcp",
                            "version": "1.0.0"
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                # Bildirim, yanıt gerekmez
                pass

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                try:
                    result = handle_tool_call(tool_name, args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result, separators=(',', ':'))
                                }
                            ]
                        }
                    }
                except Exception as ex:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "isError": True,
                        "error": {
                            "code": -32603,
                            "message": str(ex)
                        }
                    }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

        except Exception as e:
            logger.error(f"MCP sunucu döngü hatası: {e}")

if __name__ == "__main__":
    run_stdio_server()
