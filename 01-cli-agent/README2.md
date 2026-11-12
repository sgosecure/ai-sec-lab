## The big idea: a smart helper who can't look things up

Imagine Claude is a **very smart student sitting in a room with no windows and no phone**. It knows a lot, but it can't see today's weather or look up the latest security bugs.

So you give it a **list of helpers waiting outside the door**:
- 🌤️ **Weather helper**: "Give me a city, I'll tell you the weather."
- 🐛 **CVE helper**: "Give me a bug ID, I'll look it up in the government's bug database."

The student can't go outside, but it can **slip a note under the door** saying "Weather helper, please check Denver." Someone outside runs to the helper, gets the answer, and slips it back under the door. Then the student answers you.

- **`agent.py`** is the **messenger** who carries notes back and forth.
- **`tools.py`** is **the helpers** who do the actual looking-up.

---

## The story of one question

You type: **"Is CVE-2021-44228 critical?"**

```
YOU ──► agent.py ──► Claude: "Here's the question, and here are the helpers you can use."
                     Claude: "I need help! Note: lookup_cve('CVE-2021-44228')"
         agent.py ──► tools.py: "Run lookup_cve please"
                     tools.py ──► NVD website ──► "CVSS 10.0, CRITICAL, Log4j..."
         agent.py ──► Claude: "Here's what the helper found."
                     Claude: "Yes, it's critical, 10.0. It's the Log4Shell bug..."
YOU ◄── agent.py
```

Claude never touches the internet. **Your code does**, and only for the helpers you allowed.

---

## `tools.py`, piece by piece

| Code part | Grade-school version |
|---|---|
| `TOOL_SCHEMAS` | The **menu card** you hand Claude: "Here are the helpers, here's what each does, here's what to tell them." Claude reads this to know what it can ask for. |
| `get_weather(city)` | Weather helper. Step 1: ask a map website "where is Denver?" (gets latitude/longitude). Step 2: ask a weather website "what's the weather at that spot?" |
| `lookup_cve(cve_id)` | Bug helper. Asks the NIST website about one bug and brings back its score and description. |
| `CVE_PATTERN` | A **bouncer** at the door. Checks that a bug ID looks like `CVE-2021-44228`. If someone sends garbage like `"; DROP TABLE"`, it's turned away. |
| `@_retry` | **"Try again if the phone line is busy."** If the website doesn't answer, it waits a second and tries up to 3 times. |
| `REGISTRY` | The **official list of helpers**. If Claude asks for a helper not on this list, the answer is "no such helper." |
| `run_tool(name, args)` | The **front desk**. Takes Claude's note, finds the right helper, runs it, and if something breaks, writes "error: ..." instead of crashing the whole program. |

---

## `agent.py`, piece by piece

| Code part | Grade-school version |
|---|---|
| `load_dotenv()` | Opens your secret `.env` file to get your **API key**, your password for talking to Claude. |
| `logging...agent.log` | A **diary**. Writes down every note passed, so you can read later what happened. |
| `SYSTEM` | **Rules for the student**: "Be short. Use helpers for weather and bugs. Don't make up bug info." |
| `MAX_TOOL_ROUNDS = 5` | **"You can only send 5 notes per question."** Stops Claude from asking forever. |
| `main()` | The **front door of the program**. Says hello, waits for you to type, and repeats until you type `quit`. |
| `messages = []` | The **notebook of the whole conversation**. Claude has no memory between calls, so you resend the whole notebook every time. |
| `chat_turn()` | The **messenger loop**, the most important part (below). |

### `chat_turn()`: the messenger loop

```python
for _ in range(MAX_TOOL_ROUNDS):          # up to 5 trips
    resp = client.messages.create(...)     # 1. Send notebook + menu to Claude
    messages.append(assistant reply)       # 2. Write Claude's reply in the notebook

    if resp.stop_reason != "tool_use":     # 3. Did Claude ask for a helper?
        return the text                    #    NO → that's the final answer, done!

    for block in resp.content:             # 4. YES → for each helper note...
        out = run_tool(name, input)        #    run the helper
        results.append(tool_result)        #    write down the answer
    messages.append(results)               # 5. Put answers in the notebook, go back to step 1
```

The key word is **`stop_reason`**. It's Claude saying either:
- `"tool_use"`: "I need a helper, hold on."
- `"end_turn"`: "I'm done, here's my answer."

---

## Try it in the debugger

Set **one breakpoint** on `if resp.stop_reason != "tool_use":` and press F5. Ask about CVE-2021-44228. You'll stop there **twice**:
1. **1st stop:** hover over `resp.stop_reason` and it says `tool_use`. Claude is asking for help.
2. **2nd stop:** it says `end_turn`. Claude has the answer.

Watching that happen once makes the whole thing click. Ask me about any line that's still fuzzy.