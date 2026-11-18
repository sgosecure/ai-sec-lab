#1

What happened for each of the 3 questions


Q1.

Q: Do I need VPN on public Wi-Fi?
   found (score 4): VPN is required when working from public Wi-Fi.
   A: Yes. The policy says a VPN is required when working from public Wi-Fi.
   
 Q2:
 
 Q: How long should my login secret be?
   found (score 0): VPN is required when working from public Wi-Fi.
   A: No matching policy found.
   
Q3:

Q: Do passwords need special characters?
   found (score 2): Passwords must be 14 characters and changed every 90 days.
   


#2

Which two lines of code stop Claude from making up answers? (One stops it before calling Claude, one inside the prompt.)

prompt = (                                         # A: Augmented
        "Answer using ONLY the policy below. "
        "If it doesn't answer the question, say 'Not in policy.'\n\n"
        f"Policy: {page}\n\nQuestion: {question}"
    )
    
#3

What does RAG look like in your code, step by step?

R = retrival , code retrives information from the pages =[] list
A = I couldn't find the augentation part
G = when it responds with No matching policy if it cannot find the answer, I answers when it finds answer in the matching pages.

---

Interview : Q & A

A, corrected: the page is stapled to the question, and together they make the prompt.



page + question  →  prompt  →  Claude  →  response
     (A)                         (G)

The prompt goes into Claude and the response comes out. A happens before Claude, so the response doesn’t exist yet.



“R is when search() finds the best page. A is when I build the prompt by stapling the page to the question. G is when Claude writes the answer from that prompt.”

Lesson 3 Key ideas

What you’ve learned so far
Lesson	Key idea
1	RAG means your code finds a page and Claude answers from it
2	Word matching misses plurals and synonyms, and search always returns something
3	R → A → G connected, with two safety layers against made-up answers

Lesson 5

Embeddings match meaning
