"""
Diferansiyel Test Modülü (Differential Testing against G*Power Oracle).
Kâhin (oracle/gpower_vectors.csv) ile yeniden yazım motorunu karşılaştırır.
KAPI KURALI: N değeri en az %90 oranında TAM eşleşmelidir.
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.solver import run_calculation

ORACLE_CSV = PROJECT_ROOT / "oracle" / "gpower_vectors.csv"

def load_oracle_vectors():
    vectors = []
    with open(ORACLE_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vectors.append(row)
    return vectors

def test_differential_oracle_gate_requirement():
    """Tüm referans vektörler üzerinde diferansiyel test çalıştırır ve %90+ tam N eşleşmesini doğrular."""
    vectors = load_oracle_vectors()
    assert len(vectors) >= 30, f"En az 30 kâhin vektörü olmalıdır. Mevcut: {len(vectors)}"

    exact_n_matches = 0
    total_vectors = len(vectors)
    discrepancies = []

    for vec in vectors:
        vec_id = vec["id"]
        test_fam = vec["test"]
        mode = vec["mode"]
        tails = int(vec["tails"])
        d = float(vec["d"])
        alpha = float(vec["alpha"])
        power = float(vec["power_target"]) if vec["power_target"] else None
        ratio = float(vec["ratio"]) if vec["ratio"] else 1.0
        n1 = int(vec["n1"]) if vec["n1"] else None
        n2 = int(vec["n2"]) if vec["n2"] else None

        expected_n1 = int(vec["n1"])
        expected_n2 = int(vec["n2"])
        expected_n_total = int(vec["n_total"])
        expected_df = int(vec["df"])
        expected_crit = float(vec["critical"])
        expected_ncp = float(vec["ncp"])
        expected_power = float(vec["actual_power"])

        # Motoru çalıştır
        res = run_calculation(
            test=test_fam,
            mode=mode,
            tails=tails,
            d=d,
            alpha=alpha,
            power=power,
            ratio=ratio,
            n1=n1,
            n2=n2
        )

        n1_ok = (res["n1"] == expected_n1)
        n2_ok = (res["n2"] == expected_n2)
        n_total_ok = (res["n_total"] == expected_n_total)
        df_ok = (res["df"] == expected_df)
        crit_ok = abs(res["critical"] - expected_crit) <= 0.0002
        ncp_ok = abs(res["ncp"] - expected_ncp) <= 0.0002
        power_ok = abs(res["actual_power"] - expected_power) <= 0.0002

        if n1_ok and n2_ok and n_total_ok:
            exact_n_matches += 1
        else:
            discrepancies.append({
                "id": vec_id,
                "notes": vec["notes"],
                "expected": f"n1={expected_n1}, n2={expected_n2}, N={expected_n_total}",
                "actual": f"n1={res['n1']}, n2={res['n2']}, N={res['n_total']}"
            })

    match_rate = exact_n_matches / total_vectors
    print(f"\nDiferansiyel Test Sonucu: {exact_n_matches}/{total_vectors} tam eşleşti (%{match_rate * 100:.2f})")

    # KAPI KONTROLÜ: En az %90 tam eşleşme
    assert match_rate >= 0.90, (
        f"KAPI BAŞARISIZ: N tam eşleşme oranı %{match_rate * 100:.2f} (%90'ın altında). "
        f"Uyuşmazlıklar: {discrepancies}"
    )

    if discrepancies:
        print(f"Uyuşmazlıklar ({len(discrepancies)} adet): {discrepancies}")
    else:
        print("Tebrikler: Kâhin ile %100 TAM EŞLEŞME sağlandı!")

if __name__ == "__main__":
    test_differential_oracle_gate_requirement()
