import threading, time
from pathlib import Path
from collections import deque
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .ledger import ImmutableLedger
from .identity import DevicePassport
from .sensors import build_sensors, KIND_CONFIG
from .ai import AIBrain
from .compliance import generate_report
from .vozops import process_voice
from .traceability import CustodyChain, seed_custody
app = FastAPI(title="Passport - IoT + Blockchain + AI Protocol")
ledger = ImmutableLedger(); sensors = build_sensors(); ai = AIBrain()
passports = {s.sensor_id: DevicePassport(s.sensor_id, s.kind, s.location) for s in sensors}
custody = CustodyChain(); seed_custody(custody)
history = {s.sensor_id: deque(maxlen=30) for s in sensors if s.kind != "gps"}
readings_log, anomalies, predictions = [], [], []
LOCK = threading.Lock()
def in_range(kind, value):
    cfg = KIND_CONFIG.get(kind)
    if not cfg: return True
    lo, hi = cfg.get("min"), cfg.get("max")
    if lo is not None and value < lo: return False
    if hi is not None and value > hi: return False
    return True
def capture_loop(interval=4):
    while True:
        for s in sensors:
            r = s.read(); passport = passports.get(s.sensor_id)
            with LOCK:
                if s.kind == "gps":
                    ledger.append({"type": "LOCATION", "sensor_id": s.sensor_id, "did": passport.did, "lat": r["lat"], "lon": r["lon"]}); continue
                ok_r = in_range(s.kind, r["value"]); anomaly = ai.detect_anomaly(s.sensor_id, r["value"])
                if anomaly:
                    anomaly["loss"] = ai.quantify_loss(anomaly); anomalies.append(anomaly)
                else: ai.update_baseline(s.sensor_id, r["value"])
                pred = ai.predict_maintenance(s.sensor_id, r["timestamp"], r["value"]) if s.kind == "vibration" else None
                if pred: predictions.append(pred)
                risk = ai.compute_risk(s.sensor_id, ok_r, anomaly, pred)
                history[s.sensor_id].append(r["value"]); readings_log.append({**r, "in_range": ok_r})
                sig = passport.sign(r["value"]) if passport else None
                ledger.append({"type": "READING", "sensor_id": s.sensor_id, "did": passport.did if passport else None, "kind": s.kind, "value": r["value"], "in_range": ok_r, "risk": risk, "signature": sig[:12] if sig else None})
        time.sleep(interval)
@app.on_event("startup")
def startup(): threading.Thread(target=capture_loop, daemon=True).start()
@app.get("/api/readings")
def get_readings():
    latest = {}
    for r in readings_log: latest[r["sensor_id"]] = r
    return {"sensors": [{**r, "risk": ai.risk.get(r["sensor_id"], 0), "history": list(history.get(r["sensor_id"], []))} for r in latest.values()], "config": KIND_CONFIG}
@app.get("/api/ai")
def get_ai():
    with LOCK: return {"anomalies": anomalies[-10:], "predictions": predictions[-5:], "risk": ai.risk, "recommendations": ai.recommendations(), "total_loss": round(ai.total_loss, 2), "anomaly_count": len(anomalies)}
@app.get("/api/compliance")
def compliance():
    with LOCK: return generate_report(ledger, readings_log, ai)
@app.get("/api/passports")
def get_passports(): return {"passports": [p.to_dict() for p in passports.values()]}
@app.get("/api/ledger")
def get_ledger():
    with LOCK: return {"blocks": ledger.to_list()[-15:], "total": len(ledger.chain), "merkle_root": ledger.merkle_root()}
@app.get("/api/ledger/verify")
def verify():
    with LOCK:
        ok, msg = ledger.verify()
        return {"valid": ok, "message": msg, "blocks": len(ledger.chain), "merkle_root": ledger.merkle_root()}
@app.get("/api/custody")
def get_custody(): return {"events": custody.to_list()}
@app.post("/api/vozops")
def vozops(payload: dict):
    result = process_voice(payload.get("text", ""))
    if result.get("recognized"):
        with LOCK: ledger.append({"type": "VOICE", "command": result["action"], "desc": result["desc"], "confidence": result["confidence"]})
    return result
@app.get("/", response_class=HTMLResponse)
def dashboard():
    return (Path(__file__).resolve().parent.parent / "frontend" / "index.html").read_text(encoding="utf-8")
