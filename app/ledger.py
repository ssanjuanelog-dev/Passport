import hashlib, time, json
class MerkleTree:
    @staticmethod
    def root(leaves):
        if not leaves: return ""
        level = [hashlib.sha256(l.encode()).hexdigest() for l in leaves]
        while len(level) > 1:
            if len(level) % 2: level.append(level[-1])
            level = [hashlib.sha256((level[i]+level[i+1]).encode()).hexdigest() for i in range(0, len(level), 2)]
        return level[0]
class Block:
    def __init__(self, index, timestamp, event, prev_hash):
        self.index, self.timestamp, self.event, self.prev_hash = index, timestamp, event, prev_hash
        self.hash = self.compute_hash()
    def compute_hash(self):
        payload = json.dumps({"index": self.index, "timestamp": self.timestamp, "event": self.event, "prev_hash": self.prev_hash}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()
    def to_dict(self):
        return {"index": self.index, "timestamp": self.timestamp, "event": self.event, "prev_hash": self.prev_hash, "hash": self.hash}
class ImmutableLedger:
    def __init__(self): self.chain = [Block(0, time.time(), {"type": "GENESIS"}, "0"*64)]
    def append(self, event):
        prev = self.chain[-1]; b = Block(len(self.chain), time.time(), event, prev.hash); self.chain.append(b); return b
    def verify(self):
        for i, b in enumerate(self.chain):
            if b.hash != b.compute_hash(): return False, f"Bloque {i}: hash alterado"
            if i > 0 and b.prev_hash != self.chain[i-1].hash: return False, f"Bloque {i}: enlace roto"
        return True, "Integridad verificada"
    def merkle_root(self): return MerkleTree.root([b.hash for b in self.chain])
    def to_list(self): return [b.to_dict() for b in self.chain]
