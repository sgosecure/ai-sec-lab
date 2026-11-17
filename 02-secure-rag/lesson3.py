import re
import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

pages = [
    "Passwords must be 14 characters and changed every 90 days.",
    "Laptops must use full-disk encryption.",
    "Report phishing emails to the security team.",
    "VPN is required when working from public Wi-Fi.",
]
STOP = {"how", "must", "be", "the", "a", "is", "what", "should", "my", "to", "do", "i", "when"}

def words(text):
    return set(re.findall(r"[a-z]+", text.lower())) - STOP

def search(question):                                  # R: Retrieval
    q = words(question)
    results = [(len(q & words(p)), p) for p in pages]
    results.sort(reverse=True)
    return results[0]                                  # best (score, page)

def ask(question):
    score, page = search(question)
    print(f"\nQ: {question}\n   found (score {score}): {page}")
    if score == 0:                                     # Gatekeeper
        return "No matching policy found."

    prompt = (                                         # A: Augmented
        "Answer using ONLY the policy below. "
        "If it doesn't answer the question, say 'Not in policy.'\n\n"
        f"Policy: {page}\n\nQuestion: {question}"
    )
    reply = client.messages.create(                    # G: Generation
        model="claude-sonnet-5-5", max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return reply.content[0].text

# for q in ["How long must passwords be?",
#           "What do I do with phishing emails?",
#           "Do I need VPN on public Wi-Fi?",
#           "How long should my login secret be?",
#           "Do passwords need special characters?"]:
    
for q in ["Do passwords need special characters?"]:
    print("   A:", ask(q))