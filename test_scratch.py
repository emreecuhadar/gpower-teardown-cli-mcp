import csv
from src.engine.solver import compute_t2_indep_power, solve_a_priori_t2_indep

with open("oracle/gpower_vectors.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

for r in rows:
    tails = int(r["tails"])
    d = float(r["d"])
    alpha = float(r["alpha"])
    mode = r["mode"]
    
    if mode == "a-priori":
        p_target = float(r["power_target"])
        ratio = float(r["ratio"]) if r["ratio"] else 1.0
        exp_n1 = int(r["n1"])
        exp_n2 = int(r["n2"])
        
        # solve
        res = solve_a_priori_t2_indep(tails, d, alpha, p_target, ratio)
        if res["n1"] != exp_n1 or res["n2"] != exp_n2:
            # Check what power exp_n1 actually has:
            check = compute_t2_indep_power(tails, d, alpha, exp_n1, exp_n2)
            print(f"Row {r['id']} ({r['notes']}): CSV has n1={exp_n1},n2={exp_n2} (power={check['actual_power']}), but target={p_target}. Engine found n1={res['n1']},n2={res['n2']} (power={res['actual_power']})")
