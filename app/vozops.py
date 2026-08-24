import time
COMMANDS = {"despachado": {"action": "DISPATCHED", "desc": "Activo despachado / en ruta"}, "terminado": {"action": "COMPLETED", "desc": "Proceso completado"}, "recibido": {"action": "RECEIVED", "desc": "Activo recibido / custodia transferida"}, "apagado": {"action": "SHUTDOWN", "desc": "Equipo apagado / fuera de servicio"}}
def process_voice(text):
    text = text.lower().strip()
    for cmd, meta in COMMANDS.items():
        if cmd in text: return {"recognized": cmd, "action": meta["action"], "desc": meta["desc"], "confidence": 0.95, "timestamp": time.time()}
    return {"recognized": None, "error": "Comando no reconocido", "confidence": 0.0}
