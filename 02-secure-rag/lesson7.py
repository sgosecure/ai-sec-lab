# Lesson 7: Access control, colored library cards
import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
CUTOFF = 0.30

# Each card now has a security label (all fictional data)
cards = [
    {"role": "public",  "text": "Passwords must be at least 14 characters. Change them every 90 days."},
    {"role": "public",  "text": "A VPN is required on public Wi-Fi."},
    {"role": "analyst", "text": "Incident 2026-014: phishing attack hit the finance team. Attacker IP 203.0.113.50. Investigation ongoing."},
    {"role": "admin",   "text": "Emergency admin account is bg-admin. Its credentials are stored in Safe B in the server room."},
]
vectors = np.array(list(model.embed([c["text"] for c in cards])))

LEVEL = {"public": 0, "analyst": 1, "admin": 2}    # higher card opens lower shelves

def allowed(user_role, card):
    return LEVEL[user_role] >= LEVEL[card["role"]]

def closeness(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def search(question, user_role, lock_on=True):
    q = np.array(list(model.embed([question])))[0]
    results = []
    for card, vec in zip(cards, vectors):
        if lock_on and not allowed(user_role, card):   # 🔒 THE LOCK: skip before scoring
            continue
        results.append((closeness(q, vec), card))
    if not results:
        return None
    score, card = max(results, key=lambda r: r[0])
    return (score, card) if score >= CUTOFF else None

def show(question, user_role, lock_on):
    hit = search(question, user_role, lock_on)
    lock = "ON " if lock_on else "OFF"
    if hit:
        score, card = hit
        print(f"[{user_role:7} lock {lock}] ({score:.2f}) [{card['role']}] {card['text']}")
    else:
        print(f"[{user_role:7} lock {lock}] No matching policy found.")

#q = "What is the emergency admin account?"
q = "Was there a phishing attack recently?"
print("Q:", q)
# show(q, "public", lock_on=False)   # ❌ leak
# show(q, "public", lock_on=True)    # ✅ blocked
# show(q, "admin",  lock_on=True)    # ✅ admin allowed

show(q, "public", lock_on=True)   # ❌ leak
show(q, "analyst", lock_on=True)    # ✅ blocked
show(q, "public",  lock_on=False)    # ✅ admin allowed