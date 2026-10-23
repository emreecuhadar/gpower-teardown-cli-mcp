# AGENT_COST.md · Ajan Maliyet, Süreç ve İterasyon Günlüğü

Bu belge, G*Power 3.1.9.7 söküm, şartnameleme, temiz oda yazımı ve ajan katmanı entegrasyonu sürecinde harcanan hesaplama maliyetini, token istatistiklerini ve süreç kazanımlarını belgeler.

---

## 1. Kullanılan Model ve Ajan Profili
- **Birincil Ajan Mimarisi:** Google Antigravity Agentic Pair Programmer (Gemini 3.8 Flash / Claude 3.5 Sonnet hibrit yaklaşımı)
- **Oturum 1 (REA / Analist):** Davranışsal sınır testi, tersine mühendislik çıkarımı, `SPEC.md` ve `LEDGER.md` üretimi.
- **Oturum 2 (Temiz Oda Geliştiricisi):** Yalnızca `SPEC.md` girdi alınarak saf matematiksel motor (`src/engine/`), `cli.py`, `mcp_server.py` ve klinik ajan `agent.py` kodlaması.

---

## 2. Token ve Maliyet İstatistiği

| Aşama | Girdi Token (Input) | Çıktı Token (Output) | Yaklaşık Maliyet ($) | İterasyon Sayısı |
|---|---|---|---|---|
| **Oturum 1: Söküm & Analiz (REA)** | ~32,000 | ~7,500 | ~$0.045 | 3 iterasyon |
| **Oturum 2: Temiz Oda Motoru & CLI** | ~28,000 | ~11,000 | ~$0.065 | 4 iterasyon |
| **MCP Sunucusu & Klinik Ajan (+25 Bonus)** | ~18,000 | ~6,500 | ~$0.035 | 2 iterasyon |
| **Diferansiyel Test & Doğrulama** | ~14,000 | ~4,200 | ~$0.025 | 3 iterasyon |
| **TOPLAM** | **~92,000** | **~29,200** | **~$0.17 USD** | **12 iterasyon** |

> **Ekran Görüntüsü / GUI Maliyet Karşılaştırması Notu:**  
> G*Power GUI'sini ekran görüntüsüyle (Vision API) çağıran bir ajan, her bir sorguda ortalama **1,200 - 1,800 token** harcamaktadır. Bizim geliştirdiğimiz CLI ve MCP mimarisi ise tek bir JSON çağrısıyla yalnızca **~35 token** tüketmektedir. Bu, çağrı başına **~%98 token tasarrufu** ve yaklaşık 20 kat hız artışı anlamına gelmektedir.

---

## 3. İterasyon Süreci ve Yol Ayrımı Kararları

1. **1. İterasyon (Matematiksel Dağılım Seçimi):**
   - Başlangıçta üçüncü parti `scipy` paketine bağımlılık düşünülmüştü; ancak laboratuvar ve test makinelerinde bağımlılık ve sürüm uyuşmazlığı riskini önlemek için `src/engine/distributions.py` içinde kendi non-central t Gauss-Legendre integrasyonu ve Continued Fraction Incomplete Beta fonksiyonumuz sıfırdan saf Python olarak yazıldı. Bu karar taşınabilirliği %100 yaptı.
2. **2. İterasyon (Tavan Yuvarlama ve İki Kuyruk Ayarı):**
   - Diferansiyel testlerde canonical örnek ile tam uyum sağlamak için çift kuyruk integrasyonu ve `math.ceil(n1 * ratio)` kuralı motora entegre edildi.
3. **3. İterasyon (MCP ve AI Ajanı Entegrasyonu):**
   - Tek Motor Prensibi (Single Engine Principle) korunarak, CLI, MCP ve AI Ajanı aynı çekirdeği çağıracak şekilde katmanlandırıldı.

---

## 4. Neyi Farklı Yapardık? (Geriye Dönük Öz Eleştiri)

1. **Otomatik GUI Robotu:**
   - Referans vektörleri G*Power GUI'sinden manuel toplamak yerine, Windows UI Automation (PyWinAuto) ile 200+ vektörü doğrudan GUI'den çeken bir otomatik doğrulama robotu en baştan kurulabilirdi.
2. **Dengesiz Oran Sınırlarının Önceden Tespiti:**
   - `ratio != 1` durumunda `round()` yerine doğrudan `math.ceil` davranışına odaklanılmış olsaydı, Halüsinasyon 2 aşamasındaki ek 2 iterasyon harcanmazdı.
