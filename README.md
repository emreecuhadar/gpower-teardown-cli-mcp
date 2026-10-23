# G*Power Clean-Room Reverse Engineering & AI Agent Suite (`gpower-clone`)

> **YZM301 · Yazılım Gerçekleme ve Test Dersi · Teardown Sprint**  
> **Hedef Puan:** 110 / 110 (Temel CLI 85 Puan + 15 Puan MCP Sunucusu + 10 Puan Klinik AI Ajanı)

---

## 🏆 Tamamlanan Katmanlar ve Bonus Beyanı

Bu projede temel gereksinim ve her iki bonus katman eksiksiz olarak gerçeklenmiştir:
- [x] **Temel Katman: CLI (85 Puan):** Kâhin G*Power 3.1.9.7 ile %100 tam eşleşen tek satır JSON CLI aracı (`gpower-clone`). Gizli vektörler kapı kuralı (%90+) aşılmıştır.
- [x] **Bonus Katman 1: MCP Sunucusu (+15 Puan -> 100 Puan):** Model Context Protocol standartlarına tam uyumlu, stdio tabanlı JSON-RPC 2.0 sunucusu. Aynı hesap motorunu çağıran sıfır-kopyalama adaptörü.
- [x] **Bonus Katman 2: Klinik AI Ajanı (+10 Puan -> 110 Puan):** Hekimlerin Türkçe klinik araştırma sorularını anlayan, Sistem 1 sınıflandırıcısı ile test ailesini seçen, güven skoru < 0.75 olduğunda hekime soran ve hesabı MCP aracı üzerinden yaptıran doğal dil ajanı. 10 soruluk değerlendirme seti ve ölçülmüş token/süre kıyaslama raporu mevcuttur.

---

## 📸 REA ve Ghidra Oturum Uygunluk Kontrolü

**Soru:** *REA araçları ve Ghidra sağlayıcısı bu oturumda kullanılabilir mi?*  
**Ajan Yanıtı:**  
> *"Evet. Bu oturumda statik ve dinamik tersine mühendislik analizleri, Ghidra disassembly/decompiler sembol ve dize analizleri, REA etiketleme protokolü ([DOK], [REA], [AJAN]) ve temiz oda (Clean-Room) şartname üretim metodolojisi tam olarak uygulanabilir. Bu oturum Oturum 1 (Analist / REA) rolünü üstlenerek G\*Power 3.1.9.7 binary davranışını, sayısal kök bulma mantığını, sınır koşullarını ve yuvarlama mekanizmalarını inceleyip SPEC.md ve LEDGER.md dokümanlarını üretmeye hazırdır."*

---

## 🔬 Hedef Test Ailesi: `t2-indep`
- **İstatistiksel Test:** İki Bağımsız Örneklem Ortalama Farkı t-Testi (`Means: Difference between two independent means, two groups` - İlaç ve Plasebo).
- **Desteklenen Modlar:**
  - `a-priori`: Verilen $d, \alpha, \text{power}, \text{tails}, \text{ratio}$ ile gereken tamsayı örneklem boyutu ($n_1, n_2, N_{total}$) hesabı.
  - `post-hoc`: Verilen $d, \alpha, n_1, n_2, \text{tails}$ ile gerçekleşen istatistiksel güç ($1-\beta$) hesabı.

---

## ⚙️ Kurulum ve Gereksinimler

Proje **Zero-Dependency (Sıfır Dış Bağımlılık)** prensibiyle tasarlanmıştır. Yalnızca Python 3.10+ kurulu olması yeterlidir.

```bash
# Repoyu klonlayın
git clone <repo-url>
cd "yazılım gerçekleme test gpower"

# Python sürümünü kontrol edin (3.10 veya üzeri önerilir)
python --version
```

---

## 🚀 Çalıştırma Talimatları

### 1. CLI Kullanımı (`gpower-clone`)

#### A-Priori Modu (Kanonik Örnek):
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
```
**Çıktı (Tek Satır JSON):**
```json
{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}
```

#### Eşit Olmayan Grup Oranı (`ratio != 1` - Tavan Yuvarlama):
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.80 --ratio 1.5
```
**Çıktı:**
```json
{"n1":54,"n2":81,"n_total":135,"actual_power":0.8066,"critical":1.9779,"df":133,"ncp":2.846}
```

#### Post-Hoc Modu:
```bash
python src/cli.py --test t2-indep --mode post-hoc --tails 2 --d 0.5 --alpha 0.05 --n1 64 --n2 64
```
**Çıktı:**
```json
{"n1":64,"n2":64,"n_total":128,"actual_power":0.8015,"critical":1.979,"df":126,"ncp":2.8284}
```

#### Hata Durumu (Geçersiz Girdi):
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d -0.5 --alpha 0.05 --power 0.95
```
**Çıktı (Exit Code 1):**
```json
{"error":"Effect size d must be > 0. Girilen: -0.5"}
```

*(Windows için `gpower-clone.bat`, Linux/macOS için `./gpower-clone` betikleri kök dizinde hazırdır.)*

---

### 2. MCP Sunucusu (Model Context Protocol)

MCP sunucusu Claude Desktop, Cursor veya Antigravity gibi AI ortamlarına stdio üzerinden bağlanabilir:

```bash
python src/mcp_server.py
```

#### MCP Araç Şeması (Tool Schema):

1. **`calculate_sample_size_t2_indep`**:
   - `d` (number): Cohen's d etki büyüklüğü.
   - `alpha` (number): Anlamlılık düzeyi (Tip I hata).
   - `power` (number): Hedef güç ($1-\beta$).
   - `tails` (integer): Hipotez yönü (1 veya 2).
   - `ratio` (number, opsiyonel): $n_2/n_1$ oranı (varsayılan: 1.0).
   - **Çıktı Alanları:** `n1`, `n2`, `n_total`, `actual_power`, `critical`, `df`, `ncp`.

2. **`calculate_power_t2_indep`**:
   - `d` (number): Cohen's d etki büyüklüğü.
   - `alpha` (number): Anlamlılık düzeyi.
   - `n1` (integer): Grup 1 denek sayısı.
   - `n2` (integer): Grup 2 denek sayısı.
   - `tails` (integer): 1 veya 2.
   - **Çıktı Alanları:** `n1`, `n2`, `n_total`, `actual_power`, `critical`, `df`, `ncp`.

---

### 3. Klinik AI Ajanı ve 10 Soruluk Değerlendirme Seti

Hekimin doğal dil sorusunu işleyen ajanı tek başına denemek için:
```bash
python src/agent.py
```

10 soruluk kapsamlı benchmark ve değerlendirme testini çalıştırmak ve log kayıtlarını incelemek için:
```bash
python eval/run_eval.py
```

---

## 🧪 Testlerin Çalıştırılması ve Kapı Doğrulaması

Diferansiyel testler kâhin veri seti (`oracle/gpower_vectors.csv`) üzerindeki 35 vektörü doğrular:

```bash
# Diferansiyel test ve %90+ Kapı doğrulaması
python tests/test_differential.py

# Birim ve CLI / MCP parite testleri
python tests/test_engine.py
python tests/test_cli.py
python tests/test_mcp.py
```

*(Eğer `pytest` kuruluysa doğrudan `pytest tests/` komutu da çalıştırılabilir.)*

---

## 📁 Proje Dizin Yapısı

```text
├── .gitignore               # GPower.exe ve binary'leri dışlayan temiz oda kuralları
├── README.md                # Ana dokümantasyon, kurulum ve atıflar
├── SPEC.md                  # Gherkin formatında davranışsal kabul kriterleri
├── LEDGER.md                # [DOK], [REA] ve [AJAN] etiketli kanıt defteri
├── HALLUCINATIONS.md        # Ajanın yanlış çıkardığı 3 kritik bulgu ve yakalayan testler
├── AGENT_COST.md            # Token tüketimi, maliyet ve süreç analizi
├── gpower-clone.bat         # Windows için doğrudan komut çalıştırıcı
├── gpower-clone             # Unix / macOS için doğrudan komut çalıştırıcı
├── prompts/                 # Temiz oda oturumlarının ilk prompt'ları
│   ├── session1_rea.md      # İnceleme ve analiz oturumu prompt'u
│   └── session2_cleanroom.md# Şartnameye dayalı temiz yazım oturumu prompt'u
├── oracle/                  # G*Power kâhin vektörleri ve ekran görüntüsü referansları
│   ├── gpower_vectors.csv   # 35 doğrulanmış GUI vektörü
│   └── README.md            # Kâhin açıklamaları
├── src/                     # Temiz oda kaynak kodları (Tek Motor Prensibi)
│   ├── engine/              # İstatistik motoru (Sıfır bağımlılık)
│   │   ├── distributions.py # Normal, Student-t ve Non-central t dağılımları
│   │   └── solver.py        # A-priori ve post-hoc diskret kök bulucu
│   ├── cli.py               # Sözleşmeye %100 uyumlu CLI katmanı
│   ├── mcp_server.py        # Model Context Protocol stdio sunucusu
│   └── agent.py             # Sistem 1 sınıflandırıcılı Klinik AI Ajanı
├── tests/                   # Doğrulama ve diferansiyel testler
│   ├── test_engine.py       # Matematiksel motor birim testleri
│   ├── test_cli.py          # CLI entegrasyon testleri
│   ├── test_mcp.py          # CLI ve MCP çıktı eşdeğerlik testleri
│   ├── test_differential.py # Kâhin üzerinde %90+ tam eşleşme kapı testi
│   └── report.md            # Diferansiyel test ve tolerans raporu
├── eval/                    # Değerlendirme ve benchmark
│   ├── clinic_10_eval.json  # 10 klinik soru ve altın standart yanıtlar
│   ├── run_eval.py          # Değerlendirme çalıştırıcısı
│   └── token_benchmark.md   # Ölçülmüş token ve süre karşılaştırma raporu
└── demo/                    # 60 saniyelik CLI video senaryosu
    └── demo_script.md       # Adım adım demo yönergesi
```

---

## 🔒 Etik, Temiz Oda ve Yasal Bilgiler

1. **Temiz Oda Prensibi:** Teslim edilen repoda hiçbir decompile edilmiş C++ kodu, IDA/Ghidra ham asm dökümü veya telifli dosya bulunmamaktadır. Tüm hesaplama motoru `SPEC.md` matematiksel modeline dayanılarak sıfırdan yazılmıştır.
2. **GPower.exe Dağıtımı:** `GPower.exe` repoya **kesinlikle dahil edilmemiştir** ve `.gitignore` ile korunmaktadır.
3. **Resmi G*Power Sürüm Bilgisi:**
   - **Yazılım:** G*Power 3.1.9.7 for Windows (March 2020)
   - **Resmi SHA-256 Hash'i:** `c48858e92823aa5098a729e2f41e5ff0d1a44415cf24c29ea77dc30f1469e6b4`
   - **Resmi İndirme:** [Heinrich-Heine-Universität Düsseldorf](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower)
4. **Demo Video:**
   - Demo video çekim senaryosu `demo/demo_script.md` dosyasında yer almaktadır.

---

## 📚 Kaynakça ve Yazarlara Atıf

Bu çalışma, G*Power yazılımının değerli yazarlarının bilim dünyasına sunduğu akademik çalışmalara dayanmaktadır:

- **Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007).** G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences. *Behavior Research Methods*, 39(2), 175–191.
- **Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009).** Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses. *Behavior Research Methods*, 41(4), 1149–1160.
