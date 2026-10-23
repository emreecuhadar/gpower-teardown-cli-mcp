"""
Saf Python İstatistiksel Dağılım Modülü (Zero-Dependency Statistical Engine).
Öğrenci t, Normal ve Merkezi Olmayan (Non-central) t dağılımı fonksiyonlarını içerir.
"""

import math

def normal_cdf(x: float) -> float:
    """Standart normal dağılım kümülatif yoğunluk fonksiyonu (CDF)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

def normal_ppf(p: float) -> float:
    """
    Standart normal dağılım ters CDF (Quantile / PPF) fonksiyonu.
    Acklam'ın yüksek hassasiyetli rasyonel yaklaşım algoritması (hata < 1.15e-9).
    """
    if p <= 0.0 or p >= 1.0:
        raise ValueError(f"Olasılık p değeri (0, 1) aralığında olmalıdır. Girilen: {p}")
    
    a = [
        -3.969683028665376e+01,  2.209460984245205e+02,
        -2.759285104469687e+02,  1.383577518672690e+02,
        -3.066479806614716e+01,  2.506628277459239e+00
    ]
    b = [
        -5.447609879822406e+01,  1.615858368580409e+02,
        -1.556989798598866e+02,  6.680131188771972e+01,
        -1.328068155288572e+01
    ]
    c = [
        -7.784894002430293e-03, -3.223964580411365e-01,
        -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00,  2.938163982698783e+00
    ]
    d = [
         7.784695709041462e-03,  3.224671290700398e-01,
         2.445134137142996e+00,  3.754408661907416e+00
    ]

    q = p - 0.5
    if abs(q) <= 0.42:
        r = q * q
        num = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        den = (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
        return num / den
    else:
        r = p if q < 0 else 1.0 - p
        r = math.log(-math.log(r))
        x = c[0] + r * (c[1] + r * (c[2] + r * (c[3] + r * (c[4] + r * c[5]))))
        x = x / (1.0 + r * (d[0] + r * (d[1] + r * (d[2] + r * d[3]))))
        return -x if q < 0 else x

def betainc(a: float, b: float, x: float, max_iter: int = 250, eps: float = 1e-15) -> float:
    """
    Düzenli Tamamlanmamış Beta Fonksiyonu I_x(a, b).
    Lentz sürekli kesirler yöntemi ile yüksek hassasiyetli hesaplama.
    """
    if x < 0.0 or x > 1.0:
        raise ValueError(f"x değeri [0, 1] aralığında olmalıdır. Girilen: {x}")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0

    # Simetri dönüşümü
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - betainc(b, a, 1.0 - x, max_iter, eps)

    ln_beta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(a * math.log(x) + b * math.log(1.0 - x) - ln_beta) / a

    f = 1.0
    c = 1.0
    d = 1.0 - (a + b) * x / (a + 1.0)
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    f = f * d

    for m in range(1, max_iter):
        # Çift adım (2m)
        num_even = m * (b - m) * x / ((a + 2.0 * m - 1.0) * (a + 2.0 * m))
        d = 1.0 + num_even * d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + num_even / c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        f = f * (c * d)

        # Tek adım (2m + 1)
        num_odd = -(a + m) * (a + b + m) * x / ((a + 2.0 * m) * (a + 2.0 * m + 1.0))
        d = 1.0 + num_odd * d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0 + num_odd / c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        delta = c * d
        f = f * delta

        if abs(delta - 1.0) < eps:
            break

    return front * f

def student_t_cdf(t: float, df: float) -> float:
    """Merkezi Student's t dağılımı kümülatif yoğunluk fonksiyonu (CDF)."""
    if df <= 0:
        raise ValueError(f"Serbestlik derecesi df > 0 olmalıdır. Girilen: {df}")
    if t == 0.0:
        return 0.5
    x = df / (df + t * t)
    val = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - val if t > 0 else val

def student_t_ppf(p: float, df: float) -> float:
    """
    Merkezi Student's t dağılımı ters CDF (Quantile / Critical t).
    Hill (1970) yaklaşımı ve Newton-Raphson iteratif rafinasyonu ile 1e-12 hassasiyet.
    """
    if p <= 0.0 or p >= 1.0:
        raise ValueError(f"Olasılık p değeri (0, 1) aralığında olmalıdır. Girilen: {p}")
    if p == 0.5:
        return 0.0
    if p < 0.5:
        return -student_t_ppf(1.0 - p, df)

    z = normal_ppf(p)
    if df > 2:
        x = z + (z**3 + z) / (4.0 * df) + (5.0 * z**5 + 16.0 * z**3 + 3.0 * z) / (96.0 * df**2)
    else:
        x = z

    for _ in range(25):
        val = student_t_cdf(x, df)
        err = val - p
        if abs(err) < 1e-12:
            break
        ln_pdf = (
            math.lgamma((df + 1.0) / 2.0)
            - math.lgamma(df / 2.0)
            - 0.5 * math.log(math.pi * df)
            - ((df + 1.0) / 2.0) * math.log(1.0 + x * x / df)
        )
        pdf = math.exp(ln_pdf)
        step = err / pdf
        x -= step
        if abs(step) < 1e-12:
            break
    return x

def nct_cdf(t: float, df: float, delta: float) -> float:
    """
    Merkezi Olmayan (Non-central) Student's t Dağılımı CDF'i.
    P(T <= t | df, delta)
    Gauss-Legendre / Simpson kompozit sayısal integrali ile hesaplanır.
    """
    if df <= 0:
        raise ValueError(f"Serbestlik derecesi df > 0 olmalıdır. Girilen: {df}")

    # Özel durum: delta == 0 iken merkezi t dağılımı
    if delta == 0.0:
        return student_t_cdf(t, df)

    u_max = max(4.0, 1.0 + 8.0 / math.sqrt(2.0 * df))
    n_steps = 400
    h = u_max / n_steps
    ln_const = math.log(2.0) + (df / 2.0) * math.log(df / 2.0) - math.lgamma(df / 2.0)

    def integrand(u: float) -> float:
        if u <= 0.0:
            return 0.0
        val = ln_const + (df - 1.0) * math.log(u) - 0.5 * df * u * u
        if val < -100.0:
            return 0.0
        fu = math.exp(val)
        return normal_cdf(t * u - delta) * fu

    total = integrand(0.0) + integrand(u_max)
    for i in range(1, n_steps):
        u = i * h
        weight = 4.0 if i % 2 == 1 else 2.0
        total += weight * integrand(u)
    
    res = total * (h / 3.0)
    return min(1.0, max(0.0, res))
