# Day 7 — GenAI Interview Drilling + Final Prep

**Time:** 2.5 hours · **Goal:** lock in GenAI/RAG mental model, rehearse the project narrative, cool down.

This is the **day before the interview**. Do not learn new things. Polish.

---

## Schedule

| Block | Time | Activity |
|---|---|---|
| A | 1h | Drill Sections 4-6 of [interview-prep.md](interview-prep.md) — FastAPI, RAG, LangChain/LangGraph |
| B | 1h | Rehearse the 5-beat project narrative + likely follow-ups |
| C | 30 min | Cool-down: re-read Quick Reference blocks, sleep early |

---

## Block A — GenAI drill (1h)

### Coverage
- Section 4 — FastAPI (8 Qs × ~3 min) = 24 min
- Section 5 — RAG concepts (15 Qs × ~3 min) = 45 min — **this is the heart of the interview**
- Section 6 — LangChain/LangGraph specifics (8 Qs × ~3 min) = 24 min — overflow into B if needed

### Drill technique
Same as Day 6: cover answer → speak aloud in 30-60 sec → reveal → star if shaky.

**Pay special attention to:**
- 5.1 What is RAG?
- 5.4 Chunking strategies
- 5.10 Hybrid retrieval
- 5.11 Reranking
- 5.13 Reducing hallucination
- 5.14 Eval — RAG triad
- 6.1 LCEL
- 6.4 LangGraph vs LCEL

If any of these are 🟡 or ❌, re-read the relevant section of day-04 / day-05.

---

## Block B — Project narrative rehearsal (1h)

### The 5-beat narrative

Open [interview-prep.md](interview-prep.md) Section 7.1 and read the 5 beats aloud. Then close it and try from memory.

**Practice loop (15 min × ~4 rounds):**

1. Speak the full 5-beat narrative. Time yourself.
2. **Target: 75-100 seconds.** If you go over 2 minutes you're rambling.
3. Note what felt awkward — usually the trade-off section. Rewrite that beat in your own words.
4. Try again.

By round 4 it should feel natural — not memorized, but structured.

### Drill the follow-ups (Section 7.2)
For each:
1. Read the question.
2. Answer in your own words, 30 seconds.
3. Check the model answer.

The interviewer will ask 2-3 of these on average — make sure you have a take.

### Practice with a real demo (15 min)
- Open the live Render URL in your browser. Hit it once to warm up (cold start ~1 min on free tier).
- Open `/docs` (Swagger UI) — make sure it loads.
- Run a real query via the Swagger UI. Note: how long does it take? What do the sources look like?
- Open your GitHub repo. Browse it as if you'd never seen it. Is the README clear? Does the architecture diagram render? Are there typos?

Fix anything obviously broken **today** — not on interview day.

---

## Block C — Cool down (30 min)

### Re-read all Quick Reference blocks
- [day-01](day-01-python-core.md) Quick Reference (5 min)
- [day-02](day-02-python-intermediate.md) Quick Reference (5 min)
- [day-03](day-03-python-advanced-fastapi-intro.md) Quick Reference (5 min)
- [day-04](day-04-fastapi-rag-build.md) Quick Reference (5 min)
- [day-05](day-05-rag-agent-deploy.md) Quick Reference (5 min)
- [project-docsgpt-spec.md](project-docsgpt-spec.md) Quick Reference (5 min)

These are the only notes you need on interview day.

### Final checklist

- [ ] Live URL works (Render not down)
- [ ] GitHub repo is public, README renders, architecture diagram visible
- [ ] You can answer Section 7.1 narrative in <100 seconds
- [ ] You have 3 follow-up questions of your own ready (Section 7.4)
- [ ] You know your salary range + a one-sentence justification
- [ ] Tomorrow's outfit / camera / mic / quiet room sorted

### Sleep early
Cognitive performance is more sensitive to sleep than to one extra hour of cramming. Stop at the 2.5 hour mark, eat, sleep 8 hours.

---

## Interview-day morning (NOT during the 2.5h block — for tomorrow)

**60 minutes before:**
- Warm up the Render URL with a query (don't get caught by cold start)
- Open Swagger UI tab
- Open your GitHub repo
- Open this folder; have [interview-prep.md](interview-prep.md) Section 7 visible

**30 minutes before:**
- Skim every Quick Reference block one more time (15 min total)
- 10 deep breaths. Hydrate.
- Re-read the 5-beat narrative once.

**5 minutes before:**
- Stop reading. Close tabs except: the meeting link, Swagger, GitHub.
- Smile. You've done the work. They wouldn't be interviewing you if they didn't already think you might be a fit.

---

## If something goes wrong on the day

**"I'm sorry, can you repeat that?"** — totally fine. They asked the question once for the answer, not once-only.

**"That's a great question — let me think for 10 seconds."** — better than rushing into a wrong answer. Use the time.

**"I haven't worked with X specifically, but here's how I'd approach it..."** — honest + shows reasoning. Never bluff a library or tool you haven't touched.

**On a coding question:** *talk through your approach before typing*. Even if it's wrong, it shows engineering thought. Many candidates lose points for silent typing.

**If they ask something you genuinely don't know:** "I don't know off the top of my head, but I'd find out by [reading X / running Y / asking the team]." Honest > made-up.

---

You've built a real, working RAG service in a week while holding down a full-time job. You're ready.
