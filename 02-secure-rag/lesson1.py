# Lesson 1: What is RAG?

import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

# Our "company files" (just 3 sentences for now)
pages = [
    "Passwords must be 16 characters and changed every 90 days.",
    "Laptops must use full-disk encryption.",
    "Report phishing emails to security@orcasecure.net.",
]

question = "How long must passwords be?"

# Step 1: FIND the page (cheap trick: does it share a word?)
found = [p for p in pages if "laptop" in p.lower()]

# Step 2: STAPLE it to the question
prompt = f"Use only this page to answer:\n{found}\n\nQuestion: {question}"

# Step 3: ANSWER
reply = client.messages.create(
    model="claude-sonnet-5-5", max_tokens=200,
    messages=[{"role": "user", "content": prompt}],
)
print("Page found:", found)
print("Answer:", reply.content[0].text)