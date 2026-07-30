## How I approached the problem

- Wrote problem statement with pen and paper as it helps me giving a complete and visual view of the problem and context around it.
- After that, I went to meat of the problem statement: metrics to calculate. Building service was surely an easy work than brainstorming on metrics part. I took around 30% of time in deciding metrics and how to measure them.
- Then I started with building LLM core service:
  - Noted down various design decisions for it before starting actual code.
  - First wrote schema.py as it becomes a contract of request and response body
  - Completed writing code that makes call to llm, tested it
  - Wrote core.py which is LLM service flow end-to-end. Tested it too.

## Design Decisions

**1. Harness reports quality, it doesn't decide "go ahead, and ship"**

- Quality is scored against domain expert defined weights (as mentioned in 2nd point below). So "did quality improve" is run same way every time.
- But other metrics like Cost, Latency, Token usage, TTFT would not require domain expert's input.
- Reference point: [artificialanalysis.ai](https://artificialanalysis.ai/) reports quality, price and latency side by side and never names a best model

**2. Missed escalations vs False escalations**

- The harness can't decide "change is better" without getting these input from stakeholders.
- Examples:
  - how much worse is case where an issue gets auto-closed instead of HITL.
  - how much worse is calling an issue as "low" where it in fact should have been "critical"
- Numbers I went ahead with:
  - 10:1 for "needs_human" (cost of 1 Missed HITL is 10x the cost of False HITL)
  - For urgency too, I assumed similar numbers
- Imp:
  - Given these numbers can change, these assumptions live in config file / AWS Parameter store. So changing them requires no deployment.

**3. Retries are not being considered so that true failures surface.**

**4. LLM core service:**

- will accept a list of issues, and as of now it'll be only one entry in that list.
- will be synchronous in nature (i.e. no polling or webhook)
- Error types in case of failure:
  - malformed_json, missing_output_field, invalid_output_type, llm_failure
- Any metric that can change output (say temperature, max_tokens) should be present in service output.
- Output schema (OpenAI offers schema strictness) should be configurable, instead of static value. So that users can know the impact of keeping schema strict vs non-strict.
- API accepts {title, body, context}, not a URL. Because live git issue info can be edited. URL support is deliberately left out for now.
  - Context so that tomorrow if repo details need to be provided, can be stored there
- Not building an API for core service, harness will simply import it.
- I have only implemented OpenAI call, ideally we should use a router like Litellm using which any model can be used without code change