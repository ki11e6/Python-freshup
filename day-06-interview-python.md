# Day 6 — Python Interview Drilling

**Time:** 2.5 hours · **Goal:** answer any Python question (basic to advanced) without hesitation.

---

## Schedule

| Block | Time | Activity |
|---|---|---|
| A | 1.5h | Drill Section 1-3 of [interview-prep.md](interview-prep.md) — Python Qs |
| B | 1h | 2-3 Python LeetCode easy problems |

---

## Block A — Drill (1.5h)

### How to drill effectively

1. **Cover the answer** (or open another tab). Read just the question.
2. **Answer aloud** in 30-60 seconds. Speak it — don't think it. Mumbling is fine.
3. **Reveal the model answer.** Compare.
4. **If wrong or shaky:** mark with a star. Re-do at the end.
5. After full pass: re-do starred items.

### Target coverage in 90 minutes
- Section 1 (10 Qs × ~3 min each) = 30 min — basics
- Section 2 (10 Qs × ~3 min each) = 30 min — intermediate
- Section 3 (8 Qs × ~3 min each) = 25 min — advanced
- Buffer = 5 min for starred re-do

### Self-grading rubric

For each question, rate yourself:

- ✅ **Sharp** — answered with structure + an example + a TS analogy where relevant
- 🟡 **Vague** — got the right answer but rambled or missed key detail
- ❌ **Blank** — didn't have the answer

After the pass:
- All ✅ — move to Block B
- Any ❌ — re-read that day's source file (day-01 / day-02 / day-03) for 5 min then retry
- 🟡 — fine for now, will tighten on interview-day skim

### Bonus drills (if time)

**Code-on-whiteboard style — write these from memory, no editor autocomplete:**

```python
# 1. A decorator that times function calls
def timer(fn): ...

# 2. A generator producing Fibonacci numbers
def fib(): ...

# 3. A context manager (both class + generator style) that prints "enter" / "exit"

# 4. A Pydantic model for a User with email, age (0-150), tags (list[str]),
#    and a field_validator that strips whitespace from email
```

If you can write these without lookup, you're ready.

---

## Block B — Coding warmup (1h)

### Why LeetCode?
Some Python+GenAI screens include a 20-30 min coding question. They're usually easy/medium — string/list manipulation, simple data structures. Not graph algorithms.

### Pick 2-3 from this list

**String / list manipulation (most likely):**
- LC 1: Two Sum — `dict` lookup pattern
- LC 49: Group Anagrams — `dict` of `tuple`-keyed groups
- LC 347: Top K Frequent Elements — `Counter` + `heapq`
- LC 5: Longest Palindromic Substring — two-pointer expansion
- LC 271: Encode/Decode Strings — design-flavor

**Dict / Counter / set patterns:**
- LC 387: First Unique Character
- LC 242: Valid Anagram
- LC 128: Longest Consecutive Sequence

**Generator / iterator pattern (rarer but possible):**
- Write `chunked(iterable, n)` — split any iterable into lists of size n
- Write a generator that yields running averages

### Pythonic idioms to use in answers

```python
# Use Counter for frequency
from collections import Counter
counts = Counter("mississippi")   # {'i': 4, 's': 4, ...}

# Use defaultdict to avoid checking key
from collections import defaultdict
groups = defaultdict(list)
for word in words:
    groups[tuple(sorted(word))].append(word)

# Use heapq for top-k
import heapq
top_k = heapq.nlargest(k, counter.items(), key=lambda kv: kv[1])

# Use enumerate for index+value
for i, c in enumerate(s):
    ...

# Use zip for parallel iteration
for a, b in zip(xs, ys):
    ...

# Unpack in one line
*head, last = [1, 2, 3, 4]   # head=[1,2,3], last=4

# Slicing is your friend
s[::-1]   # reverse
s[1:-1]   # drop first and last

# Walrus operator (3.8+) when you need both the test and the value
if (m := re.match(p, s)):
    return m.group(1)
```

**Show these idioms in your code** — interviewer can tell native Python from Python-as-second-language.

### Where to practice

- leetcode.com — premium not required for easy/medium
- Or just write them in your editor; LeetCode's UI is fine but not necessary.

---

## End-of-Day-6 self-check

- [ ] You can answer every question in Sections 1-3 of [interview-prep.md](interview-prep.md) in under a minute
- [ ] You wrote at least 2 LeetCode problems start-to-finish
- [ ] You used 3+ Pythonic idioms in those solutions
- [ ] You have NO ❌ items left from the drill

---

## Stretch

If you're done early:
- Read the **What you skipped** sections from days 1-3 — anything that still mystifies you, look up briefly
- Re-skim Day 4 + Day 5 Quick Reference blocks — these come up on Day 7
- Verify your live Render URL is still up. If it's spun down, hit `/health` to warm it up.
