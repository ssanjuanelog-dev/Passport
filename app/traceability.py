import time
class CustodyChain:
    def __init__(self): self.events = []
    def transfer(self, asset, from_p, to_p):
        ev = {"asset": asset, "from": from_p, "to": to_p, "timestamp": time.time()}; self.events.append(ev); return ev
    def to_list(self): return self.events
def seed_custody(chain):
    chain.transfer("Lote Vacunas #A-102", "Laboratorio", "Transportador")
    chain.transfer("Lote Vacunas #A-102", "Transportador", "Hospital")
