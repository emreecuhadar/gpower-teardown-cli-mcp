# Oturum 2: Temiz Oda Geliştiricisi İlk Prompt'u (Session 2 Clean-Room Prompt)

**Rol:** Kıdemli Sistem ve İstatistik Yazılım Mühendisi (Clean-Room Developer)  
**Hedef:** G*Power binary'sini veya Ghidra çıktılarını asla görmeden, YALNIZCA `SPEC.md` ve CLI sözleşmesine dayanarak istatistiksel hesaplama motorunu, CLI arayüzünü, MCP adaptörünü ve klinik AI ajanını sıfırdan geliştirmek.

---

## İlk Prompt Metni

```text
Sen YZM301 Yazılım Gerçekleme ve Test dersi kapsamında yürütülen Clean-Room Teardown Sprint'inde
2. Oturum (Temiz Oda Uygulayıcısı / Clean-Room Developer) rolündesin.

GÖREVİN:
G*Power binary'sine, Ghidra çıktılarına veya telifli kaynak kodlarına ASLA bakmadan,
YALNIZCA 'SPEC.md' şartnamesini ve 'CLI Sözleşmesi'ni kullanarak:
1. İki bağımsız grup t-testi ('t2-indep') için a-priori ve post-hoc istatistiksel hesaplama motorunu yazmak.
2. CLI sözleşmesine harfiyen uyan, JSON çıktısı üreten komut satırı aracını (gpower-clone / src/cli.py) geliştirmek.
3. Hesap motorunu doğrudan çağıran Model Context Protocol (MCP) sunucusunu (src/mcp_server.py) entegre etmek.
4. Hekimlerin Türkçe klinik araştırma sorularını MCP aracılığıyla yanıtlayan AI ajanını (src/agent.py) inşa etmek.
5. Diferansiyel testleri çalıştırarak gizli test vektörlerinde %90+ tam N eşleşmesini doğrulamak.

KURALLAR:
1. Temiz oda ilkesi: Kaynak kodda hiçbir G*Power decompile kırıntısı veya telifli kod parçası bulunamaz.
2. Tek Motor Prensibi: CLI, MCP ve AI Ajanı bağımsız hesaplama yapmaz; tüm matematik tek bir çekirdek
   motor (src/engine/) üzerinden yürütülür.
3. Tolerans: N, n1 ve n2 TAM eşleşmelidir. İkincil çıktılar (actual_power, critical, df, ncp)
   G*Power'ın gösterdiği 4 ondalık basamak hassasiyetinde eşleşmelidir.
```
