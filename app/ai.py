from collections import deque
class AIBrain:
    def __init__(self):
        self.baselines = {}; self.vibration_history = {}; self.windows = {}; self.risk = {}
        self.anomalies = []; self.predictions = []; self.total_loss = 0.0
    def update_baseline(self, sid, value):
        b = self.baselines.setdefault(sid, {"count": 0, "mean": 0.0, "m2": 0.0}); b["count"] += 1
        d = value - b["mean"]; b["mean"] += d / b["count"]; b["m2"] += d * (value - b["mean"])
    def _std(self, sid):
        b = self.baselines.get(sid)
        if not b or b["count"] < 2: return 0.0
        return (b["m2"] / (b["count"]-1)) ** 0.5
    def detect_anomaly(self, sid, value, threshold=3.0, min_samples=20):
        b = self.baselines.get(sid)
        if not b or b["count"] < min_samples: return None
        s = self._std(sid)
        if s == 0: return None
        z = abs(value - b["mean"]) / s
        if z > threshold: return {"sensor_id": sid, "value": value, "z": round(z, 2), "baseline_mean": round(b["mean"], 2)}
        return None
    def predict_maintenance(self, sid, t, value, fail_threshold=10.0):
        hist = self.vibration_history.setdefault(sid, []); hist.append((t, value))
        if len(hist) > 200: hist.pop(0)
        if len(hist) < 10: return None
        n = len(hist); xs = [h[0] for h in hist]; ys = [h[1] for h in hist]
        mx, my = sum(xs)/n, sum(ys)/n
        den = sum((xs[i]-mx)**2 for i in range(n))
        if den == 0: return None
        slope = sum((xs[i]-mx)*(ys[i]-my) for i in range(n)) / den
        if slope <= 0: return None
        intercept = my - slope*mx; secs = (fail_threshold - intercept)/slope - t
        if secs <= 0: return None
        return {"sensor_id": sid, "current": round(value, 2), "threshold": fail_threshold, "days_to_failure": round(secs/86400, 1), "slope": round(slope, 4)}
    def compute_risk(self, sid, in_range, anomaly, pred):
        w = self.windows.setdefault(sid, deque(maxlen=50)); w.append(0 if in_range else 1)
        rate = sum(w)/len(w) if w else 0; score = rate * 60
        if anomaly: score += 25
        if pred and pred.get("days_to_failure", 999) < 30: score += 15
        self.risk[sid] = round(min(100, score), 1); return self.risk[sid]
    def quantify_loss(self, anomaly, unit_value=50.0):
        loss = round(abs(anomaly["value"] - anomaly["baseline_mean"]) * unit_value, 2); self.total_loss += loss; return loss
    def recommendations(self):
        recs = []
        for sid, score in sorted(self.risk.items(), key=lambda x: -x[1]):
            if score >= 70: recs.append({"sensor_id": sid, "priority": "CR\u00cdTICA", "action": "Intervenir de inmediato: revisar equipo y reubicar producto"})
            elif score >= 40: recs.append({"sensor_id": sid, "priority": "ALTA", "action": "Programar mantenimiento preventivo en 24h"})
            elif score >= 20: recs.append({"sensor_id": sid, "priority": "MEDIA", "action": "Monitorear de cerca; aumentar frecuencia de muestreo"})
        return recs[:6]
