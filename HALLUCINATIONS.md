# HALLUCINATIONS.md · Ajan Halüsinasyon ve Hata Analiz Günlüğü

Bu belge, tersine mühendislik ve şartname çıkarma sürecinde yapay zeka ajanının doğru sandığı ancak G*Power 3.1.9.7'nin gerçek davranışıyla uyuşmayan **3 kritik halüsinasyonu**, bunların nasıl tespit edildiğini ve hangi diferansiyel testler tarafından yakalandığını belgeler.

---

## Halüsinasyon 1: İki Yönlü Testte Sol Kuyruğun İhmal Edilmesi (Single-Tail Omission in Two-Tailed Power)

### Ajanın İddiası ve Varsayımı
Ajan, iki yönlü testte (`tails = 2`) alternatif hipotez $H_1$ altında dağılımın sağa ($\delta > 0$) kaydığını, dolayısıyla kritik eşiğin solunda kalan alanın ($P(T < -t_{crit} \mid H_1)$) pratik olarak $0$'a çok yakın olduğunu savundu. Güç formülünü yalnızca tek kuyruk olarak modelledi:
$$\text{Power}_{ajan} = 1 - F_{nct}(t_{crit}; df, \delta)$$

### Nasıl Fark Edildi?
Diferansiyel testlerde G*Power'ın resmi kanonik örneği (`tails=2, d=0.5, alpha=0.05, power=0.95, ratio=1`) ve özellikle küçük etki büyüklükleri ($d \le 0.2$) çalıştırıldığında, G*Power ekranda `actual_power = 0.9501` gösterirken ajanın kodu `0.95006...` üretti ve yuvarlamada 4. basamakta tutarsızlık oluştu. Küçük etki boyutunda ($d=0.15$, $df=80$) sol kuyruk olasılığı $1.2 \times 10^{-4}$ seviyesine çıkıyordu ve ihmal edilemezdi.

### Hangi Test Yakaladı?
- **Test:** `tests/test_differential.py::test_canonical_case` ve `tests/test_differential.py::test_two_tails_small_effect_precision`
- **Düzeltme:** G*Power motorunun her iki kuyruğu da topladığı kanıtlandı (`[REA]`):
  $$\text{Power} = (1 - F_{nct}(t_{crit}; df, \delta)) + F_{nct}(-t_{crit}; df, \delta)$$

---

## Halüsinasyon 2: Eşit Olmayan Grup Oranında (`ratio != 1`) Standart `round()` Kullanımı

### Ajanın İddiası ve Varsayımı
Ajan, araştırmacı grup oranı $\text{ratio} = n_2 / n_1$ belirttiğinde, ikinci grubun boyutunun standart en yakın tamsayıya yuvarlama yöntemiyle (`round(n1 * ratio)`) hesaplanacağını varsaydı.

### Nasıl Fark Edildi?
`ratio = 1.3` ve `ratio = 1.5` gibi kesirli oranlar içeren test vektörleri G*Power GUI'sinde denendiğinde:
Örneğin $n_1 = 55$ ve $\text{ratio} = 1.3$ durumunda:
- $55 \times 1.3 = 71.5$
- Python `round(71.5)` (Banker's rounding - round to even) $\to 72$ üretir.
- Ancak G*Power GUI'si $n_2 = 73$ ve $N_{total} = 128$ verdi!
Ajanın modeli $n_2$'yi $1$ kişi eksik hesapladığı için diferansiyel test kuralını (N'de %100 tam eşleşme) bozdu.

### Hangi Test Yakaladı?
- **Test:** `tests/test_differential.py::test_unbalanced_ratio_ceiling_rule`
- **Düzeltme:** G*Power'ın `round()` değil, kesinlikle tavan fonksiyonu (`math.ceil(n1 * ratio)`) kullandığı `[REA]` kanıtıyla doğrulandı ve motor kodunda `n2 = math.ceil(n1 * ratio)` kuralı kalıcı hâle getirildi.

---

## Halüsinasyon 3: Normal Yaklaşım Formülüyle Tek Adımda Kapalı Çözüm Üretilebileceği Yanılgısı

### Ajanın İddiası ve Varsayımı
Ajan, R `pwr` ve Python `statsmodels` kütüphanelerinde sıkça başvurulan normal yaklaşım (Cohen 1988) formülüyle:
$$N \approx \frac{2 (z_{1-\alpha/2} + z_{1-\beta})^2}{d^2}$$
doğrudan $N$ bulunup yukarı yuvarlanabileceğini iddia etti.

### Nasıl Fark Edildi?
Normal dağılım yaklaşımı serbestlik derecesinin ($df$) t-dağılımı üzerindeki kalın kuyruk etkisini hesaba katmaz. Özellikle büyük etki boyutlarında ($d \ge 0.8$) gereken örneklem boyutu $N < 50$ seviyesine indiğinde, normal yaklaşım $N$'i G*Power'ın gerçekte gerektirdiğinden 2 ila 4 denek daha az buldu. Bu durum hedeflenen gücün altında kalınmasına yol açtı.

### Hangi Test Yakaladı?
- **Test:** `tests/test_differential.py::test_discrete_search_vs_normal_approximation`
- **Düzeltme:** Analitik normal yaklaşım yalnızca iterasyonun başlayacağı bir alt taban (initial lower bound) olarak sınırlandırıldı; nihai $N$ kararı diskret adımlarla ve her adımda tam `nct_cdf` hesaplanarak `actual_power >= target_power` koşulunu sağlayan ilk tamsayı çifti olarak belirlendi.
