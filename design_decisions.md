# Design Decisions

## 1. Why not use something like DeepEval for harness?

- In our case, outputs (`issue_type`, `usability`, `needs_human`) are not open-ended. Scoring is exact match - deterministic, free, instant.
- If our outputs were open-ended text with no single right answer, I could have tried DeepEval.
- Also adding an LLM judge would result in its own non-determinism.
- Hence I decided to build my own harness for this use-case.

## 2. My harness reports quality, it doesn't decide "go ahead, and ship"

- Quality is scored against domain expert defined weights (as mentioned in 2nd point below). So "did quality improve" is run same way every time.
- But other metrics like Cost, Latency, Token usage, TTFT would not require domain expert's input.
- Reference point: artificialanalysis.ai reports quality, price and latency side by side and never names a best model

## 3. Missed escalations vs False escalations

- The harness can't decide "change is better" without getting these input from stakeholders.
- Examples:
  - how much worse is case where an issue gets auto-closed instead of HITL.
  - how much worse is calling an issue as "low" where it in fact should have been "critical"
- Numbers I went ahead with:
  - 10:1 for `needs_human` (cost of 1 Missed HITL is 10x the cost of False HITL)
  - For `urgency` too, I assumed similar numbers
- **Imp:**
  - Given these numbers can change, these assumptions live in config file / AWS Parameter store. So changing them requires no deployment.

## 4. Retries

Retries are not being considered so that true failures surface.

## 5. LLM core service

- Not building an API for core service, harness will simply import it.
- Service accepts `{title, body, context}`, not a URL. Because live git issue info can be edited. URL support is deliberately left out for now.
- I have only implemented Openai call, ideally we should use a router like Litellm using which any model can be used without code change


## 6. Golden dataset creation

- This was a task which can be handed to An AI agent. But if LLM itself is also writing "gold" value, gold becomes nothing else but what an LLM thinks.
- Also this stage requires creation of "rubric" i.e. written set of rules that says in what situation, label X should be assigned.
- I am writing rubric using LLM, but ideally should be written by domain expert.
- Observation: many real GitHub issues put the answer in the title - https://github.com/agno-agi/agno/issues/9238
  - Hence I am stripping bracketed prefixes and ignore repo labels when building the golden set.
- I've added ~20 issues and there's real variety in them.
  - It was fun to add this one: https://github.com/openai/tiktoken/issues/571

## 7. Harness

- For a single item in golden set, I'm making 3 calls to core service. This is to not be biased because of LLM non-determinism.
  - So, 3 runs × 20 issues = 60 calls per configuration.
- I am splitting core service call for gold set and actual evaluation as 2 steps. Because core service call has costing involved, so it should run once, and results be stored.
- Weights live in `harness/config.py`, not a separate policy file.
- Core service response on golden set => 1 jsonl file
  - `runs/gpt-4o-mini.jsonl` — 40 lines = 2 runs x 20 issues
  - Each line of jsonl = Response from Core service
  - Also I am storing a run manifest file for each jsonl file which describes the run.
  - `runs/gpt-4o-mini.manifest.json`
- N runs per issue means each issue is scored N times. Two ways to aggregate, and I use both for different jobs.
  - Headline metrics (accuracy, cost, latency) score every result **INDEPENDENTLY**. So all 60 lines considered independently.
  - Stability is reported **SEPARATELY**: for each issue, how often did the N runs agree?