import hashlib

def fake_embedding(text: str):
    h = hashlib.sha256(text.encode()).hexdigest()
    return [int(h[i:i+2], 16)/255 for i in range(0, 64, 2)]
