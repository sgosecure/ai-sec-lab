# Lesson 2: Find the right page by matching words

import re

pages = [
    "Passwords must be 14 characters and changed every 90 days.",
    "Laptops must use full-disk encryption.",
    "Report phishing emails to the security team.",
    "VPN is required when working from public Wi-Fi.",
]

# Small words that appear everywhere and don't help matching
STOP = {"how", "must", "be", "the", "a", "is", "what", "should", "my", "to", "do", "i", "when"}

def words(text):
    """Turn a sentence into a set of useful lowercase words."""
    return set(re.findall(r"[a-z]+", text.lower())) - STOP

def search(question):
    q = words(question)
    results = []
    for page in pages:
        score = len(q & words(page))      # & = words in BOTH
        results.append((score, page))
    results.sort(reverse=True)            # highest score first
    return results

question = "How long must passwords be?"


print("Question words:", words(question))
for score, page in search(question):
    print(score, "|", page)
    
best_score, best_page = search(question)[0]
if best_score == 0:
    print("No matching page. Don't ask Claude.")
else:
    print("Best page:", best_page)