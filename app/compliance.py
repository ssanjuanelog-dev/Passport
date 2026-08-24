import time
from datetime import datetime
def _status(score): return "CUMPLE" if score >= 90 else "CUMPLE CON OBSERVACIONES" if score >= 70 else "EN RIESGO"
def generate_report(ledger, readings_log, ai):
    ok, msg = ledger.verify(); total = len(readings_log)
    bad = sum(1 for r in readings_log if not r.get("in_range", True))
    rate = round((1 - bad/total)*100, 2) if total else 100.0
    return {"report_id": f"RPT-{int(time.time())}", "generated_at": datetime.utcnow().isoformat() + "Z", "compliance_rate": rate, "regulations": score_regulations(readings_log, ai, ledger), "ai": {"anomalies": len(ai.anomalies), "predicted_failures": len(set(p["sensor_id"] for p in ai.predictions)), "quantified_loss": round(ai.total_loss, 2)}, "evidence": {"ledger_blocks": len(ledger.chain), "integrity_verified": ok, "integrity_message": msg, "merkle_root": ledger.merkle_root()[:16] + "\u2026"}}
def score_regulations(readings_log, ai, ledger):
    total = len(readings_log); bad = sum(1 for r in readings_log if not r.get("in_range", True))
    rate = (1 - bad/total)*100 if total else 100; ok, _ = ledger.verify()
    return {"INVIMA_PAI": {"score": round(rate), "focus": "Cadena de fr\u00edo 2\u20138\u00b0C", "status": _status(rate)}, "ANLA": {"score": round(rate*0.9), "focus": "Monitoreo ambiental continuo", "status": _status(rate*0.9)}, "EUDR": {"score": round(min(100, rate+5)) if ok else 50, "focus": "Trazabilidad libre de deforestaci\u00f3n", "status": _status(min(100, rate+5)) if ok else "EN RIESGO"}}
