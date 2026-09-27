# Recording the demo — click by click

For whoever is at the keyboard, whether or not they have used the application.
The audio is already recorded; this produces footage that matches it.

Everything runs on the deterministic stub: no API key, no spend, and the same
clicks produce the same screen every time. That is what lets you re-record one
section without the others drifting.

---

## Part 0 — Before you record

### 0.1 Start the application

Open a terminal in the project folder (`D:\projects\SentinelOps`) and run:

```powershell
$env:SENTINELOPS_LLM_PROVIDER = "fake"
python -m streamlit run src/sentinelops/ui/app.py
```

A browser opens at `http://localhost:8501`. First start takes 20–40 seconds
while it builds its database.

> **If you changed any code since the last run, stop the server and start it
> again.** Streamlit keeps files it has already loaded, so an old version can
> stay on screen. Ctrl+C in the terminal, then run the command again.

### 0.2 Set the browser up

1. **Full screen** (F11). No bookmarks bar, no second tab visible.
2. **Zoom exactly 100%** (Ctrl+0).
3. Screen resolution **1920×1080**. If your display is larger, record a
   1920×1080 region.
4. Close anything that can pop up mid-take — chat, mail, update prompts.

### 0.3 Open these four files in background tabs

You will switch to them during sections 4, 5 and 6. Open each with Ctrl+O:

| Tab | File |
|---|---|
| Brief | `data/artefacts/prioritisation_brief_2027-04-15.html` |
| Audit report | `data/artefacts/audit_report_AUD-REL-2027-03.html` |
| Evidence pack | `data/packs/audit_pack_20260101_20270415.html` |
| Summary | `data/artefacts/results_summary.html` |

### 0.4 Learn the screen — 2 minutes

**Left sidebar, top to bottom:**

- **Work** — Today · Findings · Schedule · Inbox
- **Insight** — Portfolio · Recurrence
- **Assurance** — Audit trail · Walkthrough
- **Acting as** — a dropdown of people. Changing it changes who you are and
  which pages exist. It is not a login.
- **Simulated date** — the date *inside* the story. Not today's real date.
- **Next event** — a small card naming what happens next in the story.
- **Jump to next event** — the teal button. Moves the clock to that event.
- **Run cycle now**, **+1 day**, **+1 week**, **+1 month** — move time forward.
- **Reset scenario** — puts everything back to the beginning. Your undo button.

**Top right of the page:** two grey chips — who you are acting as, and the
simulated date. Useful for checking you are in the right state before a take.

### 0.5 The three people you will act as

| Name | Role | What they can do |
|---|---|---|
| **P. Kaur** | PA/InfoSec (the auditor) | Reviews evidence, accepts or rejects it, closes findings |
| **C. Okonkwo** | Unit owner, Facilities | Files evidence. Cannot close anything |
| **Y. Nakamura** | Unit owner, IT | Same, for IT |

To switch: click the **Acting as** dropdown, type part of the name, click it.

---

## Part 1 — Session A (the later part of the story)

Captures sections **3C, 4, 5, 6, 7**.

### 1.1 Set the clock — do this before recording, ~4 minutes

1. Click **Reset scenario**. Wait for the page to settle.
2. Click **+1 month**. Wait until the spinner stops and the date changes.
3. Repeat **+1 month** until the top-right chip reads a date in **April 2027**.
   That is **13 presses**. Each one runs a month of the story, so it takes a
   few seconds.
4. Check the top-right chips read **P. Kaur · PA/InfoSec** and **Apr 2027**.

> Press once, wait, press again. Pressing quickly queues them up and the page
> appears frozen.

### 1.2 Section 3C — Recurrence · 18 seconds

**What it shows:** the same problem appearing again somewhere else.

1. Sidebar → **Recurrence**.
2. Wait for the four boxes at the top (Suggested links, Recurring categories,
   Longest gap, Findings involved).
3. Scroll down to the heading **This has happened before**.
4. Under it is a dropdown labelled **Gap category**. Click it and choose
   **access not revoked**.
5. Scroll so that the **first card** fills the middle of the screen. A card has
   a coloured tag, "N months apart", and two findings side by side.

**Recording:**

| Time | Do this |
|---|---|
| 0:00–0:04 | Hold still at the top of the page |
| 0:04–0:08 | Slowly scroll down to the first card |
| 0:08–0:18 | **Do not move.** The card is on screen for the whole line |

The left half is the earlier finding, the right half the one that resembles it.

### 1.3 Section 4 — Application of AI · 52 seconds

**What it shows:** what the model does, and that a person still decides.

1. Sidebar → **Findings**.
2. A table appears under the heading **On record**.
3. Find a row whose name starts **FND-CHANGED-PROCESS** or
   **FND-BACKUP-VERIFY**. Click **anywhere on that row** — its name will do.
   A large panel opens over the page.
4. The panel has four tabs: **Evidence · Evidence rounds · Recurrence ·
   Audit timeline**. Stay on **Evidence**.
5. You should see a grey badge like **Gap**, a confidence number, the words
   **Model assessment**, and below that the document with **one line
   highlighted in yellow**.

**Recording:**

| Time | Do this |
|---|---|
| 0:00–0:14 | Hold on the Evidence tab with the highlighted line visible |
| 0:14–0:26 | Scroll up a little inside the panel to the **Severity** row. It reads "assigned by the auditor · the model suggested …" — hold there |
| 0:26–0:38 | Switch to the **Brief** browser tab |
| 0:38–0:52 | Switch to the **Audit report** tab, showing the paragraph with `[FND-…]` references |

Close the panel afterwards with the **Close** button at its top right.

### 1.4 Section 5 — Alignment with scope · 27 seconds

1. Sidebar → **Portfolio**. Wait for the charts to draw.
2. Sidebar → **Audit trail**. Two boxes: **Verify the chain** and **Audit
   pack**. Each has a button, and **nothing happens until you press it** —
   the verification line does not appear on its own.

| Time | Do this |
|---|---|
| 0:00–0:10 | Scroll slowly down Portfolio, once, without stopping |
| 0:10–0:12 | Sidebar → **Audit trail** |
| 0:12–0:19 | Click **Verify audit chain**. A green line appears saying the chain is intact and how many entries were checked. Hold on it |
| 0:19–0:27 | Click **Generate audit pack**. It replays the log and offers **Download pack (HTML)**. Hold there |

Generating takes a few seconds. If it is still working when the audio ends,
switch to the **Evidence pack** browser tab instead and hold on that — same
document, already built.

### 1.5 Section 6 — Outcomes · 47 seconds

1. Switch to the **Summary** browser tab (`results_summary.html`).

**Do not scroll. The page is built to fill the screen exactly.**

| Time | Do this |
|---|---|
| 0:00–0:47 | Nothing. Leave it still for the whole section |

If you want to draw the eye, move the **mouse pointer** slowly to the figure
being spoken about. Never move the page.

### 1.6 Section 7 — Limitations · 35 seconds

Same page. Move the pointer away and hold on the dark panel at the bottom left
headed **Scope**. No movement at all. **Stop recording two seconds after the
last word.**

---

## Part 2 — Session B (the early part of the story)

Captures sections **1, 3A, 3B**. The clock must go backwards, which means a
reset — so do this after Session A.

### 2.1 Set the clock — ~1 minute

1. Click **Reset scenario**.
2. Click **+1 month**. Wait. Click **+1 month** again.
3. The chip should read a date around **30 March 2026**.
4. Acting as should be **P. Kaur · PA/InfoSec**.

### 2.2 Prepare section 3B's evidence — off camera

Section 3B shows the auditor reviewing evidence, so evidence has to exist.

1. **Acting as** → type `Okonkwo` → choose **C. Okonkwo · Unit owner ·
   Facilities**.
2. Sidebar → **Finding detail**.
3. At the top is a dropdown listing her findings. Choose any one.
4. Scroll to the box headed **Evidence for this finding** and click
   **File evidence for this finding**. A window opens.
5. In **…or paste the evidence**, paste:
   ```
   Process review — Facilities
   All changed processes were reviewed before go-live.
   Compliance impact recorded for each change.
   ```
6. Click **File evidence round**. The window closes.
7. **Acting as** → back to **P. Kaur · PA/InfoSec**.

Remember which finding you used.

### 2.3 Section 1 — The problem · 34 seconds

1. Sidebar → **Today**.
2. At the top there should be a **green banner** beginning "Cycle complete".

| Time | Do this |
|---|---|
| 0:00–0:34 | Nothing at all. One still screen for the whole section |

> No green banner? Press **+1 day** once and it reappears.

### 2.4 Section 3A — The chase · 23 seconds

Stay on **Today**. Look at the sidebar's **Next event** card — it names a
finding and what happens next.

| Time | Do this |
|---|---|
| 0:00–0:04 | Hold, with the Next event card visible |
| 0:04 | Click **Jump to next event** once |
| 0:10 | Click it again |
| 0:16 | Click it a third time |
| 0:19–0:23 | Hold still |

Wait for each jump to finish before the next. The card's text changes each
time — that is the point of the shot.

### 2.5 Section 3B — Evidence and authority · 42 seconds

| Time | Do this |
|---|---|
| 0:00–0:18 | **Findings** → open the finding you filed evidence against → **Evidence** tab, highlighted line visible. Hold. |
| 0:18–0:30 | Close the panel → sidebar **Today** → under **Review queue**, the first item is open. The model's reading is on the left, the document on the right |
| 0:30–0:36 | Click **Mark insufficient**. The finding stays **Open** and a new round opens |
| 0:36–0:42 | **Acting as** → **C. Okonkwo** → **Finding detail** → hold. **There is no Close button on this screen** — that absence is the shot |

> Review queue empty? You skipped 2.2. Go back and file the evidence.

---

## Part 3 — Section 2

A slide, not the application. 31 seconds of the architecture diagram.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| Error mentioning a missing attribute | Old server. Ctrl+C in the terminal, start it again |
| Error about a missing column | Delete `data\demo\sentinelops.db`, reload |
| Page stuck with a spinner | Wait. A cycle takes a few seconds. Do not click again |
| Wrong date on screen | **Reset scenario** and redo the month presses for that session |
| Wrong person on screen | Change **Acting as**. Check the chip at the top right |
| Recurrence page nearly empty | The clock is too early. It needs Session A's date |
| A finding named in the audio isn't on screen | Read what is there. The story is the same; the identifier is not the point |

---

## Final check before each take

1. Top-right chips: right **person**, right **date**.
2. Sidebar expanded.
3. Browser full screen, 100% zoom.
4. Nothing loading.
5. For 3B only: a round is waiting in the review queue.
