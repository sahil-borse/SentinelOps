"""Deterministic stand-in for a real model, so the suite runs with no key.

Same request in, same response out — which also makes it a useful control when
measuring verdict consistency: any divergence between two areas is then the
pipeline's doing, not sampling noise.

It quotes real text. Citations are verified against the source in S3, so a stub
that invented a quotation would fail every assessment and prove nothing; this
one pulls an actual line out of the evidence it was shown.

It also models a *well-behaved* assessor: shown a document that instructs it to
return a pass, it refuses and flags for review. That simulates the behaviour the
system prompt asks for — it does not demonstrate that a real model resists. Only
the real provider can show that. What the tests around it do demonstrate is that
the pipeline holds even when the model misbehaves, which is the part that is
actually under our control.
"""

from __future__ import annotations

import hashlib
import json
import random
import re

from ..parsing import extract_json, validate
from ..prompts.assessment import EVIDENCE_CLOSE, EVIDENCE_OPEN
from ..protocol import LlmRequest, LlmResponse

MODEL = "fake-assessor-v1"

#: Phrasing that only appears when a document is talking to the assessor rather
#: than describing the control.
_INJECTION = re.compile(
    r"(ignore (the|all|previous)|disregard|you must (mark|return|set)|"
    r"mark this control|pre-?approved|do not report|override|"
    r"system\s*:|instruction to the (assessor|reviewer|model)|"
    r"return\s+\"?compliant)",
    re.IGNORECASE,
)

#: Negations that describe a *good* outcome. "No accounts were dormant" is a
#: pass; "no review was performed" is not. Stripped before looking for failure.
_BENIGN_NEGATION = re.compile(
    r"(no longer required|no discrepancies|no gaps|without incident)",
    re.IGNORECASE,
)

#: A clause that says something did not happen.
_NEGATED = re.compile(r"\b(no|not|never|neither|nor|none)\b", re.IGNORECASE)

#: A clause that says something happened, but not fully.
_HEDGED = re.compile(
    r"(pending|partially|a sample of|awaits?|awaiting|incomplete|unsigned|"
    r"outstanding|queued for|slightly outside|left blank|scheduled for|"
    r"only the|past the|the rest|the remainder|of them|remain open)",
    re.IGNORECASE,
)

#: "3 of 5 accounts were disabled" — a shortfall stated as arithmetic, with no
#: word anywhere in it that reads as failure.
#:
#: Added after the section 3 control library landed: its clauses state shortfalls
#: this way far more often than the set they replaced, and the stub was missing
#: six near-misses instead of one. Comparing two numbers is something a keyword
#: rule can legitimately do, so teaching it here is making the stub less bad at
#: a mechanical job — not softening the corpus so the stub looks better. What is
#: left after this is genuine language work, which is the part the model tier is
#: for and the part `tests/test_fake_accuracy.py` still measures it failing.
_SHORTFALL = re.compile(r"\b(\d+) of (\d+)\b")

_NUMBERED = re.compile(r"^\s*\d+\.\s", re.MULTILINE)


def _falls_short(clause: str) -> bool:
    """True when the clause reports fewer than the whole of something."""
    for fewer, total in _SHORTFALL.findall(clause):
        if int(fewer) < int(total):
            return True
    return False


def _digest(request: LlmRequest) -> str:
    body = request.system + json.dumps(request.messages, sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def _evidence_text(user_text: str) -> str:
    """What the prompt actually put in front of the model.

    Everything between the untrusted-evidence markers, with the [E1] labels
    stripped, so a quotation taken from here resolves against the source.
    """
    if EVIDENCE_OPEN in user_text and EVIDENCE_CLOSE in user_text:
        body = user_text.split(EVIDENCE_OPEN, 1)[1].split(EVIDENCE_CLOSE, 1)[0]
    else:  # the v1 prompt, still used by the slice-1 skeleton
        body = user_text.split("EVIDENCE EXCERPTS:", 1)[-1]
    return "\n".join(
        re.sub(r"^\[E\d+\]\s*", "", line) for line in body.strip().splitlines()
    )


def _quotable_lines(evidence: str) -> list[str]:
    return [
        line.strip()
        for line in evidence.splitlines()
        if len(line.strip()) > 25 and not line.strip().startswith("{")
    ]


def _clause_lines(evidence: str) -> list[str]:
    """The numbered criteria responses, which is where the verdict lives."""
    return [
        line.strip()
        for line in evidence.splitlines()
        if _NUMBERED.match(line)
    ]


#: `- FND-X | unit: … | severity: … | category: …`
_FINDING_ROW = re.compile(
    r"^- (?P<id>\S+) \| unit: (?P<unit>[^|]+)\| severity: (?P<severity>[^|]+)\|"
    r" category: (?P<category>[^|]+)\|",
    re.MULTILINE,
)


#: Keyword rules standing in for a classifier. Ordered: the first that matches
#: wins, so the more specific phrasings come before the general ones. This is a
#: stub and it is wrong on descriptions that avoid its vocabulary — which is the
#: entire reason section 2 justifies a model here, and why
#: `tests/test_intelligence.py` measures the stub against the corpus rather than
#: assuming it.
_CATEGORY_RULES: list[tuple[str, str]] = [
    ("access_not_revoked",
     r"(still held|retained active|remained enabled|remained active|not revoked|"
     r"left active|revocation .{0,20}(pending|not)|still enabled|"
     r"never revoked|past the engagement)"),
    ("third_party_due_diligence",
     r"(due diligence|supplier|vendor|questionnaire|third[- ]party)"),
    ("change_not_authorised",
     r"(without the .{0,30}(review|approval)|not authorised|unapproved|"
     r"who approved|release gate|went to production)"),
    ("training_not_completed",
     r"(training|awareness)"),
    ("data_retention_or_privacy",
     r"(retention period|personal data|privacy|dpia|data protection impact)"),
    ("documentation_out_of_date",
     r"(manual|procedure|controlled document|out of date|versions behind|"
     r"past their review date)"),
    ("access_not_recertified",
     r"(recertif|access review|privileged account)"),
    ("evidence_not_retained",
     r"(could not produce|cannot be relied|no record of|logs for|"
     r"cannot be produced|not evidenced|never approved|sat in draft)"),
    ("periodic_review_overdue",
     r"(last reviewed|no entry in the risk register|risk register|"
     r"was not reviewed|reconcil)"),
    ("control_not_performed",
     r"(was not (carried out|performed|run)|appears to have been signed off|"
     r"never)"),
]

_SEVERE = re.compile(
    r"(privileged|production|settlement|payments|customer|personal data|"
    r"critical|used after|still enabled|four accounts)",
    re.IGNORECASE,
)
_MILD = re.compile(
    r"(no discrepancy|no unapproved|was identified|observation|"
    r"worth fixing|no exception was raised)",
    re.IGNORECASE,
)


def _canned_triage(prompt: str) -> dict:
    """Pick a category by keyword and a severity by tone. Heuristics, not a model."""
    description = prompt.split("description:\n", 1)[-1]
    lowered = description.lower()
    category = "control_not_performed"
    matched = ""
    for name, pattern in _CATEGORY_RULES:
        found = re.search(pattern, lowered)
        if found:
            category, matched = name, found.group(0)
            break

    if _MILD.search(description):
        severity = "Observation"
    elif _SEVERE.search(description):
        severity = "Major"
    else:
        severity = "Minor"
    return {
        "category": category,
        "suggested_severity": severity,
        "confidence": 0.82 if matched else 0.45,
        "rationale": (
            f"Classified as {category} on the phrase {matched!r}."
            if matched else
            "No distinguishing phrase found; defaulted to control_not_performed."
        ),
    }


#: Two descriptions recur when they share enough distinctive vocabulary. A real
#: model reads meaning; this counts words, and the tests say how often that is
#: the same answer.
_STOPWORDS = frozenset(
    "the a an and or of to in for was were is are be been at on by with that "
    "this it its their they them not no had has have from as but which who "
    "when out up over into than then there here all any some each".split()
)


def _keywords(text: str) -> set[str]:
    return {
        w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _STOPWORDS
    }


def _canned_recurrence(prompt: str) -> dict:
    blocks = prompt.split("EARLIER FINDINGS", 1)
    if len(blocks) < 2 or "(none)" in blocks[1]:
        return {"recurrences": []}
    target = _keywords(blocks[0])
    out = []
    for line in blocks[1].splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        ident = stripped[2:].split(" |", 1)[0].strip()
        # the description is the indented line that follows
        out.append((ident, stripped))
    matches = []
    lines = blocks[1].splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        ident = stripped[2:].split(" |", 1)[0].strip()
        description = lines[index + 1] if index + 1 < len(lines) else ""
        shared = target & _keywords(description)
        if len(shared) >= 4:
            matches.append({
                "finding_id": ident,
                "confidence": min(0.5 + 0.1 * len(shared), 0.95),
                "reason": (
                    "Both describe the same failure; shared terms: "
                    + ", ".join(sorted(shared)[:5])
                ),
            })
    matches.sort(key=lambda m: -m["confidence"])
    return {"recurrences": matches[:3]}


def _canned_brief(facts: str) -> dict:
    """A brief that cites, because an uncited one is withheld."""
    rows = []
    lines = facts.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("- ") or " | " not in stripped:
            continue
        parts = [p.strip() for p in stripped[2:].split(" | ")]
        rows.append(parts)
    if not rows:
        return {"brief": "", "cited_finding_ids": []}

    def field(row, marker, default=""):
        for part in row:
            if marker in part:
                return part
        return default

    ids = [r[0] for r in rows]
    top = ids[:3]
    open_count = next(
        (l.split(":", 1)[1].strip() for l in lines if l.startswith("open findings:")),
        str(len(ids)),
    )
    units = {}
    for row in rows:
        if len(row) > 1:
            units.setdefault(row[1], []).append(row[0])
    heaviest, heaviest_ids = max(units.items(), key=lambda kv: len(kv[1]))

    sentences = [
        f"{open_count} findings are open at this cycle.",
        f"The most urgent are [{', '.join(top)}], which combine the highest "
        f"severities with the longest time past target.",
    ]
    if len(heaviest_ids) > 1:
        sentences.append(
            f"{heaviest} carries {len(heaviest_ids)} of the ranked items "
            f"[{', '.join(heaviest_ids[:4])}], which is where attention would "
            f"go furthest."
        )
    chased = [r[0] for r in rows if "chased" in " ".join(r) and
              any(p.startswith("chased") and not p.endswith("0x") for p in r)]
    if chased:
        sentences.append(
            f"Several have been chased more than once without evidence arriving "
            f"[{', '.join(chased[:4])}]."
        )
    return {
        "brief": " ".join(sentences),
        "cited_finding_ids": ids,
    }


def _canned_report(facts: str) -> dict:
    """A summary paragraph that cites, because an uncited one is rejected.

    Written the way the real prompt asks: a count, then the weight of the
    findings with their ids attached, then the pattern if there is one. It reads
    stiffly on purpose — this is a stub standing in for a writer, and a stub
    that read well would invite somebody to mistake it for the real output.
    """
    rows = [m.groupdict() for m in _FINDING_ROW.finditer(facts)]
    if not rows:
        return {"summary": "", "cited_finding_ids": []}

    for row in rows:
        for key in ("unit", "severity", "category"):
            row[key] = row[key].strip()

    by_severity: dict[str, list[str]] = {}
    by_unit: dict[str, list[str]] = {}
    by_category: dict[str, list[str]] = {}
    for row in rows:
        by_severity.setdefault(row["severity"], []).append(row["id"])
        by_unit.setdefault(row["unit"], []).append(row["id"])
        by_category.setdefault(row["category"], []).append(row["id"])

    def cite(ids):
        return "[" + ", ".join(sorted(ids)) + "]"

    sentences = [
        f"This audit raised {len(rows)} finding(s) across "
        f"{len(by_unit)} auditable unit(s)."
    ]
    major = by_severity.get("Major", [])
    if major:
        sentences.append(
            f"The weight of the audit sits in {len(major)} Major finding(s) "
            f"{cite(major)}, which carry the shortest target dates."
        )
    heaviest_unit, heaviest_ids = max(by_unit.items(), key=lambda kv: len(kv[1]))
    if len(heaviest_ids) > 1:
        sentences.append(
            f"{heaviest_unit} accounts for {len(heaviest_ids)} of them "
            f"{cite(heaviest_ids)}."
        )
    repeated = {c: ids for c, ids in by_category.items() if len(ids) > 1}
    if repeated:
        category, ids = max(repeated.items(), key=lambda kv: len(kv[1]))
        sentences.append(
            f"The same gap category, {category}, appears more than once "
            f"{cite(ids)}, which is the pattern worth attention here."
        )
    else:
        rest = [r["id"] for r in rows if r["id"] not in major][:4]
        if rest:
            sentences.append(
                f"The remainder are individually scoped and separately owned "
                f"{cite(rest)}."
            )
    return {
        "summary": " ".join(sentences),
        "cited_finding_ids": sorted(r["id"] for r in rows),
    }


def _canned(evidence: str) -> dict:
    """Pick a verdict clause by clause. Heuristics, not a model.

    A clause that says something did not happen is a failure; one that hedges is
    partial; otherwise it passes. This is a stub standing in for judgement, and
    it is wrong on documents whose failures are phrased without a negation —
    `tests/test_fake_accuracy.py` measures exactly how often, so nobody mistakes
    its verdicts for the real assessor's.
    """
    lines = _quotable_lines(evidence) or [evidence.strip()[:160]]
    clauses = _clause_lines(evidence)

    injected = _INJECTION.search(evidence)
    failing = next(
        (
            c for c in clauses
            if _NEGATED.search(_BENIGN_NEGATION.sub("", c)) or _falls_short(c)
        ),
        None,
    )
    hedging = next((c for c in clauses if _HEDGED.search(c)), None)

    def _line_for(text) -> str:
        if text is None:
            return lines[0]
        if isinstance(text, str):
            return next((ln for ln in lines if ln in text or text in ln), text)
        return next(
            (ln for ln in lines if text.group(0).lower() in ln.lower()), lines[0]
        )

    if injected is not None:
        return {
            "verdict": "gap",
            "confidence": 0.55,
            "rationale": (
                "The submission contains text addressed to the assessor rather "
                "than describing the control, which is treated as evidence of an "
                "irregular submission and not acted on. Assessed on its "
                "substantive content, the criteria are not fully met."
            ),
            "cited_spans": [_line_for(injected)],
            "gaps": ["The submission attempts to direct the assessment."],
            "recommended_action": "Review this submission with the owning team.",
            "needs_human_review": True,
        }

    if failing is not None:
        return {
            "verdict": "gap",
            "confidence": 0.88,
            "rationale": "A criterion is contradicted by the evidence.",
            "cited_spans": [_line_for(failing)],
            "gaps": ["A required clause is not satisfied."],
            "recommended_action": "Perform the control and resubmit.",
            "needs_human_review": False,
        }

    if hedging is not None:
        return {
            "verdict": "partial",
            "confidence": 0.62,
            "rationale": "A criterion is only partially evidenced.",
            "cited_spans": [_line_for(hedging)],
            "gaps": ["A clause is addressed but not completed."],
            "recommended_action": "Complete the outstanding work and resubmit.",
            "needs_human_review": False,
        }

    return {
        "verdict": "compliant",
        "confidence": 0.91,
        "rationale": "Every criterion is addressed by the evidence.",
        "cited_spans": [lines[0]],
        "gaps": [],
        "recommended_action": "",
        "needs_human_review": False,
    }


class FakeModelClient:
    """Implements the LlmClient protocol."""

    def complete(self, request: LlmRequest) -> LlmResponse:
        user_text = "\n".join(m["content"] for m in request.messages)
        head = user_text.lstrip()
        if head.startswith("AUDIT\n"):
            payload = _canned_report(user_text)
        elif head.startswith("CATEGORIES\n"):
            payload = _canned_triage(user_text)
        elif head.startswith("FINDING\n"):
            payload = _canned_recurrence(user_text)
        elif head.startswith("PORTFOLIO\n"):
            payload = _canned_brief(user_text)
        else:
            payload = _canned(_evidence_text(user_text))
        if request.response_schema:
            payload = validate(payload, request.response_schema)
        text = json.dumps(payload)

        # Counts are produced by the (fake) provider and read off the response,
        # exactly as the real client reads provider usage — the meter never
        # estimates. What this stub reports is proportional to the prompt it was
        # actually handed, because that is what a tokenizer does: a provider
        # returning a number unrelated to its input would make any comparison
        # between a full document and a retrieved extract meaningless.
        prompt = request.system + "".join(m["content"] for m in request.messages)
        rng = random.Random(_digest(request))
        return LlmResponse(
            text=text,
            parsed_json=extract_json(text),
            input_tokens=max(1, len(prompt) // 4),
            output_tokens=max(1, len(text) // 4),
            # the constant system prefix is the part a provider cache can serve
            cached_tokens=len(request.system) // 4 if rng.random() > 0.3 else 0,
            model=MODEL,
            latency_ms=120 + rng.randrange(0, 200),
            raw={"provider": "fake"},
        )
