#!/usr/bin/env python3
"""
Klinik AI Ajanı (Clinical AI Agent for Power Analysis).
Hekimlerin ve araştırmacıların doğal dildeki (Türkçe) klinik araştırma sorularını anlar,
Sistem 1 sınıflandırıcısı ile test ailesini belirler (güven < 0.75 ise hekime sorar),
parametreleri ayrıştırır ve hesabı MCP aracı üzerinden çekirdek motora yaptırır.

KURAL: Ajan hesabı kendisi YAPMAZ! Hesap daima motordan gelir.
"""

import re
import json
import time
from typing import Dict, Any, Tuple
from pathlib import Path

from src.mcp_server import handle_tool_call

LABELS = [
    "t2-indep",
    "t-paired",
    "anova-oneway",
    "chi2-contingency",
    "multireg-r2",
    "ambiguous",
    "unsupported"
]

class System1Classifier:
    """
    Sistem 1 Hızlı Karar Verici (Test Ailesi Sınıflandırıcısı).
    Klinik soruyu analiz ederek test ailesini ve güven skorunu belirler.
    Hiçbir sayısal N veya güç değeri üretmez.
    """
    def classify(self, text: str) -> Tuple[str, float, str]:
        lower = text.lower()

        # Belirsiz (Ambiguous) durumlar
        if len(lower.strip()) < 15 or "bilmiyorum" in lower or "kararsızım" in lower:
            return "ambiguous", 0.50, "Soru yeterli klinik detay içermiyor."

        # Desteklenmeyen (Unsupported) durumlar
        if "sağkalım" in lower or "survival" in lower or "kaplan-meier" in lower or "cox" in lower:
            return "unsupported", 0.95, "Sağkalım (Survival) analizleri t-testi kapsamı dışındadır."
        if "wilcoxon" in lower or "mann-whitney" in lower:
            return "unsupported", 0.90, "Non-parametrik testler henüz desteklenmemektedir."

        # ANOVA (3 veya daha fazla grup)
        if any(w in lower for w in ["anova", "3 grup", "üç grup", "3 kol", "üç kol", "üç tedavi", "dört grup"]):
            return "anova-oneway", 0.92, "Üç veya daha fazla bağımsız tedavi kolunun karşılaştırılması."

        # Eşleştirilmiş t-testi (Önce / Sonra - Paired)
        if any(w in lower for w in ["önce ve sonra", "öncesi ve sonrası", "eşleştirilmiş", "paired", "aynı hastaların", "tedavi öncesi"]):
            return "t-paired", 0.94, "Aynı deneklerin tedavi öncesi ve sonrası ölçümlerinin karşılaştırılması."

        # Ki-Kare (Oranlar / Olumsallık)
        if any(w in lower for w in ["ki-kare", "chi-square", "oran", "oranlar", "olumsallık", "yüzde farkı", "yanıt oranı"]):
            return "chi2-contingency", 0.91, "Kategorik yanıt oranlarının karşılaştırılması."

        # Çoklu Regresyon (R^2)
        if any(w in lower for w in ["regresyon", "r2", "r-kare", "risk faktörleri", "bağımsız değişken"]):
            return "multireg-r2", 0.93, "Çoklu risk faktörlerinin regresyon modeli."

        # İki Bağımsız Grup t-Testi (t2-indep)
        indep_keywords = [
            "iki grup", "2 grup", "ilaç ve plasebo", "plasebo", "kontrol grubu",
            "bağımsız", "iki hasta grubu", "iki kol", "fark var mı", "ortalamaları karşılaştır"
        ]
        if any(w in lower for w in indep_keywords):
            return "t2-indep", 0.95, "İki bağımsız grup ortalaması (örneğin ilaç vs plasebo) karşılaştırması."

        # Varsayılan iki grup t-testi şüphesi ancak düşük güven
        if "ortalama" in lower or "fark" in lower:
            return "t2-indep", 0.70, "Ortalama farkından bahsediliyor ancak grup bağımsızlığı tam açık değil."

        return "ambiguous", 0.40, "Klinik tasarım sınıflandırılamadı."

class ClinicalPowerAgent:
    """
    Klinik Güç Analizi ve Örneklem Boyutu AI Ajanı.
    """
    def __init__(self):
        self.classifier = System1Classifier()
        self.call_logs = []

    def extract_parameters(self, text: str) -> Dict[str, Any]:
        """Metinden klinik parametreleri (etki büyüklüğü, alfa, güç, kuyruk, oran) çıkarır."""
        lower = text.lower()
        
        # Etki büyüklüğü (d)
        d = 0.5  # varsayılan orta etki
        d_match = re.search(r'(?:etki\s*büyüklüğü|etki\s*boyutu|cohen[\'s]*\s*d|d\s*=|d\s*:)\s*([0-9]+(?:[.,][0-9]+)?)', lower)
        if d_match:
            d = float(d_match.group(1).replace(',', '.'))
        elif "küçük etki" in lower:
            d = 0.2
        elif "büyük etki" in lower:
            d = 0.8
        elif "orta etki" in lower:
            d = 0.5

        # Alfa (Anlamlılık düzeyi)
        alpha = 0.05  # klinik tıp altın standardı
        alpha_match = re.search(r'(?:alfa|alpha|anlamlılık|tip\s*1\s*hata)\s*(?:düzeyi)?\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)', lower)
        if alpha_match:
            alpha = float(alpha_match.group(1).replace(',', '.'))
            if alpha > 1.0:  # %5 girildiyse
                alpha /= 100.0

        # Güç (Power)
        power = 0.80  # standart klinik güç
        if "95" in lower and ("güç" in lower or "power" in lower):
            power = 0.95
        elif "90" in lower and ("güç" in lower or "power" in lower):
            power = 0.90
        elif "80" in lower and ("güç" in lower or "power" in lower):
            power = 0.80
        else:
            power_match = re.search(r'(?:güç|power|1-beta)\s*[:=]?\s*([0-9]+(?:[.,][0-9]+)?)', lower)
            if power_match:
                val = float(power_match.group(1).replace(',', '.'))
                if val > 1.0:
                    val /= 100.0
                power = val

        # Kuyruk (Tails)
        tails = 2
        if "tek yönlü" in lower or "one-tailed" in lower or "üstünlük" in lower:
            tails = 1

        # Tahsis Oranı (Ratio)
        ratio = 1.0
        if "1:2" in lower or "iki katı plasebo" in lower:
            ratio = 2.0
        elif "2:1" in lower:
            ratio = 0.5

        return {
            "d": d,
            "alpha": alpha,
            "power": power,
            "tails": tails,
            "ratio": ratio
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        """Hekimin klinik sorusunu işler ve yanıt döner."""
        start_time = time.time()
        label, confidence, rationale = self.classifier.classify(query)

        log_entry = {
            "query": query,
            "classification": {
                "label": label,
                "confidence": confidence,
                "rationale": rationale
            },
            "timestamp": time.time()
        }

        # Güven < 0.75 veya belirsiz/desteklenmeyen ise araştırmacıya sor
        if confidence < 0.75 or label in ("ambiguous", "unsupported"):
            elapsed_ms = (time.time() - start_time) * 1000.0
            log_entry["status"] = "NEEDS_CLARIFICATION"
            log_entry["elapsed_ms"] = elapsed_ms
            self.call_logs.append(log_entry)
            
            if label == "unsupported":
                msg = f"Sayın Araştırmacı, sorunuz '{label}' ({rationale}) olarak tespit edildi. Sistemimiz şu anda t2-indep test ailesini tam doğrulanmış olarak desteklemektedir."
            else:
                msg = f"Sayın Araştırmacı, klinik tasarımınız tam anlaşılamadı (Güven Skoru: {confidence:.2f}). Lütfen grup sayısını ve bağımsızlık durumunu netleştiriniz."
            
            return {
                "status": "clarification_needed",
                "label": label,
                "confidence": confidence,
                "message": msg
            }

        if label != "t2-indep":
            elapsed_ms = (time.time() - start_time) * 1000.0
            log_entry["status"] = "DIFFERENT_FAMILY"
            log_entry["elapsed_ms"] = elapsed_ms
            self.call_logs.append(log_entry)
            return {
                "status": "different_family",
                "label": label,
                "confidence": confidence,
                "message": f"Bu araştırma '{label}' test ailesini gerektirmektedir. ({rationale})"
            }

        # Parametreleri çıkar
        params = self.extract_parameters(query)

        # MCP Aracı Çağrısı (Hesap motora yaptırılır!)
        mcp_tool_name = "calculate_sample_size_t2_indep"
        mcp_args = {
            "d": params["d"],
            "alpha": params["alpha"],
            "power": params["power"],
            "tails": params["tails"],
            "ratio": params["ratio"]
        }

        mcp_result = handle_tool_call(mcp_tool_name, mcp_args)
        elapsed_ms = (time.time() - start_time) * 1000.0

        log_entry["status"] = "SUCCESS"
        log_entry["mcp_tool"] = mcp_tool_name
        log_entry["mcp_arguments"] = mcp_args
        log_entry["mcp_result"] = mcp_result
        log_entry["elapsed_ms"] = elapsed_ms
        self.call_logs.append(log_entry)

        # Hekim dilinde açıklayıcı klinik yanıt oluştur
        doctor_reply = (
            f"Klinik Çalışma Tasarımı Örneklem Raporu:\n"
            f"- Test Türü: İki Bağımsız Örneklem t-Testi (t2-indep)\n"
            f"- Hipotez Yönü: {'Çift Yönlü (Two-tailed)' if params['tails'] == 2 else 'Tek Yönlü (One-tailed)'}\n"
            f"- Belirlenen Etki Büyüklüğü (d): {params['d']}\n"
            f"- İstatistiksel Anlamlılık (α): {params['alpha']}\n"
            f"- Hedef Güç (1-β): {params['power'] * 100:.0f}%\n"
            f"--------------------------------------------------\n"
            f"Gereken Örneklem Büyüklüğü:\n"
            f"• Tedavi / Grup 1 (n1): {mcp_result['n1']} hasta\n"
            f"• Kontrol / Grup 2 (n2): {mcp_result['n2']} hasta\n"
            f"• TOPLAM HASTA (N): {mcp_result['n_total']} hasta\n"
            f"--------------------------------------------------\n"
            f"Hesaplanan Gerçek Güç (Actual Power): {mcp_result['actual_power'] * 100:.2f}%\n"
            f"Kritik t Değeri: {mcp_result['critical']} (Serbestlik Derecesi df: {mcp_result['df']})\n"
            f"Noncentrality Parametresi (δ): {mcp_result['ncp']}"
        )

        return {
            "status": "success",
            "label": label,
            "confidence": confidence,
            "result": mcp_result,
            "clinical_response": doctor_reply,
            "execution_time_ms": round(elapsed_ms, 2)
        }

if __name__ == "__main__":
    agent = ClinicalPowerAgent()
    sample_query = "Yeni geliştirdiğimiz antihipertansif ilacı plasebo grubuyla karşılaştıracağız. Orta düzeyde bir etki (d=0.5) bekliyoruz, %95 güç ve 0.05 anlamlılık için kaçar hasta almalıyız?"
    response = agent.process_query(sample_query)
    print("--- AJAN YANITI ---")
    print(response["clinical_response"])
