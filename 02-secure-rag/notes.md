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

# Interview : Q & A

A, corrected: the page is stapled to the question, and together they make the prompt.



page + question  →  prompt  →  Claude  →  response
     (A)                         (G)

The prompt goes into Claude and the response comes out. A happens before Claude, so the response doesn’t exist yet.



“R is when search() finds the best page. A is when I build the prompt by stapling the page to the question. G is when Claude writes the answer from that prompt.”

Lesson 3 Key ideas

# What you’ve learned so far
Lesson	Key idea
1	RAG means your code finds a page and Claude answers from it
2	Word matching misses plurals and synonyms, and search always returns something
3	R → A → G connected, with two safety layers against made-up answers

Lesson 5

# Embeddings match meaning

# Chunking, interview version

“Chunking splits documents into pieces that each hold one complete idea, so each piece gets a precise embedding and only the relevant piece is sent to the model.”

“A good chunk is focused: it holds one complete idea, so its embedding is precise and Claude gets everything it needs and nothing extra.”

# Interview question

How do you stop RAG from leaking confidential data?

# Lesson 7

Now that you’ve read both, answer in your own words, one sentence each:

# Questions

Why filter in code instead of telling Claude “don’t reveal it”?
Where must the role come from, and what happens if it comes from the question?

# Answer

“I enforce access control in the retrieval code, before search, so restricted chunks never reach the model. Prompt instructions can be bypassed; code can’t.”
“The user’s role comes from authentication, never from the prompt. Otherwise anyone can claim to be an admin and escalate privileges.”

# MCP Server 

Question

what MCP is

“MCP is a standard plug for AI tools. I write tools once in a separate server, and any MCP app (Claude Desktop, Claude Code) can use them, instead of rebuilding them inside each app.”

# (base) [3.12.12] ~/Documents/code/ai-engineer/ai-sec-lab % echo "$PWD/.venv/bin/python"
# /Users/sgo/Documents/code/ai-engineer/ai-sec-lab/.venv/bin/python
# (base) [3.12.12] ~/Documents/code/ai-engineer/ai-sec-lab % echo "$PWD/03-mcp-server/server.py"
# /Users/sgo/Documents/code/ai-engineer/ai-sec-lab/03-mcp-server/server.py

Interview version:

“I built an MCP server and connected it to Claude Desktop. The model decides when to call the tool from its description, and the tool provides data the model can’t know, like internal service names.”


“I built an MCP server that reads authentication logs, so Claude can answer questions like ‘which IP has the most failed logins?’ Tool design matters: the model can only reason over what the tool returns.”

“MCP tools are an attack surface: an attacker who can influence the model can control tool arguments. I validate every argument in the tool itself with an allowlist. For example, my log-reading tool only opens approved files, which blocks path traversal.”

