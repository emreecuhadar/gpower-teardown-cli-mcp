"""
Birim Testleri: İstatistik Dağılım Fonksiyonları ve Hesaplama Motoru
"""

import math
import pytest
from src.engine.distributions import (
    normal_cdf,
    normal_ppf,
    student_t_cdf,
    student_t_ppf,
    nct_cdf
)
from src.engine.solver import (
    compute_t2_indep_power,
    solve_a_priori_t2_indep,
    run_calculation
)

def test_normal_distribution_inversion():
    """Normal ppf ve cdf birbirinin tersi olmalıdır."""
    for p in [0.001, 0.01, 0.05, 0.1, 0.5, 0.9, 0.95, 0.99, 0.999]:
        z = normal_ppf(p)
        recovered_p = normal_cdf(z)
        assert abs(p - recovered_p) < 1e-7

def test_student_t_quantile():
    """Öğrenci t quantilesi standart tablolara uymalıdır."""
    # df=10, p=0.975 için kritik t yaklaşık 2.2281 olmalı
    t_val = student_t_ppf(0.975, 10)
    assert abs(t_val - 2.2281) < 0.001
    # df=100, p=0.975 için yaklaşık 1.9840 olmalı
    t_val_100 = student_t_ppf(0.975, 100)
    assert abs(t_val_100 - 1.9840) < 0.001

def test_canonical_a_priori_vector():
    """Ödev yönergesindeki kanonik örnek tam eşleşmelidir."""
    # tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1
    res = solve_a_priori_t2_indep(tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1.0)
    assert res["n1"] == 105
    assert res["n2"] == 105
    assert res["n_total"] == 210
    assert res["df"] == 208
    assert abs(res["critical"] - 1.9714) <= 0.0001
    assert abs(res["ncp"] - 3.6228) <= 0.0001
    assert abs(res["actual_power"] - 0.9501) <= 0.0001

def test_unbalanced_ratio_ceiling_rule():
    """[REA]: ratio != 1 durumunda tavan kuralı (ceil) uygulanmalıdır."""
    # d=0.5, alpha=0.05, power=0.80, ratio=1.5
    res = solve_a_priori_t2_indep(tails=2, d=0.5, alpha=0.05, power=0.80, ratio=1.5)
    assert res["n1"] == 54
    assert res["n2"] == 81
    assert res["n_total"] == 135
    assert res["n2"] == math.ceil(res["n1"] * 1.5)
    assert res["actual_power"] >= 0.80

def test_post_hoc_canonical_vector():
    """Canonical vektörün post-hoc testi doğrulanmalıdır."""
    res = compute_t2_indep_power(tails=2, d=0.5, alpha=0.05, n1=105, n2=105)
    assert res["df"] == 208
    assert res["ncp"] == 3.6228
    assert res["actual_power"] == 0.9501

def test_invalid_parameters_raise_value_error():
    """Geçersiz girdiler uygun hata fırlatmalıdır."""
    # Negatif etki boyutu
    with pytest.raises(ValueError, match="Effect size d must be > 0"):
        solve_a_priori_t2_indep(tails=2, d=-0.1, alpha=0.05, power=0.95)
    
    # Geçersiz alfa
    with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
        solve_a_priori_t2_indep(tails=2, d=0.5, alpha=1.5, power=0.95)
        
    # Geçersiz güç
    with pytest.raises(ValueError, match="Power must be between 0 and 1"):
        solve_a_priori_t2_indep(tails=2, d=0.5, alpha=0.05, power=-0.5)

    # Geçersiz tails
    with pytest.raises(ValueError, match="Tails must be 1 or 2"):
        solve_a_priori_t2_indep(tails=3, d=0.5, alpha=0.05, power=0.95)

    # Desteklenmeyen test ailesi
    with pytest.raises(ValueError, match="Unsupported test family"):
        run_calculation(test="anova-twoway", mode="a-priori", tails=2, d=0.5, alpha=0.05, power=0.95)
