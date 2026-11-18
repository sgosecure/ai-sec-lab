import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")

policy = """## Passwords
Passwords must be at least 14 characters. Change them every 90 days. Never reuse your last 5 passwords.

## Devices
Laptops must use full-disk encryption. USB drives are not allowed on company laptops. Lock your screen when you step away.

## Email
Report phishing emails to the security team. Never open attachments from unknown senders.

## Remote work
A VPN is required on public Wi-Fi. Do not work from shared computers."""

# Three ways to cut the document into cards
def no_cut(text):
    return [text]

def cut_by_size(text, size=300):
    return [text[i:i + size] for i in range(0, len(text), size)]

def cut_by_section(text):
    return [c.strip() for c in text.split("\n\n") if c.strip()]

def closeness(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def best_card(question, cards):
    q = np.array(list(model.embed([question])))[0]
    vectors = np.array(list(model.embed(cards)))
    scores = [closeness(q, v) for v in vectors]
    i = int(np.argmax(scores))
    return scores[i], cards[i]

#question = "Can I plug in a thumb drive?"
question = "Can I reuse an old password?"
print("Q:", question)
for name, cutter in [("NO CUT", no_cut), ("BY SIZE", cut_by_size), ("BY SECTION", cut_by_section)]:
    cards = cutter(policy)
    score, card = best_card(question, cards)
    print(f"\n{name}: {len(cards)} cards | best score {score:.2f}")
    print("   card:", card.replace("\n", " "))