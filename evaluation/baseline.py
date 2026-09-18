"""The naive baseline — built to be *beaten fairly*, not to lose.

A reviewer's first question about any efficiency claim is what the comparison
was against, and the answer has to be "a reasonable implementation" rather than
"the worst thing we could think of". So this baseline does the two obvious
things any competent engineer would do on day one:

  * it does not call a model for an instance with no evidence — there is
    nothing to read, and paying to be told so would be silly;
  * it caches by document hash, so the same document submitted twice is
    assessed once.

And it does not do the three things this project argues are the point:

  * no applicability rules — without them you cannot know which controls apply
    where, so every control is considered for every area;
  * no pre-screen — wrong-type, stale and structured evidence all go to the
    model, because without the rules there is nothing to catch them;
  * no retrieval — the whole document goes in, every time.

Everything else is held constant on purpose. Same model, same system prompt,
same user template, same schema, same max_tokens. The only variables are the
three above, so the difference in tokens is attributable to architecture rather
than to prompt-wrangling. Giving the baseline a worse prompt would produce a
better-looking number and a worthless one.

Results are cached to disk on first run and never recomputed: this is the only
part of the project that costs real money twice if you are careless with it.
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from sentinelops.llm import get_client
from sentinelops.llm.parsing import extract_json, validate
from sentinelops.llm.prompts.assessment import (
    ASSESSMENT_SYSTEM_V2,
    PROMPT_VERSION,
    assessment_schema_v2,
    assessment_user_v2,
)
from sentinelops.llm.protocol import LlmError, LlmRequest
from sentinelops.periods import periods_for

CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "baseline"


@dataclass
class BaselineResult:
    """What the naive path cost and concluded."""

    corpus_fingerprint: str
    model: str
    prompt_version: str
    instances_considered: int = 0
    skipped_no_evidence: int = 0
    served_from_document_cache: int = 0
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    characters_sent: int = 0
    wall_seconds: float = 0.0
    # Set only when the budget would not cover the whole baseline. Recorded on
    # the result, in the cache key and in results.md, because a sampled figure
    # and a full one are not the same measurement.
    sample_size: int | None = None
    sample_seed: int | None = None
    sample_method: str = ""
    verdicts: dict[str, str] = field(default_factory=dict)
    failures: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def cache_path(
    fingerprint: str, model: str, sample: int | None = None,
    sample_seed: int | None = None,
) -> Path:
    """Where this run's result lives.

    The sample is part of the key. Without it a sampled run would be served
    later to a caller asking for the full baseline, which is the quietest way
    to publish a partial measurement as a complete one.
    """
    suffix = "" if not sample else f"|sample={sample}@{sample_seed}"
    key = hashlib.sha256(f"{fingerprint}|{model}|{PROMPT_VERSION}{suffix}".encode())
    return CACHE_DIR / f"baseline_{key.hexdigest()[:16]}.json"


def load_cached(
    fingerprint: str, model: str, sample: int | None = None,
    sample_seed: int | None = None,
) -> BaselineResult | None:
    path = cache_path(fingerprint, model, sample, sample_seed)
    if not path.exists():
        return None
    return BaselineResult(**json.loads(path.read_text(encoding="utf-8")))


def save(result: BaselineResult) -> Path:
    path = cache_path(
        result.corpus_fingerprint, result.model, result.sample_size,
        result.sample_seed,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    return path


def instance_key(control_id: str, area_id: str, period: str) -> str:
    """Matches the pipeline's own id scheme so results can be compared row for row."""
    return (
        f"CHK-{control_id.removeprefix('CTRL-')}-"
        f"{area_id.removeprefix('AREA-')}-{period}"
    )


def _select(
    corpus, sample: int | None, sample_seed: int
) -> set[tuple[str, str, str]] | None:
    """Which (control, unit, period) instances this run will walk.

    `None` means all of them, which is the only honest default. A sample is
    drawn over the *whole* considered population, the no-evidence instances
    included, so a sampled run stays a scale model of the full one rather than
    a run over a different, evidence-richer corpus — the skip rate is part of
    what the baseline is measuring.
    """
    if sample is None:
        return None
    instances = [
        (control.id, area.id, period.label)
        for control in sorted(corpus.controls, key=lambda c: c.id)
        for area in sorted(corpus.areas, key=lambda a: a.id)
        for period in periods_for(
            control.frequency, corpus.year, corpus.through,
            last_month=corpus.last_month,
        )
    ]
    if sample >= len(instances):
        return None  # a sample of everything is not a sample
    return set(random.Random(sample_seed).sample(instances, sample))


def run(
    corpus,
    *,
    client=None,
    year: int = 2026,
    force: bool = False,
    model: str | None = None,
    sample: int | None = None,
    sample_seed: int = 19,
) -> tuple[BaselineResult, bool]:
    """Run the naive path once, or return what it cost last time.

    Returns (result, was_cached). The cache key covers the corpus fingerprint,
    the model, the prompt version and the sample, so a changed corpus
    recomputes, an unchanged one never does, and a sampled run is never handed
    back to a caller that asked for the whole thing.

    `sample` exists for one reason: a budget that will not cover the full
    baseline. It is recorded on the result and reported in `results.md`.
    """
    client = client or get_client()
    model = model or type(client).__name__
    selected = _select(corpus, sample, sample_seed)
    drawn = len(selected) if selected is not None else None

    if not force:
        cached = load_cached(corpus.fingerprint(), model, drawn, sample_seed)
        if cached is not None:
            return cached, True

    result = BaselineResult(
        corpus_fingerprint=corpus.fingerprint(),
        model=model,
        prompt_version=PROMPT_VERSION,
    )
    if selected is not None:
        result.sample_size = drawn
        result.sample_seed = sample_seed
        result.sample_method = (
            f"Run on a random sample of {drawn} of the (control, unit, period) "
            f"instances the naive path would consider, drawn without replacement "
            f"by `random.Random({sample_seed}).sample` over the instance list in "
            f"sorted order, because the remaining budget would not cover the "
            f"whole baseline. Its token and cost figures are for the sample, not "
            f"the full run."
        )
    schema = assessment_schema_v2()
    submissions = {
        (s.control_id, s.auditable_unit_id, s.period): s
        for s in corpus.submissions
        if not s.is_remediation
    }
    by_document: dict[str, dict[str, Any]] = {}
    started = time.perf_counter()

    # No applicability: every control is considered against every area.
    for control in sorted(corpus.controls, key=lambda c: c.id):
        for area in sorted(corpus.areas, key=lambda a: a.id):
            for period in periods_for(
                control.frequency, corpus.year, corpus.through,
                last_month=corpus.last_month,
            ):
                if selected is not None and (
                    control.id, area.id, period.label
                ) not in selected:
                    continue
                result.instances_considered += 1
                submission = submissions.get((control.id, area.id, period.label))
                if submission is None:
                    result.skipped_no_evidence += 1
                    continue

                key = instance_key(control.id, area.id, period.label)
                # Competent move one: the same document is assessed once.
                cache_key = f"{control.id}|{submission.content_hash}"
                if cache_key in by_document:
                    result.served_from_document_cache += 1
                    result.verdicts[key] = by_document[cache_key]["verdict"]
                    continue

                # No retrieval: the whole document, plus the whole criteria.
                request = LlmRequest(
                    system=ASSESSMENT_SYSTEM_V2,
                    messages=[
                        {
                            "role": "user",
                            "content": assessment_user_v2(
                                control.title, control.criteria_text,
                                [submission.content],
                            ),
                        }
                    ],
                    max_tokens=700,
                    response_schema=schema,
                    tier="assess",
                )
                result.characters_sent += len(request.messages[0]["content"])
                try:
                    response = client.complete(request)
                    payload = response.parsed_json or extract_json(response.text)
                    validate(payload, schema)
                except LlmError:
                    result.failures += 1
                    continue

                result.model_calls += 1
                result.input_tokens += response.input_tokens
                result.output_tokens += response.output_tokens
                result.cached_tokens += response.cached_tokens
                by_document[cache_key] = payload
                result.verdicts[key] = payload["verdict"]

    result.wall_seconds = round(time.perf_counter() - started, 2)
    save(result)
    return result, False
