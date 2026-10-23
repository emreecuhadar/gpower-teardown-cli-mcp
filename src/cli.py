#!/usr/bin/env python3
"""
G*Power-Clone CLI Arayüzü.
Ödev sözleşmesine (CLI Contract) %100 uyumlu komut satırı aracı.

Örnek çağrı:
gpower-clone --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
"""

import sys
import json
import argparse
from pathlib import Path

# src dizinini import yoluna ekle
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.solver import run_calculation

def main():
    parser = argparse.ArgumentParser(
        description="G*Power Clean-Room CLI (gpower-clone)",
        add_help=True
    )
    parser.add_argument("--test", type=str, required=True, help="Test ailesi (örn: t2-indep)")
    parser.add_argument("--mode", type=str, required=True, choices=["a-priori", "post-hoc"], help="Hesaplama modu")
    parser.add_argument("--tails", type=int, required=True, choices=[1, 2], help="Kuyruk sayısı (1 veya 2)")
    parser.add_argument("--d", type=float, required=True, help="Cohen's d etki büyüklüğü")
    parser.add_argument("--alpha", type=float, required=True, help="Anlamlılık düzeyi (alfa)")
    parser.add_argument("--power", type=float, default=None, help="Hedef güç (a-priori için zorunlu)")
    parser.add_argument("--ratio", type=float, default=1.0, help="Grup 2 / Grup 1 örneklem oranı (N2/N1, varsayılan: 1.0)")
    parser.add_argument("--n1", type=int, default=None, help="Grup 1 örneklem boyutu (post-hoc için zorunlu)")
    parser.add_argument("--n2", type=int, default=None, help="Grup 2 örneklem boyutu (post-hoc için zorunlu)")

    try:
        # Argümanları ayrıştır
        args = parser.parse_args()

        # Tek motor üzerinden hesabı çalıştır
        result = run_calculation(
            test=args.test,
            mode=args.mode,
            tails=args.tails,
            d=args.d,
            alpha=args.alpha,
            power=args.power,
            ratio=args.ratio,
            n1=args.n1,
            n2=args.n2
        )

        # Sözleşmeye uygun tek satır JSON çıktısı üret
        output_json = json.dumps(result, separators=(',', ':'))
        print(output_json)
        sys.exit(0)

    except SystemExit as se:
        # Argparse yardım veya eksik parametre hatası durumunda
        if se.code != 0:
            error_payload = {"error": "Invalid or missing arguments"}
            print(json.dumps(error_payload, separators=(',', ':')))
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        # Matematiksel veya iş kuralı hatası
        error_payload = {"error": str(e)}
        print(json.dumps(error_payload, separators=(',', ':')))
        sys.exit(1)

if __name__ == "__main__":
    main()
