import hashlib, secrets, time
class DevicePassport:
    def __init__(self, device_id, kind, location):
        self.device_id, self.kind, self.location = device_id, kind, location
        self.private_key = secrets.token_hex(32)
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()
        self.did = f"did:protocol:{self.public_key[:16]}"
        self.created = time.time(); self.status = "ACTIVE"
    def sign(self, payload):
        return hashlib.sha256(str(payload).encode() + self.private_key.encode()).hexdigest()
    def to_dict(self):
        return {"device_id": self.device_id, "did": self.did, "public_key": self.public_key[:16] + "\u2026", "kind": self.kind, "location": self.location, "status": self.status}
