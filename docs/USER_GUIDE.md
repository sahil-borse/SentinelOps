# SentinelOps — user guide

Every screenshot below was taken by driving the real application in a real
browser ([`docs/capture.py`](capture.py)). Nothing is a mock-up, so if the
interface changes and this guide is not re-captured, the difference will show.

> **The images are one slice behind.** The v3 migration renamed the AI verdict
> from *Finding* to *Assessment*, so some captions in the screenshots still read
> "Finding detail". The text below is current; the pictures are re-taken once the
> migration settles, with `python docs/capture.py`.

**Contents**

1. [Install and start](#1-install-and-start)
2. [What you are looking at](#2-what-you-are-looking-at)
3. [The guided walkthrough](#3-the-guided-walkthrough) — the six-minute tour
4. [The operator console](#4-the-operator-console)
5. [Uploading your own evidence](#5-uploading-your-own-evidence)
6. [The audit pack](#6-the-audit-pack)
7. [Starting over](#7-starting-over)
8. [Running it without the interface](#8-running-it-without-the-interface)
9. [When things look wrong](#9-when-things-look-wrong)

![The whole dashboard](images/13-whole-page.png)

---

## 1. Install and start

Python 3.11 or newer.

```bash
pip install -e ".[dev,ui]"
streamlit run src/sentinelops/ui/app.py
```

The browser opens on `http://localhost:8501`. Nothing else needs a terminal
after this — the calendar, the cycles, uploads, re-assessment, the audit pack
and the integrity check are all buttons.

On first open the application seeds itself with a **synthetic organisation**:
seven business areas, fourteen compliance controls, and a year of evidence of
deliberately mixed quality. State lives in `data/demo/sentinelops.db` and
survives a page reload.

![The dashboard on first open](images/01-first-open.png)

Nothing has run yet, so the counters are at zero. That is expected: press the
first walkthrough button.

---

## 2. What you are looking at

The page has two halves.

| | |
|---|---|
| **Guided walkthrough** (top) | Six steps, one button each. Explains the problem before you press, and what the numbers mean afterwards. Start here. |
| **Operator console** (below the divider) | Every panel in full detail. Safe to ignore on a first pass — the walkthrough drives all of it. |

The walkthrough tracks progress by looking at **the database, not a click
counter**, so reloading the page mid-demo picks up where the data actually is.

---

## 3. The guided walkthrough

### Step 1 — Raise this month's checks

Fourteen controls apply across seven areas, but not the same ones everywhere.
Deciding which control applies where is the part teams do from memory.

Press **Raise the checks that are due**.

![After raising the checks](images/02-checks-raised.png)

The point to notice is not the total — it is that the areas differ. Payments
Processing is in scope for fourteen controls and Financial Reporting for five,
because one handles personal data and faces customers and the other does not.
No one decided that by hand; it comes from each control's applicability rule
evaluated against each area's attributes.

Some checks are **not** raised at all, because an approved exception covers
them. Those are recorded too.

### Step 2 — Let three months pass

Press **Advance three months**. This runs three monthly cycles.

![Three months later](images/03-time-passes.png)

Checks fall due, go unanswered, and the findings raised from them are chased and
then escalated on a severity-driven timer. Nobody had to notice a deadline.

> **A note on escalation.** Two clocks run on every open finding: a reminder
> cadence and an escalation timer, both set by the severity the auditor
> assigned. A Major finding is escalated three days past its target date, an
> Observation seven — never more than a week in any case. Escalation goes up
> the owner's own reporting line *and* to PA/InfoSec, and the reminders keep
> going afterwards: escalating is not a way of handing the problem on.

### Step 3 — Find the report that looks fine and is not

Press **Show me one**.

![The near-miss, selected](images/04-near-miss-walkthrough.png)

Then scroll down to **Assessment detail**. This is the view the whole system is
built around:

![The cited sentence, highlighted in the source](images/05-citation-highlighted.png)

The report was filed on time, by the right person, in the right format, and
satisfies two of its three requirements. The **highlighted sentence is the one
that fails**. That is the difference between an assistant that says *gap* and a
system that can show you the sentence, in your own document, that made it say
so.

Three things on this panel are worth pointing at:

- **Decided by** — `s3_model` means a language model judged it. Rule-decided
  findings say so instead, and cost nothing.
- **Confidence** and **Human review** — a low-confidence verdict is routed to a
  person rather than asserted.
- **Provenance** — the prompt version, a hash of the criteria as they stood,
  and a hash of the evidence. Enough to reproduce the decision months later, or
  to show it was made against criteria that have since changed.

Every quoted span is checked back against the source. **A verdict whose
quotation cannot be found in the document is thrown away rather than
recorded** — so a citation you can see is a citation that resolved.

### Step 4 — Count what that cost

Press **Show the bill**.

![The cost of the cycle so far](images/06-what-it-cost.png)

Roughly half of all decisions never reach a model: evidence that never arrived,
evidence of the wrong type, evidence too old to speak for its period, and
numbers measured against a threshold are all decidable in code — exactly, and
for nothing. Only ambiguous prose is worth paying for.

### Step 5 — Fix one, and prove it is fixed

Press **File a correction and re-check it**.

![The loop closed](images/07-remediated.png)

A corrected report is filed and goes through **the same** pre-screen and the
same assessment as the original — same criteria, same citation rule. If it
passes, an auditor closes the finding with remarks naming the assessment that
cleared it. If it does not, the finding **stays open** and the round is counted:
a finding is only ever closed by an auditor who is satisfied.

**Both assessments are kept.** The failure is marked superseded rather than
deleted, so the record still shows what was wrong and when. In *Assessment detail*
the **Assessment history** panel lists both.

### Step 6 — Prove none of this was edited afterwards

Press **Verify the record and build the pack**.

![The audit chain verified](images/08-chain-verified.png)

Every log entry carries the hash of the entry before it, so altering one line
breaks the chain at that point and at every point after. It cannot be edited
quietly. The auditor's pack is then rebuilt **from that log alone** — no
current-state table is read — and offered for download at the bottom of the
page.

---

## 4. The operator console

Everything the walkthrough did, in detail.

![The operator console controls](images/09-operator-console.png)

| Control | What it does |
|---|---|
| **Run cycle now** | One full pass at the current simulated date |
| **+1 day / +1 week / +1 month** | Advance the calendar and run the cycle that falls due |
| **Start over** | Delete the demo database and reseed |

The two metric rows are live. The second is the cost meter — watch it *not*
move when a check is decided by rule.

### Status and queues

![Status by area and the overdue queue](images/10-status-and-queue.png)

**Compliance status by process area** — worst first. *Worst severity* is a
documented formula: the control's own weight × how badly the verdict failed ×
how critical the area is × how long it has been outstanding. The arithmetic is
stored on every flag, so the number can be checked rather than trusted.

**Overdue and escalation queue** — what is late, worst first. *Escalation* 0
means it is with the owner, 1 a department head, 2 Group Compliance.

### Open findings

![Upload and open findings](images/11-upload-and-actions.png)

Every non-compliant assessment raises a **finding** against the owning unit, and
so does every audit — findings are children of audits, and both kinds are chased
and closed by exactly the same machinery. A finding is Open or Closed and nothing
else. Its target date is derived from the
severity — three days for an urgent Major, twenty-eight for an Observation —
and *Chased* counts how many times the owner has been reminded or sent back for
more evidence.

Owner progress (*acknowledged*, *action in progress*, *implemented*) is
self-reported and advisory: it never closes anything. Closed findings are listed
under the expander with the auditor who closed them and their remarks.

---

### Patterns across the portfolio

Everything above this point on the screen is one finding at a time. This section
is the part that is worth a system rather than a spreadsheet.

![Recurrence across units and months](images/14-recurrence-and-brief.png)

**This has happened before.** Every finding is classified into a gap category —
by a model, because the auditors who wrote the descriptions share no vocabulary
and section 1 says plainly that no standard taxonomy exists. Findings in the same
category, in a *different unit or a different period*, are then compared, and the
ones that describe the same underlying failure are linked.

On the demo corpus this connects privileged access left with three leavers in
Payments (March 2026), contractor accounts left active in IT Services
(November), and a partner API credential never revoked in Payments again
(February 2027). Three units, eleven months, and not one word in common. That
comparison is the claim this project rests on: nobody holds it in their head.

The link is **advisory**. It points at the earlier finding and merges nothing —
both stay open on their own, with their own owners and their own target dates.

Most of the work here is not the model's. Which findings are even eligible is
decided in code — same category, different unit or period, raised earlier — and
on the demo corpus twelve of seventeen findings have no eligible candidate at
all, so no model call is made for them.

![The prioritisation brief](images/15-prioritisation-brief.png)

**Prioritisation brief.** One model call per cycle, over a ranking the code
computed and the metrics underneath it. The ranking is deterministic on purpose:
a model that ordered the queue would be making the prioritisation decision, and
section 2 does not let it. It interprets the order; it does not choose it.

Every claim in the brief cites the findings it rests on. If the drafted brief
makes a statement it cannot attribute, the brief is withheld and you see the
metrics without it — the same rule the audit report follows, and for the same
reason: a sentence nobody can trace is a sentence nobody can check.

### Portfolio analytics

![Portfolio analytics](images/16-portfolio-analytics.png)

Expand **Portfolio analytics** for everything in section 8 of the spec: open
versus closed with percentages per unit, severity mix, overdue findings bucketed
by age, findings by unit and by gap category and by audit kind, the recurrence
rollup, the distribution of evidence rounds, closure performance by severity, the
open-findings trend by month, and what falls due in the next thirty days.

**None of it goes near a model.** That is asserted two ways in the test suite:
statically, that `analytics.py` imports nothing from `llm/`, and at runtime, by
rigging the provider factory to raise and computing the whole portfolio anyway.
Watch the cost meter while you expand the panel — it does not move.

The trend line is replayed from raise and closure dates rather than sampled from
today's state, so each month shows what was actually true then.

---

## 5. Uploading your own evidence

In **Submit evidence**:

1. **Against check** — pick the check the document answers.
2. **Document type** — the first entries are what this control accepts. Pick
   one of the others to watch the wrong-type rule reject it **without a model
   call**; the cost meter will not move.
3. **Submitted by** — whose name goes in the audit trail.
4. **This is remediation for an existing finding** — tick when fixing a failure.
5. **Re-check it straight away** — on by default, so one click files and judges.
6. Upload a file (`.txt`, `.md`, `.json`, `.csv`, `.log`) **or** paste text.
7. Press **Submit evidence**.

The confirmation names the record it created, its size, the verdict it reached
and whether the finding closed.

> Uploaded documents are not a special case. They land in the same table as the
> generated corpus and take the same path through the pre-screen and the
> assessment.

**Long documents.** Evidence can be a fifty-page export. The document panel is
a fixed-height frame with its own scrollbar, so the page never grows with the
document, and it opens scrolled to the first highlight. **Show more** makes the
panel taller — not the page longer.

---

## 6. The audit pack

![Audit controls and downloads](images/12-audit-and-downloads.png)

- **Verify audit chain** — re-walks every entry and reports either the number
  verified or the sequence number of the first broken link.
- **Generate audit pack** — rebuilds the auditor's document and offers it as
  HTML or Markdown.

The pack contains a cover, a coverage summary, the exception register with
approvers and rationales, the findings register **with the cited excerpts
inline**, the finding register from raising to closure, a method note, and the
full chronological trail.

It is assembled from the audit log and nothing else. If the log could not
support a section, that section would be missing rather than quietly filled in
from elsewhere.

---

## 7. Starting over

**Start over** in the operator console deletes `data/demo/sentinelops.db` and
reseeds. The corpus is seeded and reproducible, so you get the identical
organisation, controls and evidence every time — the same demo, twice.

---

## 8. Running it without the interface

```bash
python -m sentinelops.synth               # regenerate the corpus and truth file
python -m evaluation                      # both pipelines, writes results.md
python -m sentinelops.demo.generate_pack  # the audit pack for the full year
python -m pytest                          # the test suite
python docs/capture.py                    # re-take the screenshots in this guide
```

---

## 9. When things look wrong

**The page is blank or the counters are zero.** Nothing has run yet. Press the
first walkthrough button.

**A button seems to do nothing.** It should always report back. If it does not,
the log is in the terminal running Streamlit.

**"No checks assessed yet".** Run step 1.

**The whole page reloads on every click.** That is Streamlit; it re-runs the
script on each interaction. State is in the database, so nothing is lost.

**The accuracy figures look too good.** They probably are. Unless a real
provider is configured, assessments come from `FakeModelClient`, a deterministic
keyword stub measured at ~91% agreement with the ground truth. For real
numbers:

```bash
echo "OPENAI_API_KEY=sk-..." > .env
SENTINELOPS_LLM_PROVIDER=openai streamlit run src/sentinelops/ui/app.py
```

`results.md` carries this caveat and several others in the file itself. They are
not decoration: the corpus is synthetic with constructed failure modes, and the
manual comparison it reports is a simulation whose assumptions are printed
alongside it.
