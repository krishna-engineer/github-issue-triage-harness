import json
from collections import Counter
from datetime import datetime, timezone

from triage.core import triage_core
from triage.schema import GitIssue

from .config import RUN_CONFIG


def load_golden_set(path):
    """Reads title+body only, ignores all other fields from gold jsonl """
    with open(path) as f:
        rows = [json.loads(l) for l in f if l.strip()]

    list_issues = []
    for r in rows:
        issue_info = {
            "issue_id": r['id'],
            "title": r.get('title', ""),
            "body": r.get('body', "")
        }
        list_issues.append(issue_info)
    return list_issues

def run(label:str):
    golden_set_path = RUN_CONFIG['golden_set_path']
    list_issues = load_golden_set(golden_set_path)
    list_git_issues = [GitIssue(issue_id=issue['issue_id'], title=issue['title'], body=issue['body'])
                    for issue in list_issues]

    count_of_core_service_calls = len(list_issues) * RUN_CONFIG['num_runs']

    # current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M")
    # run_id = f"{current_time}_{label or RUN_CONFIG['prompt_version']}"

    run_id = label

    runs_dir = RUN_CONFIG['runs_dir']

    print(f"{run_id}: {count_of_core_service_calls} core service calls "
            f"[{RUN_CONFIG['model']} / {RUN_CONFIG['prompt_version']} / {RUN_CONFIG['output_mode']}]")


    error_counter = Counter()
    with open(runs_dir / f"{run_id}.jsonl", "w") as out:

        # Three complete passes over the golden set, not three calls per issue:
        # issues 1-20 (run_index 1), then 1-20 again (run_index 2), then again (3).
        for run_index in range(1, RUN_CONFIG["num_runs"] + 1):
            for issue in list_git_issues:
                resp = triage_core(
                        issue=issue,
                        model=RUN_CONFIG["model"],
                        prompt_version=RUN_CONFIG["prompt_version"],
                        output_mode=RUN_CONFIG["output_mode"],
                        temperature=RUN_CONFIG["temperature"],
                        max_completion_tokens=RUN_CONFIG["max_completion_tokens"],
                    )
                record = json.loads(resp.model_dump_json())
                record["run_index"] = run_index
                out.write(json.dumps(record) + "\n")
                out.flush()
                error_counter[resp.error_status.value] += 1

    manifest = {
        "run_id": run_id,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "golden_set_path": str(RUN_CONFIG["golden_set_path"]),
        "num_issues": len(list_git_issues),
        "num_runs": RUN_CONFIG["num_runs"],
        "run_config": {k: RUN_CONFIG[k] for k in
                        ("model", "prompt_version", "output_mode",
                        "temperature", "max_completion_tokens", "seed") if k in RUN_CONFIG},
        "counts": {"total": count_of_core_service_calls, **error_counter},
        }

    with open(runs_dir / f"{run_id}.manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

    return runs_dir / f"{run_id}.jsonl"

if __name__ == "__main__":
     import sys
     run(sys.argv[1])


            

