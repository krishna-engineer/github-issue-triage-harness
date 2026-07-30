# GitHub Issue Triage — service + evaluation harness

A small LLM service that triages a GitHub issue, and an evaluation harness for
deciding whether a change to it is an improvement.

The harness is the point. The service exists to give it something to measure.

**[▶ 5-minute video walkthrough of the eval results](https://drive.google.com/file/d/1xiQlFmjgxW4OnE1SJ6t6LyQU-Xr5LfiG/view?usp=sharing)**
--- 

## Start here — how I worked

The brief asks to see the reasoning, not a polished write-up. These are the
working notes, roughly in the order they were written:

| | |
|---|---|
| [`my_approach.md`](my_approach.md) | How I approached the problem end to end — what I did in what order, what I found mid-build that I did not expect, and what I cut |
| [`brain_storming.md`](brain_storming.md) | Working through the metrics. Most of the thinking time went here: why a single accuracy number is not enough, why run-to-run noise breaks naive comparison, and how the cost matrix came out of it |
| [`design_decisions.md`](design_decisions.md) | Each decision with its reasoning and the trade-off accepted — e.g. no HTTP API for the core service, harness reports rather than gates, weights in config rather than code |

`brain_storming.md` is the one to read if you only read one. The metrics
reasoning is what the rest of the project is built on.

---

## Quickstart

Requires **Python 3.11+**. On macOS the system `python3` is 3.9, which will fail — the OpenAI SDK itself needs 3.10+.

```bash
git clone https://github.com/krishna-engineer/github-issue-triage-harness.git
cd github-issue-triage-harness

# no 3.11?  brew install python@3.11
python3.11 -m venv .venv      
source .venv/bin/activate
pip install --upgrade pip     
pip install -e .
```

### See the results — no API key needed

Two real runs are committed under `runs/`, so every scoring and
comparison command works offline.

```bash
harness score   runs/gpt-4o-mini.jsonl
harness compare runs/gpt-4o-mini.jsonl runs/gpt-5-nano.jsonl
```

### Produce a new run — needs `OPENAI_API_KEY`, costs well under $0.01

```bash
cp .env.example .env      # add your key
harness run my-label
```

---

## What's here

```
├── data/
│   └── golden_set.jsonl          20 real GitHub issues from 5 public repos,
│                                 human-reviewed labels + reasoning per row
├── runs/
│   ├── gpt-4o-mini.jsonl         committed run artifacts — 40 results each,
│   ├── gpt-4o-mini.manifest.json  so score/compare run with NO API key
│   ├── gpt-5-nano.jsonl
│   └── gpt-5-nano.manifest.json
├── src/
│   ├── triage/                   the service
│   │   ├── schema.py             enums + request/response contract
│   │   ├── llm_client.py         the only file that touches the network
│   │   ├── core.py               title+body → triage decision + metadata
│   │   └── prompts/v1.txt        prompts are versioned files, not inline strings
│   └── harness/                  the harness
│       ├── config.py             RUN_CONFIG (engineering) + WEIGHTS (policy)
│       ├── core_service_runner.py   `run`     — makes the calls, writes results
│       ├── score_single_run.py      `score`   — one run, absolute numbers
│       ├── compare_two_runs.py      `compare` — two runs, relative numbers
│       └── cli.py                single entry point for all three
├── tests/                        offline tests — no API key, no spend
├── my_approach.md                how I worked
├── brain_storming.md             the metrics reasoning
├── design_decisions.md           decisions + trade-offs accepted
├── LABELING_RUBRIC.md            rules the golden set was labelled against
└── pyproject.toml                deps + the `harness` console script
```

