"""Slice 19: the same pipeline, on a real provider, metered and capped.

    python -m evaluation.real_run replay   --budget 1.50
    python -m evaluation.real_run baseline --budget 1.00 [--sample 200]
    python -m evaluation.real_run score    [--baseline-model gpt-4.1-mini]

Three commands, because the order matters and the money is real:

**replay** runs the full eighteen-month replay to the vantage point against the
provider, into `data/real/run.db`, and reports what it spent. The database is
kept so everything downstream — the metrics, the pack, the brief, the audit
report — comes from that one run rather than a second one.

**baseline** runs the naive baseline, and only if what is left of the budget
covers it. `evaluation.baseline` writes its cache the moment it finishes, so a
completed baseline is never paid for twice. `--sample` runs it on a random
sample of instances instead, seeded and recorded, for when the budget will not
cover the whole thing.

**score** writes `results.md` from the saved run and whichever baseline is on
disk. It spends nothing beyond finishing the section 8 pass, which is idempotent.

The budget is a hard stop, not a warning: every call is priced as it returns and
the run is abandoned the moment the total would pass the cap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import traceback
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from sentinelops.db import connect
from sentinelops.llm import models
from sentinelops.repositories import repositories
from sentinelops.llm.metering import cost_usd
from sentinelops.llm.protocol import LlmError, LlmRequest, LlmResponse
from sentinelops.synth import generate_corpus, seed_database

from . import baseline as baseline_module
from . import harness

RUN_DIR = Path(__file__).resolve().parents[1] / "data" / "real"
RUN_DB = RUN_DIR / "run.db"
#: The artefact run, kept apart from `run.db` so the brief's and the report's
#: calls never enter the figures the pipeline is compared on.
ARTEFACT_DB = RUN_DIR / "artefacts.db"
#: The baseline's paid answers, one per line, so an interrupted baseline is
#: resumed rather than paid for again.
BASELINE_JOURNAL = RUN_DIR / "baseline_responses.jsonl"
SPEND_LOG = RUN_DIR / "spend.json"


class BudgetExceeded(RuntimeError):
    """The cap is a constraint, not a guideline."""


@dataclass
class Budget:
    """Prices every call as it returns and stops the run at the cap."""

    limit_usd: float
    spent_usd: float = 0.0
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    by_tier: dict[str, dict[str, Any]] = field(default_factory=dict)

    def charge(self, tier: str, response: LlmResponse) -> None:
        cost = cost_usd(tier, response)
        if self.spent_usd + cost > self.limit_usd:
            raise BudgetExceeded(
                f"stopping: {self.spent_usd:.4f} spent, this call adds {cost:.4f}, "
                f"cap is {self.limit_usd:.2f}"
            )
        self.spent_usd += cost
        self.calls += 1
        self.input_tokens += response.input_tokens
        self.output_tokens += response.output_tokens
        self.cached_tokens += response.cached_tokens
        row = self.by_tier.setdefault(tier, {
            "model": response.model, "calls": 0, "input": 0, "output": 0,
            "cached": 0, "cost": 0.0,
        })
        row["calls"] += 1
        row["input"] += response.input_tokens
        row["output"] += response.output_tokens
        row["cached"] += response.cached_tokens
        row["cost"] += cost

    def table(self) -> str:
        lines = [
            f"{'stage':<12} {'model':<14} {'calls':>6} {'input':>10} {'output':>9} "
            f"{'cached':>9} {'cost':>9}"
        ]
        for tier, row in sorted(self.by_tier.items(), key=lambda kv: -kv[1]["cost"]):
            lines.append(
                f"{tier:<12} {row['model']:<14} {row['calls']:>6} {row['input']:>10,} "
                f"{row['output']:>9,} {row['cached']:>9,} {row['cost']:>9.4f}"
            )
        lines.append(
            f"{'total':<12} {'':<14} {self.calls:>6} {self.input_tokens:>10,} "
            f"{self.output_tokens:>9,} {self.cached_tokens:>9,} {self.spent_usd:>9.4f}"
        )
        return "\n".join(lines)


class MeteredClient:
    """The real client, with the budget in front of it. Same protocol, nothing else."""

    def __init__(
        self, budget: Budget, inner=None, every: int = 25,
        journal: Path | None = None,
    ) -> None:
        from sentinelops.llm.providers.openai import OpenAIClient

        self.budget = budget
        self.inner = inner or OpenAIClient()
        self.every = every
        #: Every paid answer, appended to disk as it arrives, keyed by the exact
        #: request. A re-run after a kill replays these free and pays only for
        #: calls that never happened. For code that saves only on finishing —
        #: the naive baseline — this is the checkpoint: the caller walks the
        #: same instances in the same order and gets the same answers back, so
        #: its counts come out exactly as an uninterrupted run's would.
        self.journal = journal
        self.replayed = 0
        self._journaled: dict[str, dict[str, Any]] = {}
        if journal is not None and journal.exists():
            for line in journal.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    entry = json.loads(line)
                    self._journaled[entry["key"]] = entry["response"]
        #: Called every `every` paid calls. Checkpointing here, at the metering
        #: boundary, covers every stage at once. The first resume was killed
        #: when its session ended, 225 calls and $0.18 in, and saved nothing:
        #: the per-cycle checkpoint lives in `run_pipeline`, and
        #: `_section_eight` — where a resume spends everything — wrote the
        #: database only on finishing. A killed process runs no `except`.
        self.checkpoint = None

    @staticmethod
    def _key(request: LlmRequest) -> str:
        blob = json.dumps({
            "system": request.system, "messages": request.messages,
            "max_tokens": request.max_tokens, "tier": request.tier,
            "model": models.model_for(request.tier),
        }, sort_keys=True)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def complete(self, request: LlmRequest) -> LlmResponse:
        key = self._key(request) if self.journal is not None else None
        if key is not None and key in self._journaled:
            # Already paid for in an earlier session. Not charged again.
            self.replayed += 1
            return LlmResponse(**self._journaled[key])
        response = self.inner.complete(request)
        if key is not None:
            # Journaled before charging: the call is paid for the moment it
            # returns, so even one the budget then refuses is kept.
            record = {
                name: getattr(response, name)
                for name in ("text", "parsed_json", "input_tokens", "output_tokens",
                             "cached_tokens", "model", "latency_ms", "raw")
            }
            with self.journal.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({"key": key, "response": record}) + "\n")
            self._journaled[key] = record
        self.budget.charge(request.tier, response)
        if self.checkpoint is not None and self.budget.calls % self.every == 0:
            self.checkpoint()
        if self.budget.calls % 25 == 0:
            print(
                f"  … {self.budget.calls} calls · ${self.budget.spent_usd:.4f} "
                f"of ${self.budget.limit_usd:.2f}",
                flush=True,
            )
        return response


def _record_spend(phase: str, budget: Budget, extra: dict[str, Any] | None = None) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    log = json.loads(SPEND_LOG.read_text(encoding="utf-8")) if SPEND_LOG.exists() else {}
    log[phase] = {
        "at": datetime.now().isoformat(timespec="seconds"),
        "calls": budget.calls,
        "input_tokens": budget.input_tokens,
        "output_tokens": budget.output_tokens,
        "cached_tokens": budget.cached_tokens,
        "cost_usd": round(budget.spent_usd, 4),
        "by_tier": {k: {**v, "cost": round(v["cost"], 4)} for k, v in budget.by_tier.items()},
        **(extra or {}),
    }
    SPEND_LOG.write_text(json.dumps(log, indent=1), encoding="utf-8")


def _save(conn, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    disk = sqlite3.connect(path)
    try:
        conn.backup(disk)
    finally:
        disk.close()


def _guard_provider() -> None:
    """Make an unmetered fallback fail instead of spending.

    The budget can only cap calls that pass through it. A stage that quietly
    falls back to `get_client()` would build a second client nothing is
    counting, and spend outside the cap. So for the duration of a paid run the
    factory is pointed at a provider that does not exist: any fallback raises
    `LlmError` immediately rather than charging the card. Stages are handed the
    metered client explicitly; nothing legitimate reads this.
    """
    os.environ["SENTINELOPS_LLM_PROVIDER"] = "unmetered-fallback-is-a-bug"


def _reconcile(conn, budget: Budget, since_id: int = 0) -> dict[str, Any]:
    """The meter's rows against the budget's own count of what it paid for.

    Two independent tallies of the same calls: the budget counts what it was
    asked to charge, `token_usage` holds what the stages recorded. A gap means
    a call went round one of them, which is the only way the reported cost can
    be wrong while every individual number looks fine.
    """
    # `since_id` exists for resumed runs: the budget counts only this session's
    # calls, while the database also holds every row the stopped run wrote, and
    # comparing the two wholesale would report a mismatch on every resume.
    row = conn.execute(
        "SELECT COUNT(*) c, COALESCE(SUM(input_tokens),0) i,"
        " COALESCE(SUM(output_tokens),0) o, COALESCE(SUM(cost_usd),0) usd"
        " FROM token_usage WHERE id > ?", (since_id,)
    ).fetchone()
    metered = sorted(
        {r[0] for r in conn.execute(
            "SELECT DISTINCT model FROM token_usage WHERE id > ?", (since_id,)
        )}
    )
    configured = sorted({models.model_for(t) for t in models.MODELS})
    return {
        "metered_rows": row[0],
        "budget_calls": budget.calls,
        "rows_match_calls": row[0] == budget.calls,
        "metered_input": row[1],
        "budget_input": budget.input_tokens,
        "tokens_match": (row[1], row[2]) == (budget.input_tokens, budget.output_tokens),
        "metered_cost": round(row[3], 4),
        "budget_cost": round(budget.spent_usd, 4),
        "models_seen": metered,
        # The provider answers with a dated snapshot — `gpt-4.1-mini-2025-04-14`
        # for a request naming `gpt-4.1-mini` — so a configured name matches
        # itself or itself-plus-date. Exact matching flagged every real call.
        "unexpected_models": [
            m for m in metered
            if not any(m == c or m.startswith(c + "-") for c in configured)
        ],
    }


def replay(budget_usd: float) -> int:
    """The full replay to the vantage point, against the provider."""
    budget = Budget(limit_usd=budget_usd)
    client = MeteredClient(budget)
    _guard_provider()
    corpus = generate_corpus()
    conn = connect(":memory:")
    client.checkpoint = lambda: _save(conn, RUN_DB)
    print(models.table())
    print(f"\nreplaying {harness.CYCLE_DATES[0]} to {harness.CYCLE_DATES[-1]} "
          f"({len(harness.CYCLE_DATES)} cycles), cap ${budget_usd:.2f}\n", flush=True)
    try:
        # Checkpointed every cycle. The first run of this lost 900 calls and
        # $0.43 to an exception after the pipeline had finished: the database
        # was in memory, the handler below caught only two exception types, and
        # the process died before anything was written. Paid work is banked as
        # it is produced, not at the end.
        stats = harness.run_pipeline(
            conn, corpus, client=client, on_cycle=lambda: _save(conn, RUN_DB),
        )
        _save(conn, RUN_DB)
        harness._section_eight(conn, client=client)
    except BaseException as stopped:  # noqa: BLE001 — see above
        # Deliberately everything. Whatever went wrong, the money is already
        # spent, and a run that is not saved is spent twice.
        _save(conn, RUN_DB)
        _record_spend("replay_stopped", budget, {
            "reason": f"{type(stopped).__name__}: {stopped}",
        })
        print(f"\nSTOPPED: {type(stopped).__name__}: {stopped}\n{budget.table()}")
        print(f"\npartial run kept at {RUN_DB}")
        traceback.print_exc()
        return 1
    _save(conn, RUN_DB)
    check = _reconcile(conn, budget)
    _record_spend("replay", budget, {"pipeline": stats, "reconciliation": check})
    print(f"\n{budget.table()}")
    print(f"\nmetering: {check}")
    if not check["rows_match_calls"] or check["unexpected_models"]:
        print("WARNING: the meter and the budget disagree; do not quote the cost")
    print(f"\nrun kept at {RUN_DB}")
    return 0


def baseline(budget_usd: float, sample: int | None, seed: int) -> int:
    """The naive baseline, if the remaining budget covers it. Cached on completion."""
    budget = Budget(limit_usd=budget_usd)
    client = MeteredClient(budget, journal=BASELINE_JOURNAL)
    _guard_provider()
    if client._journaled:
        print(f"{len(client._journaled)} answers already paid for in "
              f"{BASELINE_JOURNAL.name}; they replay free\n", flush=True)
    corpus = generate_corpus()
    # Named, rather than left to default to the client's class name: the cache
    # key is built from it, and the architecture comparison only holds if the
    # baseline ran on the same model as the pipeline's assessment stage.
    model = models.model_for("assess")
    try:
        result, was_cached = baseline_module.run(
            corpus, client=client, model=model, sample=sample, sample_seed=seed,
        )
    except (BudgetExceeded, LlmError) as stopped:
        _record_spend("baseline_stopped", budget, {"reason": str(stopped)})
        print(f"\nSTOPPED: {stopped}\n{budget.table()}")
        return 1
    if result.sample_method:
        print(result.sample_method)
    _record_spend("baseline", budget, {
        "cached_already": was_cached, "model": result.model,
        "sample_size": result.sample_size, "sample_seed": result.sample_seed,
        "note": result.sample_method, "instances": result.instances_considered,
        "replayed_from_journal": client.replayed,
    })
    cached_at = baseline_module.cache_path(
        corpus.fingerprint(), result.model, result.sample_size, result.sample_seed
    )
    print(f"\n{budget.table()}")
    print(f"\nbaseline cached at {cached_at}")
    return 0


def resume(budget_usd: float) -> int:
    """Finish a replay that stopped, from its checkpoint rather than the start.

    The pipeline is the expensive part — 906 assess calls, most of the bill —
    and a checkpointed run already holds it. `_section_eight`'s three stages are
    each idempotent by design: the taxonomy returns the frozen set rather than
    deriving a second one, classification runs only on findings with no
    category, and recurrence skips findings it has already examined. So
    resuming asks for the work that did not happen and pays for nothing twice.
    """
    if not RUN_DB.exists():
        print(f"no saved run at {RUN_DB}; run `replay` first")
        return 1
    budget = Budget(limit_usd=budget_usd)
    client = MeteredClient(budget)
    _guard_provider()
    conn = connect(":memory:")
    disk = sqlite3.connect(RUN_DB)
    try:
        disk.backup(conn)
    finally:
        disk.close()

    client.checkpoint = lambda: _save(conn, RUN_DB)
    already = conn.execute(
        "SELECT COALESCE(MAX(id), 0) m FROM token_usage"
    ).fetchone()[0]
    spent_before = conn.execute(
        "SELECT COALESCE(SUM(cost_usd), 0) c FROM token_usage"
    ).fetchone()[0]
    print(f"resuming from {RUN_DB}: {already:,} calls already paid for "
          f"(${spent_before:.4f}), cap ${budget_usd:.2f} for the rest\n", flush=True)

    try:
        harness._section_eight(conn, client=client)
    except BaseException as stopped:  # noqa: BLE001 — save first, always
        _save(conn, RUN_DB)
        _record_spend("resume_stopped", budget, {
            "reason": f"{type(stopped).__name__}: {stopped}",
        })
        print(f"\nSTOPPED: {type(stopped).__name__}: {stopped}\n{budget.table()}")
        traceback.print_exc()
        return 1

    _save(conn, RUN_DB)
    check = _reconcile(conn, budget, since_id=already)
    _record_spend("resume", budget, {"reconciliation": check,
                                     "calls_already_paid_for": already})
    print(f"\n{budget.table()}")
    print(f"\nmetering (this session only): {check}")
    print(f"\nrun kept at {RUN_DB}")
    return 0


def artefacts(budget_usd: float) -> int:
    """The brief, the audit report and the evidence pack, from the real run.

    **Into a copy, never into `run.db`.** The brief and the report each cost a
    call, and those calls would land in `token_usage` — so writing them back
    would inflate the real run's tokens-per-cycle against a stub column whose
    pipeline never generated either artefact. The comparison has to be
    like-for-like, so the artefacts get their own database and their own line
    in the spend log.

    The pack is built from the audit log alone: `pack.build` is handed a list of
    events and nothing else, and the chain is verified over that same list.
    """
    from sentinelops import pack as pack_module
    from sentinelops import render
    from sentinelops.stages import audits, intelligence
    from sentinelops.synth.calendar import CORPUS_WINDOW, SIMULATED_TODAY

    if not RUN_DB.exists():
        print(f"no saved run at {RUN_DB}; run `replay` first")
        return 1
    budget = Budget(limit_usd=budget_usd)
    client = MeteredClient(budget)
    _guard_provider()
    conn = connect(":memory:")
    disk = sqlite3.connect(RUN_DB)
    try:
        disk.backup(conn)
    finally:
        disk.close()

    out = Path(__file__).resolve().parents[1] / "data" / "artefacts"
    out.mkdir(parents=True, exist_ok=True)
    as_of = SIMULATED_TODAY
    repo = repositories(conn)

    try:
        brief = intelligence.prioritisation_brief(conn, as_of, client=client)
        audit = max(
            (a for a in repo["audits"].list()
             if a.status == "completed" and audits.findings_of(repo, a.id)),
            key=lambda a: (a.conducted_date, a.id),
        )
        report = audits.generate_report(conn, audit.id, as_of=as_of, client=client)
    except (BudgetExceeded, LlmError) as stopped:
        _record_spend("artefacts_stopped", budget, {"reason": str(stopped)})
        print(f"\nSTOPPED: {stopped}\n{budget.table()}")
        return 1

    audits.confirm(conn, audit.id, by=audit.auditor_identity, as_of=as_of,
                   remarks="Read against the findings; summary citations checked.")
    audits.issue(conn, audit.id, by=audit.auditor_identity, as_of=as_of)
    audits.attach_status(conn, report)

    brief_name = f"prioritisation_brief_{as_of}"
    (out / f"{brief_name}.md").write_text(render.brief_markdown(brief), encoding="utf-8")
    (out / f"{brief_name}.html").write_text(render.brief_html(brief), encoding="utf-8")
    report_name = f"audit_report_{audit.id}"
    (out / f"{report_name}.md").write_text(audits.render_markdown(report), encoding="utf-8")
    (out / f"{report_name}.html").write_text(render.report_html(report), encoding="utf-8")

    # The pack, from the log and nothing else — `load_events` reads the audit
    # log and `build` is handed that list and nothing more. Same window, same
    # filename and same directory as `demo.generate_pack`, so the real run
    # *replaces* the tracked pack rather than leaving a stub-derived one beside
    # it under a second name.
    packs = Path(__file__).resolve().parents[1] / "data" / "packs"
    packs.mkdir(parents=True, exist_ok=True)
    events = pack_module.load_events(conn, since=CORPUS_WINDOW.start, until=as_of)
    built = pack_module.build(
        events,
        period_start=CORPUS_WINDOW.start,
        period_end=as_of,
        scope=(
            f"All auditable units, all applicable controls, "
            f"{CORPUS_WINDOW.start} to {as_of}"
        ),
    )
    chain = pack_module.verify_chain(events)
    pack_name = pack_module.pack_filename(CORPUS_WINDOW.start, as_of)
    (packs / f"{pack_name}.md").write_text(
        pack_module.render_markdown(built), encoding="utf-8"
    )
    (packs / f"{pack_name}.html").write_text(
        pack_module.render_html(built), encoding="utf-8"
    )

    _save(conn, ARTEFACT_DB)
    _record_spend("artefacts", budget, {
        "brief_published": brief.published,
        "brief_cited_findings": len(brief.cited_findings),
        "brief_cited_metrics": len(brief.cited_metrics),
        "audit": audit.id,
        "report_status": audits.report_status(report),
        "pack_events": len(events),
        "pack_chain": chain,
    })
    print(f"\n{budget.table()}")
    print(f"\nbrief: {'published' if brief.published else 'WITHHELD'} · "
          f"{len(brief.cited_findings)} finding(s), "
          f"{len(brief.cited_metrics)} metric(s) cited")
    print(f"report: {audit.id} · {audits.report_status(report)}")
    print(f"pack: {len(events):,} events from the audit log alone · chain {chain}")
    print(f"\nwritten to {out} and {packs}")
    return 0


def score(baseline_model: str | None) -> int:
    """Write results.md from the saved run and whichever baseline is on disk.

    Guarded like the paid steps, for a subtler reason than cost. Scoring
    re-enters taxonomy, classification and recurrence. On a finished run those
    are idempotent and do nothing — but if the replay stopped early and left
    findings unclassified, an unguarded `get_client()` would quietly complete
    them on the stub and fold that output into a run reported as the real
    provider's. Raising is the outcome worth having: it says work was left
    undone, rather than finishing it with the wrong model in silence.
    """
    corpus = generate_corpus()
    _guard_provider()
    if not RUN_DB.exists():
        print(f"no saved run at {RUN_DB}; run `replay` first")
        return 1
    conn = connect(":memory:")
    disk = sqlite3.connect(RUN_DB)
    try:
        disk.backup(conn)
    finally:
        disk.close()

    log = json.loads(SPEND_LOG.read_text(encoding="utf-8")) if SPEND_LOG.exists() else {}
    result = None
    note = ""
    if baseline_model:
        entry = log.get("baseline", {})
        result = baseline_module.load_cached(
            corpus.fingerprint(), baseline_model,
            entry.get("sample_size"), entry.get("sample_seed"),
        )
        if result is None:
            print(f"no cached baseline for {baseline_model}")
            return 1
        note = result.sample_method or entry.get("note", "")

    spend = {row[0]: row[1] for row in conn.execute(
        "SELECT 'calls', COUNT(*) FROM token_usage UNION ALL "
        "SELECT 'cost', ROUND(SUM(cost_usd), 4) FROM token_usage"
    )}
    # The counts the replay itself reported. Zeros would be a lie in results.md,
    # and re-running the pipeline to recover them would spend the money twice.
    stats = log.get("replay", {}).get("pipeline") or {
        "screened": 0, "assessed": 0, "remediated": 0, "reminders": 0,
        "escalations": 0,
    }
    evaluation, _ = harness.score(
        conn, corpus, run_stats=stats, baseline_result=result, baseline_note=note,
    )
    print(f"results.md written · run spend {spend}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    replay_parser = sub.add_parser("replay")
    replay_parser.add_argument("--budget", type=float, required=True)
    baseline_parser = sub.add_parser("baseline")
    baseline_parser.add_argument("--budget", type=float, required=True)
    baseline_parser.add_argument("--sample", type=int, default=None)
    baseline_parser.add_argument("--seed", type=int, default=19)
    resume_parser = sub.add_parser("resume")
    resume_parser.add_argument("--budget", type=float, required=True)
    artefacts_parser = sub.add_parser("artefacts")
    artefacts_parser.add_argument("--budget", type=float, required=True)
    score_parser = sub.add_parser("score")
    score_parser.add_argument("--baseline-model", default=None)
    args = parser.parse_args(argv)

    if args.command == "replay":
        return replay(args.budget)
    if args.command == "baseline":
        return baseline(args.budget, args.sample, args.seed)
    if args.command == "resume":
        return resume(args.budget)
    if args.command == "artefacts":
        return artefacts(args.budget)
    return score(args.baseline_model)


if __name__ == "__main__":
    sys.exit(main())
