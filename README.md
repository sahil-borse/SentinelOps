# SentinelOps

Compliance checks that cannot be forgotten, judged the same way in every process
area, with the audit trail written as it happens rather than assembled
afterwards.

It does two scheduled things that are easy to confuse and are kept apart
throughout: **audits**, conducted by a PA/InfoSec team, whose output is
findings; and **compliance activities**, owed by a unit, whose output is
evidence. Findings are the tracked object. They stay open until an auditor says
otherwise.

This is a demonstration system built against a written spec ([`CLAUDE.md`](CLAUDE.md)),
on a synthetic corpus, at the scale the spec describes: six support functions
and a handful of project teams, fifteen to eighteen findings open at a time. It
is not a scale story.

**[Full user guide, with screenshots →](docs/USER_GUIDE.md)**

---

## Requirements

- **Python 3.11 or newer** (3.11.9 is what it's developed on)
- Windows, macOS or Linux. No database server, no Docker, no services.

```bash
pip install -e ".[dev,ui]"
```

That installs the package, `pytest` and `streamlit`. The OpenAI SDK is optional
and only needed to run against a real model:

```bash
pip install openai
```

## Run the dashboard

```bash
python -m streamlit run src/sentinelops/ui/app.py
```

It opens on http://localhost:8501, seeds itself on first run, and keeps its
state in `data/demo/sentinelops.db`. **Reset scenario** in the sidebar restores
the exact seeded state, so every demo run starts identically.

> **Restart the server after changing any code.** Streamlit re-executes page
> scripts on each interaction but keeps modules it has already imported, so an
> edit to `view.py`, `shell.py` or `service.py` will not appear until you stop
> and start it. The theme in `.streamlit/config.toml` is read only at startup
> too. An `AttributeError` about a function you just added means a stale server,
> not a bug.

### Moving the clock

The application runs on **simulated business time**, not the wall clock. Every
audit event and notification is stamped with the simulated date. The sidebar
carries:

| Control | What it does |
|---|---|
| **Jump to next event** | Names the next meaningful moment — a reminder falling due, a target date, an escalation, an audit — and advances to it |
| **Run cycle now** | Runs one full cycle on the current date |
| **+1 day / +1 week / +1 month** | Fixed advances, each running the cycles it passes |
| **Reset scenario** | Restores the seeded state exactly |

The corpus spans **January 2026 to June 2027**, with a vantage point of
**15 April 2027**. A freshly reset demo starts in January 2026 where little has
happened yet: recurrence has nothing to link and the trend charts are nearly
empty. **Advance several months before demonstrating** — the portfolio, the
ageing buckets and the recurrence chains only exist once time has passed.

### Roles

The sidebar's **Acting as** is an identity selector, not a login — there is no
authentication anywhere in this system, by design.

| Role | Pages |
|---|---|
| **PA/InfoSec** | Today, Findings, Schedule, Inbox, Portfolio, Recurrence, Audit trail, Walkthrough |
| **Unit owner** | My findings, Finding detail, Inbox — their own unit only, filtered in the query |
| **Management** | Overview, read-only |

An owner's Close and Accept controls are **absent from the page**, not disabled.

There is one unlisted page, `/cost`, reachable only by typing the address. It
shows model spend, which belongs to whoever runs the system rather than to a
compliance team's working screen.

## The other entry points

```bash
python -m sentinelops.synth               # regenerate the corpus and its truth file
python -m evaluation                      # score both paths on the stub, write results.md
python -m pytest                          # the suite: ~825 tests, about 11 minutes
```

`python -m evaluation` writes a **stub** run. When `results.md` holds a run
measured against a real provider it refuses, because replacing paid figures with
free ones is a bad trade — `--out` writes elsewhere, `--force` overwrites anyway,
and `python -m evaluation.real_run score` rebuilds it from the saved real run.

Demonstrations that print rather than render, each self-contained:

```bash
python -m sentinelops.demo.artefacts        # a cycle, the brief and the audit report
python -m sentinelops.demo.generate_pack    # the audit evidence pack
python -m sentinelops.demo.jumps            # one finding's reminder and escalation timeline
python -m sentinelops.demo.section_eight    # the portfolio analytics
python -m sentinelops.demo.lifecycle        # the evidence-round loop
python -m sentinelops.demo.inbox            # reminders, escalation and notifications
python -m evaluation.demo_intelligence      # the model-backed capabilities, scored
```

## Running against a real model

Nothing calls a provider unless you ask it to. `.env` holds the key and is
gitignored; it deliberately does **not** set the provider, so tests and demos
cannot spend money by accident.

```bash
# .env
OPENAI_API_KEY=sk-...
```

```bash
# PowerShell — this shell only
$env:SENTINELOPS_LLM_PROVIDER = "openai"
python -m streamlit run src/sentinelops/ui/app.py
```

Which model runs which stage is configuration, in
[`src/sentinelops/llm/models.py`](src/sentinelops/llm/models.py): the cheaper
model reads documents (assessment, classification, taxonomy, recurrence), the
larger one writes what a person sends on (the prioritisation brief, the audit
report). Override per stage without touching code:

```bash
$env:SENTINELOPS_MODEL_BRIEF = "gpt-4.1-mini"
```

### Measured runs

The evaluation harness runs the whole corpus against a provider under a hard
budget:

```bash
python -m evaluation.real_run replay   --budget 1.20     # the full replay
python -m evaluation.real_run resume   --budget 0.30     # finish a stopped one
python -m evaluation.real_run baseline --budget 0.80     # the naive comparison
python -m evaluation.real_run artefacts --budget 0.15    # brief, report, pack
python -m evaluation.real_run score --baseline-model gpt-4.1-mini
```

Four things protect the money, all learned the hard way:

- **The budget is a hard stop.** Every call is priced from its own response as
  it returns, and the run is abandoned before a call would cross the cap.
- **Runs checkpoint every 25 calls** and save on any exception, so an
  interruption costs one checkpoint rather than the run. `resume` finishes from
  there without repaying.
- **The baseline journals every answer**, so an interrupted baseline replays
  from disk for free.
- **During a paid run the provider factory points at a provider that does not
  exist**, so a stage falling back to its own client fails loudly instead of
  spending outside the budget.

Every penny spent is recorded in `data/real/spend.json`, including runs that
produced nothing.

## Reading the results

[`results.md`](results.md) is generated, never hand-edited. It carries its own
caveats and they are not decoration:

- Every figure in the real-provider table is marked **quotable or not**, and two
  of those marks are computed rather than asserted — if a run had refused
  verdicts unread, the detection figures would mark themselves unquotable.
- The corpus is **synthetic with constructed failure modes**: the generator
  decided what counted as a gap and then wrote a document to embody it.
- The manual comparison is a **simulation**, with its assumptions printed beside
  it.
- The token comparison against the naive baseline is stated twice: total against
  total, and assessment against assessment. Only the second is like-for-like,
  because the pipeline also classifies and detects recurrence and the baseline
  does neither.

## Where things are

| Path | What |
|---|---|
| `src/sentinelops/stages/` | The pipeline: trigger, pre-screen, assess, flag, follow-up, remediation, rounds, review, audits, taxonomy, intelligence |
| `src/sentinelops/llm/` | The provider boundary — prompts, schemas, metering, models. No SDK type crosses out of it |
| `src/sentinelops/analytics.py` | Section 8's figures. Imports nothing from `llm/`, asserted by test |
| `src/sentinelops/priority.py` | The deterministic ranking behind the brief |
| `src/sentinelops/pack.py` | The audit evidence pack, rebuilt from the log alone |
| `src/sentinelops/ui/` | The dashboard: `app.py` is layout, `view.py` and `service.py` import no Streamlit |
| `src/sentinelops/synth/` | The seeded corpus and its ground truth |
| `evaluation/` | The harness — outside the package, because it reads the answers |
| `data/truth/` | Ground truth. Nothing in `src/` may read it, enforced by test |
| `data/real/` | A real run's database, metrics and spend ledger |
| `data/artefacts/`, `data/packs/` | Generated brief, audit report and evidence pack |
| `CLAUDE.md` | The build spec this was written against |
| `PROGRESS.md` | What each slice did, and what it left open |

## How it is built

**Deterministic by default.** Scheduling, applicability, due dates, reminder and
escalation timing, status transitions, closure, permission checks and every
analytic are code. A language model does five things, all of them reading free
text written by a person:

1. classify a gap into a category derived from the corpus
2. suggest a severity — advisory; the auditor assigns
3. evaluate submitted evidence, with citations verified against the source
4. detect recurrence over a deterministically filtered shortlist
5. write the prioritisation brief, one call per cycle

Plus drafting the audit report's summary, where every sentence must cite the
findings it rests on. **The auditor closes a finding. Always.**

**The trail is a by-product.** Events are appended as things happen, hash-chained,
and the evidence pack is rebuilt from that list alone — so if the pack builds,
the trail was sufficient. Evidence is write-once, enforced by database trigger.

## Tests

```bash
python -m pytest              # everything, about 11 minutes
python -m pytest tests/test_ui.py
```

The suite runs entirely on the deterministic stub, costs nothing, and never
writes over `results.md`. Alongside the usual unit coverage it enforces the
invariants the design rests on: that analytics touches no model, that nothing in
`src/` reads the truth file, that no audit event carries a wall-clock date, that
an owner cannot reach an auditor's page, and that every prompt names the shape
its schema requires.

## Known limitations

Named plainly, and in more detail in `results.md` and `PROGRESS.md`:

- Evidence enters **through the system**. There is no collection from email,
  SharePoint or ticketing, by design.
- The accuracy figures are measured on a corpus we generated. Real evidence is
  messier, longer and ambiguous in ways this does not reproduce.
- Recurrence finds more of what was planted than the stub does and links more
  that was not: recall improved, precision fell. Reported in both directions,
  and the links are advisory.
- The hash chain proves the record has not changed since it was written. It does
  not prove a submitted document was genuine.
- No authentication, no real email, no multi-tenancy — all declared non-goals.
