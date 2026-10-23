#!/usr/bin/env python3
"""
10 Soruluk Klinik Değerlendirme Seti Çalıştırıcısı ve Raporlayıcısı.
Ajanın doğru seçim oranını ve araç çağrı kayıtlarını (log) üretir.
"""

import sys
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import ClinicalPowerAgent

def run_evaluation():
    eval_file = CURRENT_DIR / "clinic_10_eval.json"
    with open(eval_file, "r", encoding="utf-8") as f:
        cases = json.load(f)

    agent = ClinicalPowerAgent()
    correct_family_count = 0
    correct_n_count = 0
    total_cases = len(cases)

    print("=" * 80)
    print("KLİNİK AI AJANI 10 SORULUK DOĞRULAMA VE DEĞERLENDİRME KOŞUSU")
    print("=" * 80)

    for case in cases:
        cid = case["id"]
        question = case["question"]
        expected_fam = case["expected_family"]
        expected_n = case["expected_n_total"]

        print(f"\n[Soru #{cid}] ({case['clinical_domain']})")
        print(f"Hekim Sorusu: \"{question}\"")

        res = agent.process_query(question)
        detected_fam = res["label"]

        # Aile doğruluğu kontrolü
        fam_matched = (detected_fam == expected_fam)
        if fam_matched:
            correct_family_count += 1
            fam_status = "✓ DOĞRU"
        else:
            fam_status = f"✗ YANLIŞ (Beklenen: {expected_fam}, Tespit: {detected_fam})"

        print(f"Test Ailesi Seçimi: {detected_fam} (Güven: {res['confidence']:.2f}) -> {fam_status}")

        # Eğer t2-indep ise N doğruluğu kontrolü
        if expected_fam == "t2-indep":
            actual_n = res.get("result", {}).get("n_total")
            n_matched = (actual_n == expected_n)
            if n_matched:
                correct_n_count += 1
                n_status = f"✓ TAM EŞLEŞTİ (N={actual_n})"
            else:
                n_status = f"✗ SAPMA (Beklenen N={expected_n}, Motor N={actual_n})"
            print(f"Örneklem Boyutu Hesabı: {n_status}")
            print(f"Yürütme Süresi: {res.get('execution_time_ms', 0)} ms")
        else:
            print(f"Ajan Eylemi: {res.get('message', res.get('clinical_response', ''))}")

    print("\n" + "=" * 80)
    print("DEĞERLENDİRME SONUÇ RAPORU")
    print("=" * 80)
    print(f"Toplam Senaryo: {total_cases}")
    print(f"Doğru Test Ailesi Seçim Oranı: {correct_family_count}/{total_cases} (%{correct_family_count / total_cases * 100:.1f})")
    print(f"Doğru Örneklem Boyutu (N) Tam Eşleşme Oranı: {correct_n_count}/5 (%{correct_n_count / 5 * 100:.1f})")
    
    # Araç çağrı kayıtlarını kaydet
    log_file = CURRENT_DIR / "agent_call_logs.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(agent.call_logs, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Araç çağrı kayıtları (log) kaydedildi: {log_file}")

if __name__ == "__main__":
    run_evaluation()
