# SPEC.md · Kabul Kriterleri Şartnamesi (Gherkin Formatında)

Bu şartname, temiz oda prensibiyle geliştirilecek olan `t2-indep` (İki Bağımsız Örneklem t-Testi) hesaplama motorunun davranışsal kabul kriterlerini tanımlar.

---

```gherkin
Özellik: İki Bağımsız Örneklem t-Testi (t2-indep) Güç ve Örneklem Boyutu Hesaplama Motoru
  Bir araştırmacı veya klinik AI ajanı olarak
  G*Power 3.1.9.7 matematiksel sonuçlarıyla tam uyumlu
  A-priori örneklem boyutu ve post-hoc istatistiksel güç hesabı yapmak istiyorum.

  Arka Plan:
    Diyelim ki hesaplama motoru başlatıldı
    Ve hata durumlarında standart JSON hata mesajı dönüyor

  # ========================================================
  # SENARYO 1: A-Priori Modu - Standart İki Yönlü Eşit Gruplar (Canonical Case)
  # ========================================================
  Senaryo: İki yönlü, orta etki büyüklüğü ve eşit gruplarla örneklem boyutu hesaplama
    Eğer test türü "t2-indep" olarak seçilirse
    Ve hesaplama modu "a-priori" ise
    Ve hipotez yönü "tails" = 2 ise
    Ve etki büyüklüğü "d" = 0.5 ise
    Ve anlamlılık düzeyi "alpha" = 0.05 ise
    Ve hedeflenen güç "power" = 0.95 ise
    Ve grup oranı "ratio" = 1.0 ise
    Hesaplama motoru çalıştırıldığında
    O zaman dönen "n1" değeri tam olarak 105 olmalıdır
    Ve dönen "n2" değeri tam olarak 105 olmalıdır
    Ve dönen "n_total" değeri tam olarak 210 olmalıdır
    Ve dönen "df" serbestlik derecesi tam olarak 208 olmalıdır
    Ve dönen "critical" kritik t değeri 1.9714 olmalıdır (+/- 0.0001)
    Ve dönen "ncp" non-centrality parametresi 3.6228 olmalıdır (+/- 0.0001)
    Ve dönen "actual_power" değeri 0.9501 olmalıdır (+/- 0.0001)

  # ========================================================
  # SENARYO 2: A-Priori Modu - Tek Yönlü Test
  # ========================================================
  Senaryo: Tek yönlü test ile örneklem boyutu hesaplama
    Eğer test türü "t2-indep" olarak seçilirse
    Ve hesaplama modu "a-priori" ise
    Ve hipotez yönü "tails" = 1 ise
    Ve etki büyüklüğü "d" = 0.5 ise
    Ve anlamlılık düzeyi "alpha" = 0.05 ise
    Ve hedeflenen güç "power" = 0.80 ise
    Ve grup oranı "ratio" = 1.0 ise
    Hesaplama motoru çalıştırıldığında
    O zaman dönen "n1" değeri tam olarak 50 olmalıdır
    Ve dönen "n2" değeri tam olarak 50 olmalıdır
    Ve dönen "n_total" değeri tam olarak 100 olmalıdır
    Ve dönen "actual_power" en az 0.80 olmalıdır

  # ========================================================
  # SENARYO 3: A-Priori Modu - Eşit Olmayan Grup Oranı (Unbalanced Allocation & Ceiling)
  # ========================================================
  Senaryo: Eşit olmayan grup oranıyla (ratio != 1) tavan yuvarlama kuralı
    Eğer test türü "t2-indep" olarak seçilirse
    Ve hesaplama modu "a-priori" ise
    Ve hipotez yönü "tails" = 2 ise
    Ve etki büyüklüğü "d" = 0.5 ise
    Ve anlamlılık düzeyi "alpha" = 0.05 ise
    Ve hedeflenen güç "power" = 0.80 ise
    Ve grup oranı "ratio" = 1.5 ise
    Hesaplama motoru çalıştırıldığında
    O zaman "n2" değeri ceil(n1 * ratio) kuralına tam uymalıdır
    Ve dönen "n1" değeri tam olarak 54 olmalıdır
    Ve dönen "n2" değeri tam olarak 81 olmalıdır
    Ve dönen "n_total" değeri tam olarak 135 olmalıdır
    Ve dönen "actual_power" değeri hedeflenen güce eşit veya büyük olmalıdır

  # ========================================================
  # SENARYO 4: Post-Hoc Modu - Mevcut Örneklem İle Güç Hesabı
  # ========================================================
  Senaryo: Verilen n1 ve n2 ile gerçekleşen gücü hesaplama
    Eğer test türü "t2-indep" olarak seçilirse
    Ve hesaplama modu "post-hoc" ise
    Ve hipotez yönü "tails" = 2 ise
    Ve etki büyüklüğü "d" = 0.5 ise
    Ve anlamlılık düzeyi "alpha" = 0.05 ise
    Ve grup 1 boyutu "n1" = 64 ise
    Ve grup 2 boyutu "n2" = 64 ise
    Hesaplama motoru çalıştırıldığında
    O zaman dönen "df" değeri 126 olmalıdır
    Ve dönen "actual_power" değeri 0.8015 olmalıdır (+/- 0.0001)

  # ========================================================
  # SENARYO 5: Sınır Koşulları ve Hata Yönetimi (Boundary & Edge Cases)
  # ========================================================
  Senaryo Taslağı: Geçersiz parametre girişlerinde standart JSON hatası dönmelidir
    Eğer test türü "t2-indep" ise
    Ve geçersiz bir "<parametre>" değeri "<deger>" olarak verilirse
    Hesaplama motoru veya CLI çağrıldığında
    O zaman çıkış kodu sıfırdan farklı (1) olmalıdır
    Ve standart çıktı JSON formatında '{"error": "<hata_mesaji>"}' içermelidir

    Örnekler:
      | parametre | deger  | hata_mesaji                       |
      | d         | 0.0    | Effect size d must be > 0         |
      | d         | -0.5   | Effect size d must be > 0         |
      | alpha     | 0.0    | Alpha must be between 0 and 1     |
      | alpha     | 1.0    | Alpha must be between 0 and 1     |
      | power     | 0.0    | Power must be between 0 and 1     |
      | power     | 1.0    | Power must be between 0 and 1     |
      | ratio     | -1.0   | Allocation ratio must be positive |
      | tails     | 3      | Tails must be 1 or 2              |
      | test      | xyz    | Unsupported test family           |
```
