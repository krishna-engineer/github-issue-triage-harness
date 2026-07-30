import json
from collections import Counter

from .config import WEIGHTS


def load_gold(path):
    """issue_id -> gold labels. These are the answers the runner never saw."""
    gold = {}
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                gold[r["id"]] = r["labels"]
    return gold


def load_run_results(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def score(results_path, golden_path):
    results = load_run_results(results_path)
    gold = load_gold(golden_path)

    w = WEIGHTS["needs_human"]

    # Splitting usable from unusable. Unusable results are EXCLUDED, not
    # scored as wrong - but excluding them shrinks the denominator, so the
    # count and the reason are both reported.
    scorable = [r for r in results if r["error_status"] == "ok"]
    excluded_by = Counter(r["error_status"] for r in results
                          if r["error_status"] != "ok")

    total_cost = 0
    missed = 0        # gold says a human is needed, we said no  (dangerous)
    false = 0         # we said a human is needed, gold says no  (wasteful)
    correct = 0

    for r in scorable:
        g = gold[r["issue_id"]]["needs_human"]
        p = r["decision"]["needs_human"]
        if g == p:
            correct += 1
        elif g and not p:
            missed += 1
            total_cost += w["missed_escalation"]
        else:
            false += 1
            total_cost += w["false_escalation"]

    n = len(scorable)
    print("----" * 10)

    if n == 0:
        # Every call failed. Say so readably instead of dividing by zero.
        print(f"no usable results ({len(results)} calls, all failed)")
        print(f"  {dict(excluded_by)}")
        print("----" * 10)
        return

    validity = n / len(results)
    print(f"scored {n}/{len(results)} results  (validity {validity:.0%})")
    # Broken down by cause: truncated is a max_tokens problem, malformed_json
    # is a prompt problem, api_failure is neither. Collapsing them into one
    # "excluded" number would point you at the wrong fix.
    for status, count in sorted(excluded_by.items()):
        print(f"  excluded: {status} x{count}")

    print("\nneeds_human (cost matrix):")
    print(f"  missed escalations : {missed}   x{w['missed_escalation']}")
    print(f"  false escalations  : {false}   x{w['false_escalation']}")
    print(f"  accuracy           : {correct}/{n} = {correct/n:.0%}")
    print(f"  TOTAL COST         : {total_cost}   (lower is better)")

    # Floors: non-tradeable. Reported, never gated - the human decides.
    floors = WEIGHTS["floors"]
    ok_missed = missed <= floors["max_missed_escalations"]
    ok_valid = validity >= floors["min_validity_rate"]
    print(f"\n  floor missed <= {floors['max_missed_escalations']}       : "
          f"{'PASS' if ok_missed else 'BREACH'}")
    print(f"  floor validity >= {floors['min_validity_rate']:.0%}   : "
          f"{'PASS' if ok_valid else 'BREACH'}")
    if not ok_valid:
        # The denominator trap, hit for real: a config that fails on hard
        # issues gets them excluded, so its cost looks better while it
        # actually answered fewer questions.
        print("  ^ cost above is computed on a reduced set - NOT comparable "
              "to a run\n    with higher validity. Use `compare` instead.")
    print("----" * 10)

    return {"total_cost": total_cost, "missed_escalation": missed,
            "false_escalation": false, "validity": validity,
            "excluded": dict(excluded_by)}


if __name__ == "__main__":
    import sys
    score(sys.argv[1], "data/golden_set.jsonl")