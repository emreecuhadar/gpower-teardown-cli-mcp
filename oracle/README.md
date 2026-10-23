# Kâhin (Oracle) Veri Seti Dokümantasyonu

Bu dizin, diferansiyel testlerde "kâhin" (ground truth) olarak kullanılan G*Power 3.1.9.7 çıktılarını ve referans vektörlerini içerir.

## 1. Veri Kaynağı
- **Yazılım:** G*Power 3.1.9.7 (Windows x86)
- **Resmi İndirme Kaynağı:** Heinrich-Heine-Universität Düsseldorf (psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower)
- **Yazarlar:** Franz Faul, Edgar Erdfelder, Albert-Georg Lang, Axel Buchner (2007, 2009)

## 2. Vektör Çeşitliliği ve Kapsam (`gpower_vectors.csv`)
Veri setinde toplam **35 adet** doğrudan G*Power GUI arayüzünden toplanmış referans vektörü yer alır:
- **Etki Büyüklükleri ($d$):** 0.1 (çok küçük), 0.2, 0.3, 0.4, 0.5 (orta), 0.6, 0.7, 0.8 (büyük), 1.0, 1.5, 2.0 (uç etki)
- **Anlamlılık Düzeyleri ($\alpha$):** 0.001 (aşırı katı), 0.01, 0.05 (standart), 0.10 (gevşek)
- **Hedef Güç Değerleri ($1-\beta$):** 0.70, 0.80, 0.85, 0.90, 0.95, 0.99
- **Hipotez Yönü (tails):** 1 (tek yönlü) ve 2 (çift yönlü)
- **Grup Tahsis Oranları (ratio):** 0.5 (2:1), 1.0 (1:1 dengeli), 1.2, 1.5 (2:3), 2.0 (1:2)
- **Modlar:** `a-priori` (örneklem boyutu $N$ arama) ve `post-hoc` (verilen $n_1, n_2$ ile güç hesabı)

## 3. Ekran Görüntüsü Referansları
Her temel senaryonun G*Power arayüzündeki karşılığı kaydedilmiş olup, arayüzdeki şu alanlar doğrulanmıştır:
- `Total sample size` -> `n_total`
- `Sample size group 1` -> `n1`
- `Sample size group 2` -> `n2`
- `Degrees of freedom` -> `df`
- `Critical t` -> `critical`
- `Noncentrality parameter δ` -> `ncp`
- `Actual power` -> `actual_power`

## 4. Büyük Ölçekli Diferansiyel Test Üreticisi
500+ vektörlük otomatik diferansiyel test için `oracle/generate_extended_vectors.py` betiği kullanılabilir.
