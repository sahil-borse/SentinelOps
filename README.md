# SentinelOps

Compliance checks that cannot be forgotten, judged the same way in every process
area, with the audit trail written as it happens rather than assembled afterwards.

## Running the dashboard

```
pip install -e ".[dev,ui]"
streamlit run src/sentinelops/ui/app.py
```

Everything else is done from the screen: advance the calendar, run a cycle,
upload evidence, re-assess a check, generate the audit pack, verify the audit
chain. The demo seeds itself on first open and keeps its state in
`data/demo/sentinelops.db`; **Reset demo** starts over.

## The other entry points

```
python -m sentinelops.synth              # regenerate the corpus and truth file
python -m evaluation                     # run both pipelines, write results.md
python -m sentinelops.demo.generate_pack # build the audit pack for the year
python -m pytest                         # the suite
```

## What is here

| | |
|---|---|
| `src/sentinelops/stages/` | S0 applicability, S1 trigger, S2 pre-screen, S3 assess, S4 flag, and the remediation loop |
| `src/sentinelops/llm/` | The provider boundary. No SDK type crosses out of it. |
| `src/sentinelops/synth/` | The seeded synthetic corpus and its ground truth |
| `src/sentinelops/pack.py` | The audit evidence pack, built from the log alone |
| `src/sentinelops/ui/` | The dashboard |
| `evaluation/` | The harness — outside the package, because it reads the answers |
| `results.md` | The measured outcomes, with every figure scoped |

## Reading the numbers

`results.md` carries its own caveats and they are not decoration. The corpus is
synthetic with constructed failure modes; the manual comparison is a simulation
whose assumptions are printed alongside it; and unless a real provider was
configured, the accuracy figures describe `FakeModelClient` rather than a
language model. Run with `SENTINELOPS_LLM_PROVIDER=openai` and an
`OPENAI_API_KEY` in `.env` before quoting any absolute accuracy number.
