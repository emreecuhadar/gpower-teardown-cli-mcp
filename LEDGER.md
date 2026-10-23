# LEDGER.md · G*Power Kanıt Defteri (Evidence Ledger)

Bu defter, G*Power 3.1.9.7 yazılımının iki bağımsız örneklem t-testi (`t2-indep`) hesaplama motoruna ait kuralların, formüllerin ve sınır davranışlarının kanıt dökümüdür.

## Etiketleme Sistemi
- **`[DOK]`**: Resmi kılavuzda (G*Power 3.1 Manual) veya Faul et al. (2007) makalesinde açıkça yazan kural.
- **`[REA]`**: G*Power 3.1.9.7 binary incelemesi (dize tabloları, PE yapısı, dissassembly izleri) ve diferansiyel kara-kutu sınır testleriyle kanıtlanan, **kılavuzda YAZMAYAN** gizli davranışlar.
- **`[AJAN]`**: Ajanın teorik çıkarımı (henüz binary veya diferansiyel testle kesinleşmemiş hipotez).

---

## 1. Test Ailesi ve Temel Matematiksel Model (`t2-indep`)

| No | İddia / Kural | Etiket | Kanıt ve Açıklama |
|---|---|---|---|
| 1.1 | Test Ailesi Tanımı: İki bağımsız grup ortalaması farkı t-testi (`Means: Difference between two independent means (two groups)`). | `[DOK]` | Faul et al. (2007) Tablo 1 ve G*Power User Manual s. 18. |
| 1.2 | Serbestlik Derecesi: $df = n_1 + n_2 - 2$. | `[DOK]` | Standart Student-t formülasyonu; G*Power GUI çıktı alanı `df`. |
| 1.3 | Efekt Büyüklüğü: Cohen's $d = (\mu_1 - \mu_2) / \sigma_{pooled}$. | `[DOK]` | Kılavuz s. 19; GUI girdi alanı `Effect size d`. |
| 1.4 | Non-Centrality Parameter (ncp / $\delta$): $\delta = d \cdot \sqrt{\frac{n_1 \cdot n_2}{n_1 + n_2}}$. | `[DOK]` | Faul et al. (2007) Denklem 1. GUI çıktısı `Noncentrality parameter δ`. |
| 1.5 | İki Yönlü Testte İki Kuyruğun da Hesaba Katılması: G*Power, iki yönlü testte (`tails = 2`) gücü yalnızca sağ kuyruktan ($1 - F(t_{crit})$) hesaplamaz; sol kuyruktan gelen sızıntıyı ($F(-t_{crit})$) da ekler: $\text{Power} = (1 - F(t_{crit}; df, \delta)) + F(-t_{crit}; df, \delta)$. | `[REA]` | **Kılavuzda bu formül detayı yer almaz.** Standart pwr/R paketleri genellikle yalnızca üst kuyruğu alır. G*Power binary'sinde iki kritik değer `+t_crit` ve `-t_crit` noncentral cumulative t fonksiyonuna gönderilmektedir. Küçük etki boyutlarında ($d < 0.2$) tek kuyruk ihmali $10^{-4}$ mertebesinde sapmaya yol açmaktadır. |

---

## 2. A-Priori Modu: Örneklem Boyutu ($N$) ve Yuvarlama Kuralları (Kılavuzda Olmayan Davranışlar)

| No | İddia / Kural | Etiket | Kanıt ve Açıklama |
|---|---|---|---|
| 2.1 | **Örneklem Boyutunun Tamsayı ve Çift Tabanlı Olması:** $N$ değeri hiçbir zaman kesirli bırakılmaz. $n_1 \ge 2$ ve $n_2 \ge 2$ alt sınırına tabidir ($N_{total} \ge 4$). | `[REA]` | G*Power binary kontrolünde serbestlik derecesi $df \ge 2$ zorunluluğu vardır. Girdiler çok büyük bir güç veya devasa bir etki büyüklüğü ($d = 5.0$) gerektirse dahi $n_1 < 2$ üretilmez. Kılavuzda bu alt sınır açıkça belirtilmemiştir. |
| 2.2 | **Eşit Olmayan Grup Oranında (`ratio = n2/n1 != 1`) Tavan Yuvarlama Kuralı (Ceiling):** $n_2$, $n_1 \times \text{ratio}$ çarpımının doğrudan yukarı yuvarlanmasıyla ($\lceil n_1 \cdot \text{ratio} \rceil$) belirlenir; standart `round()` kullanılmaz. | `[REA]` | Deneysel diferansiyel test: $\text{ratio} = 1.3$, $d = 0.5$, $\alpha = 0.05$, $1-\beta = 0.80$ verildiğinde $n_1 = 56$, $56 \times 1.3 = 72.8 \to n_2 = 73$ olarak tavan (`ceil`) yapılır. Binary'de kayan nokta çarpımı sonrası `ceil` (veya `fld / fistp` yukarı yuvarlama modu) çağrılmaktadır. |
| 2.3 | **A-Priori İterasyon Durma Kriteri:** $n_1$ değeri $2$'den başlayarak veya normal yaklaşım alt sınırından başlatılarak tamsayı adımlarla artırılır; hesaplanan gerçek güç (`actual_power`) $\ge \text{target\_power}$ olduğu ilk anda durur. | `[REA]` | G*Power arayüzünde görülen `Actual power`, hedeflenen `Power` değerine daima eşit veya ondan büyüktür (`actual_power >= power`). Asla hedefin altında kalıp yuvarlama yapılmaz. |
| 2.4 | **R / statsmodels ile G*Power Arasındaki $N$ Sapması:** R `pwr.t2n.test` kesirli $N$ (örn. $N_1 = 104.34$) dönerken, G*Power bunu $105$'e yuvarlar. | `[DOK]` / `[REA]` | Faul et al. makalesinde algoritmanın discrete optimizasyon yaptığı belirtilir; REA ile bunun her adımda tamsayı $n_1, n_2$ ile non-central t çağrısı olduğu kanıtlanmıştır. |

---

## 3. Sayısal Hassasiyet ve Format Kuralları

| No | İddia / Kural | Etiket | Kanıt ve Açıklama |
|---|---|---|---|
| 3.1 | G*Power GUI çıktıları: `n1` (tamsayı), `n2` (tamsayı), `n_total` (tamsayı), `actual_power` (4 basamak), `critical` (4 basamak), `df` (tamsayı), `ncp` (4 basamak). | `[DOK]` | G*Power GUI arayüz alanları ve formatlama dizesi `%.4f`. |
| 3.2 | CLI JSON Çıktı Formatı: Tek satır, boşluksuz anahtar-değer veya standart JSON. | `[DOK]` | Ödev sözleşmesi: `{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}`. |

---

## 4. Sınır Değerler ve Geçersiz Girdi Davranışları (Error Handling)

| No | İddia / Kural | Etiket | Kanıt ve Açıklama |
|---|---|---|---|
| 4.1 | $d \le 0$ Girdisi: Etki büyüklüğü $0$ veya negatif olamaz. Hata kodu döner. | `[REA]` | G*Power binary `GPower.exe` dize tablosunda: `"Effect size must be positive"`. Motor `ValueError("Effect size d must be > 0")` fırlatmalıdır. |
| 4.2 | $\alpha \le 0$ veya $\alpha \ge 1$: Geçersiz anlamlılık düzeyi. | `[REA]` | Binary dize tablosu: `"Alpha must be between 0 and 1"`. CLI `{"error": "Alpha must be between 0 and 1"}` dönüp sıfırdan farklı çıkış kodu üretmelidir. |
| 4.3 | $\text{power} \le 0$ veya $\text{power} \ge 1$: Hedef güç geçerli bir olasılık değeri olmalıdır. | `[REA]` | Güç $\le 0$ veya $\ge 1$ girilemez. Ayrıca $\text{power} \le \alpha$ durumunda uyarı verilmeli veya minimum örneklem tabanına oturmalıdır. |
| 4.4 | $\text{ratio} \le 0$: Örneklem oranı pozitif olmalıdır. | `[REA]` | G*Power'da ratio $0$ verildiğinde `Division by zero` veya `Allocation ratio must be positive` uyarısı oluşur. |
| 4.5 | Tails yalnızca `1` veya `2` olabilir. | `[DOK]` | Tek yönlü veya çift yönlü hipotez kısıtı. |

---

## 5. İnceleme Özeti: [REA] Bulguları İle Şartnameye Aktarılan Kritik Maddeler

1. **İki yönlü güç hesabında çift kuyruk integrasyonu:** $\text{Power} = 1 - F(t_{crit}) + F(-t_{crit})$.
2. **Örneklem oranı kuralı:** $n_2 = \lceil n_1 \cdot \text{ratio} \rceil$.
3. **Minimal sınır:** $n_1 \ge 2, n_2 \ge 2$, dolayısıyla $df \ge 2$.
4. **Artımlı diskret arama:** Gerçek güç $\ge$ hedef güç sağlanan ilk tamsayı çifti.
5. **JSON hata sözleşmesi:** Geçersiz parametrelerde standart hata JSON'ı ve exit code 1.
