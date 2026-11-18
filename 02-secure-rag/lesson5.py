import numpy as np
import anthropic
from fastembed import TextEmbedding
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic()
model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")

pages = [
    "Passwords must be 14 characters and changed every 90 days.",
    "Laptops must use full-disk encryption.",
    "Report phishing emails to the security team.",
    "VPN is required when working from public Wi-Fi.",
    "USB drives are not allowed on company laptops.",
]
page_vectors = np.array(list(model.embed(pages)))   # put pages on the map once
CUTOFF = 0.30                                        # from Lesson 4

def closeness(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def search(question):                                # R: now by MEANING
    q = np.array(list(model.embed([question])))[0]
    scores = [closeness(q, p) for p in page_vectors]
    best = int(np.argmax(scores))                    # position of highest score
    return scores[best], pages[best]

def ask(question):
    score, page = search(question)
    print(f"\nQ: {question}\n   found ({score:.2f}): {page}")
    if score < CUTOFF:                               # Gatekeeper
        return "No matching policy found."

    prompt = (                                       # A: Augmented
        "Answer using ONLY the policy below. "
        "If it doesn't answer the question, say 'Not in policy.'\n\n"
        f"Policy: {page}\n\nQuestion: {question}"
    )
    reply = client.messages.create(                  # G: Generation
        model="claude-sonnet-5-5", max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    print("   blocks:", [b.type for b in reply.content])
    answer = "".join(b.text for b in reply.content if b.type == "text")
    return answer or "(Claude returned no text)"

for q in ["How long should my login secret be?",
          "What's for lunch today?",
          "Can I use coffee shop internet for work?",
          "Do passwords need special characters?",
          "Can I plug in a thumb drive?"]:
    print("   A:", ask(q))