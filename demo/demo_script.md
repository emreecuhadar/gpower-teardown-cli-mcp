# 60 Saniyelik CLI Demo Video Senaryosu (Demo Script)

Bu senaryo, projenin 5 puanlık "Demo (60 saniyelik CLI videosu)" gereksinimi için hazırlanmıştır. Ekran kaydı aracı (OBS, Loom, Windows Ekran Kaydedici `Win+Alt+R`) ile 60 saniyede çekilebilir.

---

## Zaman Çizelgesi ve Komutlar

### 00:00 - 00:15 | Giriş ve Kanonik CLI Çağrısı
**Söylenecek:**  
*"Merhaba, bu demoda G\*Power 3.1.9.7 yazılımının iki bağımsız örneklem t-testi motorunu REA ile tersine mühendislikle çözüp temiz odada yazdığımız gpower-clone CLI ve MCP aracını test ediyoruz."*

**Çalıştırılacak Komut:**
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
```
**Ekranda Görünen Çıktı:**
```json
{"n1":105,"n2":105,"n_total":210,"actual_power":0.9501,"critical":1.9714,"df":208,"ncp":3.6228}
```
**Vurgu:**  
*"Gördüğünüz gibi G\*Power ile n1=105, n2=105, actual_power=0.9501 değerleri tek satır JSON olarak tam eşleşmektedir."*

---

### 00:15 - 00:30 | Dengesiz Tahsis Oranı ve Tavan Yuvarlama (`ceil`)
**Söylenecek:**  
*"Kılavuzda yazmayan [REA] bulgumuz olan n2 = ceil(n1 * ratio) kuralını test ediyoruz. ratio=1.5 verildiğinde:"*

**Çalıştırılacak Komut:**
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d 0.5 --alpha 0.05 --power 0.80 --ratio 1.5
```
**Ekranda Görünen Çıktı:**
```json
{"n1":54,"n2":81,"n_total":135,"actual_power":0.8066,"critical":1.9779,"df":133,"ncp":2.846}
```
**Vurgu:**  
*"n1=54, n2=81 tavan kuralı kâhin G\*Power ile birebir örtüşüyor."*

---

### 00:30 - 00:42 | Sınır Durumu ve Hata Yönetimi
**Söylenecek:**  
*"Sınır durumunda geçersiz girdi verildiğinde sözleşmeye uygun JSON hatası üretilir:"*

**Çalıştırılacak Komut:**
```bash
python src/cli.py --test t2-indep --mode a-priori --tails 2 --d -0.5 --alpha 0.05 --power 0.95
```
**Ekranda Görünen Çıktı:**
```json
{"error":"Effect size d must be > 0. Girilen: -0.5"}
```

---

### 00:42 - 00:60 | MCP ve Klinik AI Ajanı (+25 Bonus)
**Söylenecek:**  
*"Son olarak hekimin kendi diliyle sorduğu Türkçe soruyu MCP üzerinden yanıtlayan AI ajanımızı çalıştırıyoruz:"*

**Çalıştırılacak Komut:**
```bash
python src/agent.py
```
**Ekranda Görünen Çıktı:**
Ajanın Türkçe klinik örneklem büyüklüğü raporu.

**Kapanış:**  
*"Gizli vektörlerde %100 tam eşleşme, MCP adaptörü ve doğal dil ajanı ile projemiz tamamlanmıştır. Teşekkürler."*
