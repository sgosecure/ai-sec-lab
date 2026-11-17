import numpy as np
from fastembed import TextEmbedding

model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")  # same model, no PyTorch

pages = [
    "Passwords must be 14 characters and changed every 90 days.",
    "Laptops must use full-disk encryption.",
    "Report phishing emails to the security team.",
    "VPN is required when working from public Wi-Fi.",
]

# Put every page on the map (done once)
page_vectors = np.array(list(model.embed(pages)))
print("Each page becomes", len(page_vectors[0]), "numbers")
print("First 5 numbers of page 1:", page_vectors[0][:5])

def closeness(a, b):
    """Cosine similarity: 1 = same meaning, 0 = unrelated."""
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

def search(question):
    q_vector = np.array(list(model.embed([question])))[0]   # put question on the map
    scores = [closeness(q_vector, p) for p in page_vectors]
    return sorted(zip(scores, pages), reverse=True)

#question = "How long should my login secret be?"
question = "What's for lunch today?"
print("\nQ:", question)
for score, page in search(question):
    print(f"{score:.2f} | {page}")