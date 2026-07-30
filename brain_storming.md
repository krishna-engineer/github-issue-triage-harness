## Brainstorming

### Topic: "Quality Metrics"

**Thoughts:**

- Let's consider we have golden set of 100 git issues with 3 outputs: "issue_type", "urgency" & "needs_human"

- An aggregated single number comparison is unreliable. Say old prompt giving 85% accuracy and new prompt giving 87%.

  "Can we ship to prod?" => The change in numbers can be due to non-determinism of LLM too. So not confident yet.

- We can get confidence with n runs but that too is not enough to give needed confidence. Why? see below example:
  - Old Prompt Accuracy across 4 runs: [83, 85, 87, 89] => Avg 86
  - New Prompt Accuracy across 4 runs: [84, 87, 88, 91] => Avg 87.5

  "Can we ship to prod?" => 4 runs are helping, but still as owner of a solution, I am not satisfied because Aggregation is still hiding nuances.

- If we do per item comparison (no aggregation), that'll give us better clarity. Say we get to know that:
  - New prompt is fixing 6 cases of Old prompt
  - But new prompt is also failing for 4 cases where old prompt succeeded

  "Can we ship to prod?" => What if 4 cases where new prompt is failing are super important? Say 4 cases are those where gold says "needs_human" as Yes, but new prompt is saying reverse. It's problematic.

- We should focus on metric per output:
  - **"needs_human"**: Binary output : We can consider precision, recall as metrics for it.
  - **"urgency"**:
    - Has 3 output types - critical, normal, low. And they've ordering among them.
    - Example for an issue, gold: "critical", new prompt: "low", old prompt: "normal"
    - Here both prompts are giving wrong results but new prompt is "more wrong" than old prompt.
    - Hence we should track ordinal distance, not just "hit/miss". Say "distance ≥ 2 is a red alert".
    - But Distance alone is not enough, direction here matters too. (gold "critical" -> predicted "low" vs reverse)

- So we can see one common pattern in both above output types: "Missed Escalation (FN) is more critical than False Escalation (FP)"
  - "needs_human": Case which required HITL but flagged as didn't, is more problematic than, one that didn't require but got flagged as required
  - "urgency": Flagging "critical" as "low", is more problematic than, "low" classified as "critical"
  - COST MATRIX is the best structure to handle this case.

- Cost matrix for "urgency" & "needs_human":
  - rows(gold), columns(predicted), each cell(weighted score of how bad that mistake is)
  - In cost matrix, we provide weight to mistakes. So "missed HITL" get 10 as score, while "false HITL" gets 1 as score.
  - It's like saying, cost of 1 Missed HITL is 10x the cost of False HITL

- For "issue_type", there's no ordering, no distance between them. So we can measure "per class accuracy" here.

### Topic: "Other metrics"

**Thoughts:**

- **Cost**
  - model cost changes, it's not static. Also cost changes with change in model and provider (openai vs anthropic)
  - But what's static is token count. So harness will store tokens, and derive cost using a cost file.
  - So if cost changes, we do comparison with updated cost and we'll know the delta
  - We can make use of below cost file which is maintained by open source community:
    https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json

- **Latency**
  - We should report Percentiles here (P80, P90, P95) numbers instead of Avg. Because latency distributions have long trails.
  - latency is impacted by load at provider end, time of the day, etc. So we can't confidently say - "change X increased latency"
  - Hence we shouldn't track numbers like Run_1_old_prompt for 100 issues vs Run_2_new_prompt for 100 issues. Instead, we should do: Issue_1_old_prompt vs Issue_1_new_prompt i.e. per item comparison.

- **Output schema validity**
  - This is the case where output from the service is not usable.
  - example 1: response isn't valid json at all
  - example 2: missing fields
  - example 3: out of box values for fields