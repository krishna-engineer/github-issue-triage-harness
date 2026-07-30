# How I approached the problem

- Wrote problem statement with pen and paper as it helps me giving a complete and visual view of the problem and context around it.

[Problem understanding, page 1](docs/getting_started_1.jpeg)

[Problem understanding, page 2](docs/getting_started_2.jpeg)

[Problem understanding, page 3](docs/getting_started_3.jpeg)

- After that, I went to meat of the problem statement: metrics to calculate. Building service was surely an easy work than brainstorming on metrics part. I took around 30% of time in deciding metrics and how to measure them.

- Then I started with building LLM core service:
  - Noted down various design decisions for it before starting actual code.
  - First wrote `schema.py` as it becomes a contract of request and response body
  - Completed writing code that makes call to llm, tested it
  - Wrote `core.py` which is LLM service flow end-to-end. Tested it too.

- Next was coming with golden dataset on which harness can be run.
  - I made use of AI to get `{title, body}` from git issues url

- On building harness part
  - Split it into 3 separate commands: `run`, `score`, `compare`.
  - Because API calls are the expensive part, scoring is free. Hence splitted them.

- What I cut and why
  - `urgency` and `issue_type` scoring - `needs_human` is the field that carries the real point (asymmetric error cost), so I did that one properly instead of all three loosely.

- Also thought about the person who will actually run this project
  - Made a single `harness` command with 3 subcommands (`run`, `score`, `compare`) instead of three separate `python -m` calls.
  - **VVIMP:** `score` and `compare` need NO API key. Only `run` costs money. So I committed two real runs under `runs/examples/`.
  - Reason for doing this: if someone has to first set up a key and pay for calls before seeing any output, most people will just read the code and move on.