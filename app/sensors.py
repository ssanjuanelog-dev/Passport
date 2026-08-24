import random, time
KIND_CONFIG = {
    "temperature": {"min": 2.0, "max": 8.0, "unit": "\u00b0C", "label": "Temperatura"},
    "humidity": {"min": 30, "max": 60, "unit": "%", "label": "Humedad"},
    "vibration": {"max": 10.0, "unit": "mm/s", "label": "Vibraci\u00f3n", "fail_threshold": 10.0},
    "air": {"max": 35, "unit": "\u00b5g/m\u00b3", "label": "Aire (PM2.5)"},
}
class Sensor:
    def __init__(self, sensor_id, kind, location, base, noise):
        self.sensor_id, self.kind, self.location = sensor_id, kind, location
        self.base, self.noise, self.start = base, noise, time.time()
    def read(self):
        t = time.time()
        if self.kind == "vibration": value = self.base + (t - self.start)*0.002 + random.uniform(-self.noise, self.noise)
        elif self.kind == "temperature":
            value = self.base + random.uniform(-self.noise, self.noise)
            if random.random() < 0.05: value += random.uniform(4, 8)
        else: value = self.base + random.uniform(-self.noise, self.noise)
        return {"sensor_id": self.sensor_id, "kind": self.kind, "location": self.location, "value": round(value, 2), "timestamp": t}
class GPSSensor:
    def __init__(self, sensor_id, location, lat, lon):
        self.sensor_id, self.location, self.lat, self.lon = sensor_id, location, lat, lon
    def read(self):
        return {"sensor_id": self.sensor_id, "kind": "gps", "location": self.location, "lat": round(self.lat + random.uniform(-0.0005, 0.0005), 6), "lon": round(self.lon + random.uniform(-0.0005, 0.0005), 6), "timestamp": time.time()}
def build_sensors():
    return [Sensor("SNS-001", "temperature", "Nevera Vacunas PAI", 5.0, 0.8), Sensor("SNS-002", "humidity", "Cuarto Fr\u00edo Farmacia", 45, 4), Sensor("SNS-003", "vibration", "Compresor / Planta", 3.0, 0.4), Sensor("SNS-004", "air", "Quir\u00f3fano / UCI", 20, 4), GPSSensor("GPS-001", "Ambulancia / Ruta Vacunas", 4.6097, -74.0817)]
