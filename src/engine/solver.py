"""
G*Power t2-indep Hesaplama Motoru (Unified Engine Core).
Hem a-priori (N arama) hem post-hoc (güç hesaplama) modlarını çalıştırır.
"""

import math
from typing import Dict, Any, Optional
from .distributions import student_t_ppf, nct_cdf, normal_ppf

def compute_t2_indep_power(tails: int, d: float, alpha: float, n1: int, n2: int) -> Dict[str, Any]:
    """
    Verilen n1 ve n2 için t2-indep post-hoc güç ve istatistik parametrelerini hesaplar.
    """
    if n1 < 2 or n2 < 2:
        raise ValueError(f"Örneklem büyüklüğü n1 ve n2 en az 2 olmalıdır (df >= 2). n1={n1}, n2={n2}")
    if d <= 0.0:
        raise ValueError(f"Effect size d must be > 0. Girilen: {d}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Alpha must be between 0 and 1. Girilen: {alpha}")
    if tails not in (1, 2):
        raise ValueError(f"Tails must be 1 or 2. Girilen: {tails}")

    df = n1 + n2 - 2
    n_total = n1 + n2

    # Noncentrality parameter δ (ncp)
    # δ = d * sqrt( (n1 * n2) / (n1 + n2) )
    ncp = d * math.sqrt((n1 * n2) / (n1 + n2))

    # Kritik t değeri
    if tails == 1:
        critical = student_t_ppf(1.0 - alpha, df)
        # Tek yönlü testte güç: P(T > critical | H1)
        actual_power = 1.0 - nct_cdf(critical, df, ncp)
    else:
        critical = student_t_ppf(1.0 - alpha / 2.0, df)
        # [REA]: Çift yönlü testte her iki kuyruğun toplamı
        # Power = P(T > critical | H1) + P(T < -critical | H1)
        actual_power = (1.0 - nct_cdf(critical, df, ncp)) + nct_cdf(-critical, df, ncp)

    actual_power = min(1.0, max(0.0, actual_power))

    return {
        "n1": n1,
        "n2": n2,
        "n_total": n_total,
        "actual_power": round(actual_power, 4),
        "critical": round(critical, 4),
        "df": df,
        "ncp": round(ncp, 4),
        "_raw_power": actual_power
    }

def solve_a_priori_t2_indep(
    tails: int,
    d: float,
    alpha: float,
    power: float,
    ratio: float = 1.0
) -> Dict[str, Any]:
    """
    A-priori modu: İstenen hedef gücü (power) sağlayan minimum tamsayı n1 ve n2'yi bulur.
    [REA]: n2 = ceil(n1 * ratio) tavan kuralı uygulanır.
    """
    if d <= 0.0:
        raise ValueError(f"Effect size d must be > 0. Girilen: {d}")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Alpha must be between 0 and 1. Girilen: {alpha}")
    if not (0.0 < power < 1.0):
        raise ValueError(f"Power must be between 0 and 1. Girilen: {power}")
    if ratio <= 0.0:
        raise ValueError(f"Allocation ratio must be positive. Girilen: {ratio}")
    if tails not in (1, 2):
        raise ValueError(f"Tails must be 1 or 2. Girilen: {tails}")

    # Başlangıç tahmini (Normal Yaklaşım alt sınırı)
    z_alpha = normal_ppf(1.0 - alpha / tails)
    z_beta = normal_ppf(power)
    # N* = (z_alpha + z_beta)^2 / d^2
    n_star = ((z_alpha + z_beta) / d) ** 2
    # N* = n1 * ratio / (1 + ratio) => n1 = n_star * (1 + ratio) / ratio
    approx_n1 = n_star * (1.0 + ratio) / ratio
    
    # Güvenli bir alt sınır belirle
    low_n1 = max(2, int(approx_n1 * 0.65))

    # Üst sınır arama (exponential search)
    high_n1 = max(low_n1 + 5, int(approx_n1 * 1.5) + 10)
    
    while True:
        candidate_n2 = math.ceil(high_n1 * ratio)
        res = compute_t2_indep_power(tails, d, alpha, high_n1, candidate_n2)
        if res["_raw_power"] >= power:
            break
        high_n1 *= 2

    # İkili arama (Binary Search) ile hedef gücü sağlayan EN KÜÇÜK n1'i bul
    left = low_n1
    right = high_n1
    best_n1 = high_n1

    while left <= right:
        mid = (left + right) // 2
        candidate_n2 = math.ceil(mid * ratio)
        res = compute_t2_indep_power(tails, d, alpha, mid, candidate_n2)
        
        if res["_raw_power"] >= power:
            best_n1 = mid
            right = mid - 1  # Daha küçük bir n1 ile sağlanabiliyor mu?
        else:
            left = mid + 1

    final_n2 = math.ceil(best_n1 * ratio)
    final_res = compute_t2_indep_power(tails, d, alpha, best_n1, final_n2)
    
    # Dahili ham gücü kaldırıp sözleşmeye uygun temiz dict döndür
    final_res.pop("_raw_power", None)
    return final_res

def run_calculation(
    test: str,
    mode: str,
    tails: int,
    d: float,
    alpha: float,
    power: Optional[float] = None,
    ratio: float = 1.0,
    n1: Optional[int] = None,
    n2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Tüm CLI, MCP ve Ajan çağrıları için tek hesaplama giriş noktası.
    """
    if test != "t2-indep":
        raise ValueError(f"Unsupported test family: '{test}'. Sadece 't2-indep' desteklenmektedir.")

    if mode == "a-priori":
        if power is None:
            raise ValueError("A-priori modu için 'power' parametresi zorunludur.")
        return solve_a_priori_t2_indep(tails=tails, d=d, alpha=alpha, power=power, ratio=ratio)
    elif mode == "post-hoc":
        if n1 is None or n2 is None:
            raise ValueError("Post-hoc modu için 'n1' ve 'n2' parametreleri zorunludur.")
        res = compute_t2_indep_power(tails=tails, d=d, alpha=alpha, n1=n1, n2=n2)
        res.pop("_raw_power", None)
        return res
    else:
        raise ValueError(f"Geçersiz mod: '{mode}'. Yalnızca 'a-priori' veya 'post-hoc' kullanılabilir.")
