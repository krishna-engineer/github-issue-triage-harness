from triage.core import triage_core
from triage.schema import GitIssue

issue = GitIssue(issue_id="1", title="App crashes on login", body="500 for all users")
triage_resp = triage_core(issue=issue, model="gpt-5-nano", prompt_version="v1", output_mode="prompt_only")

print(triage_resp.model_dump_json(indent=2))


"""
OUTPUT RECEIVED:

{
  "issue_id": "1",
  "decision": {
    "issue_type": "bug",
    "urgency": "critical",
    "needs_human": true,
    "rationale": null
  },
  "raw_llm_response": "{\"issue_type\":\"bug\",\"urgency\":\"critical\",\"needs_human\":true}",
  "usage": {
    "input_tokens": 71,
    "output_tokens": 218
  },
  "latency_ms": 6555.440833006287,
  "finish_reason": "stop",
  "run_config": {
    "model_name": "gpt-5-nano",
    "temperature": 1.0,
    "max_completion_tokens": 500,
    "prompt_version": "v1"
  },
  "error_status": "ok",
  "error_msg": null
}
"""