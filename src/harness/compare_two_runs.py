"""
> Load both runs, keyed by (issue_id, run_index).
> Check if manifests file agree on num_runs and golden set, if not raises error
> Walk every key. For each one, compute A's cost and B's cost.
> If either side has no usable answer, drop that pair from both.
> Sum what's left, count fixed/broke, and break errors down by type.
"""

import json
from pathlib import Path

from .config import WEIGHTS


def load_run_response(path):
    """{(issue_id, run_index): result}, plus the run's manifest."""
    with open(path) as f:
        results = {(r["issue_id"], r["run_index"]): r
                   for r in (json.loads(l) for l in f if l.strip())}
    manifest = json.loads(Path(str(path).replace(".jsonl", ".manifest.json")).read_text())
    return results, manifest


def cost_of_each_pred(result, needs_human_g):
    """Cost of one prediction, or None if the result is unusable."""
    if result is None or result["error_status"] != "ok":
        return None
    w = WEIGHTS["needs_human"]
    pred = result["decision"]["needs_human"]
    if needs_human_g == pred:
        return 0

    # If gold is True, that means Prediction is missed_escalation
    return w["missed_escalation"] if needs_human_g else w["false_escalation"]


def compare(path_a, path_b, golden_path):
    a, manifest_a = load_run_response(path_a)
    b, manifest_b = load_run_response(path_b)

    with open(golden_path) as f:
        needs_human_gold = {r["id"]: r["labels"]["needs_human"]
                for r in (json.loads(l) for l in f if l.strip())}

    # Two runs measured differently are not comparable. Hence raising error
    for key in ("num_runs", "golden_set_path"):
        if manifest_a[key] != manifest_b[key]:
            raise ValueError(f"runs differ in {key} - not comparable")

    pairs = []      # (cost_a, cost_b, gold) for pairs both runs answered
    dropped = 0

    # Below considering union of sets
    # set(a) = {("issue#1", 1), ("issue#1", 2), ("issue#2", 1)}
    # set(b) = {("issue#1", 1), ("issue#3", 1)}
    # set(a) | set(b) = {("issue#1", 1), ("issue#1", 2), ("issue#2", 1), ("issue#3", 1)}

    for id in set(a) | set(b):
        gold = needs_human_gold[id[0]]
        cost_a = cost_of_each_pred(a.get(id), gold)
        cost_b = cost_of_each_pred(b.get(id), gold)
        if cost_a is None or cost_b is None:
            dropped += 1
        else:
            pairs.append((cost_a, cost_b, gold))

    total_cost_a, total_cost_b = 0, 0
    fixed, broke = 0, 0
    # Split each side's errors by TYPE, not just count. Two configs can make a
    # similar number of mistakes and still differ hugely in cost, because one
    # missed escalation is worth ten false ones. Without this breakdown the
    # two totals are unexplained.
    missed_a = missed_b = false_a = false_b = 0

    agreed = 0
    cost_saved = cost_added = 0        # cost delta, not just a count
    fixed_missed = fixed_false = 0     # WHICH kind of error each fix rescued
    broke_missed = broke_false = 0     # WHICH kind of error each break caused

    for cost_a, cost_b, gold in pairs:
        total_cost_a += cost_a
        total_cost_b += cost_b

        # cost > 0 means "wrong", which holds only because a correct answer
        # always costs 0 (the zero diagonal of the cost matrix).
        if cost_a > 0:
            if gold:
                missed_a += 1
            else:
                false_a += 1
        if cost_b > 0:
            if gold:
                missed_b += 1
            else:
                false_b += 1

        # Counting fixes and breaks is not enough: a fix that rescues a missed
        # escalation is worth 10, a fix on a false alarm is worth 1. Counting
        # them equally repeats, one level up, exactly the mistake the cost
        # matrix exists to prevent. So track the cost delta AND which kind.
        if cost_b < cost_a:
            fixed += 1
            cost_saved += cost_a - cost_b
            if gold:
                fixed_missed += 1
            else:
                fixed_false += 1
        elif cost_b > cost_a:
            broke += 1
            cost_added += cost_b - cost_a
            if gold:
                broke_missed += 1
            else:
                broke_false += 1
        else:
            agreed += 1

    w = WEIGHTS["needs_human"]
    label = lambda m: f"{m['run_config']['model']}/{m['run_config']['prompt_version']}"

    print("----" * 10)
    print(f"A = {label(manifest_a)}")
    print(f"B = {label(manifest_b)}")
    print(f"\n{len(pairs)} pairs both answered ({dropped} dropped)\n")
    print(f"{'':22}{'A':>6}{'B':>6}")
    print(f"{'missed escalations':22}{missed_a:>6}{missed_b:>6}   x{w['missed_escalation']}")
    print(f"{'false escalations':22}{false_a:>6}{false_b:>6}   x{w['false_escalation']}")
    print(f"{'TOTAL COST':22}{total_cost_a:>6}{total_cost_b:>6}")
    net = total_cost_b - total_cost_a
    verdict = "B worse" if net > 0 else "B better" if net < 0 else "tie"

    print(f"\nB vs A, on the {len(pairs)} shared pairs:")
    print(f"  agreed              {agreed:>4}")
    print(f"  B fixed             {fixed:>4}   "
          f"({fixed_missed} missed, {fixed_false} false)   cost saved -{cost_saved}")
    print(f"  B broke             {broke:>4}   "
          f"({broke_missed} missed, {broke_false} false)   cost added +{cost_added}")
    print(f"  net by COUNT        {fixed - broke:>+4}")
    print(f"  net by COST         {net:>+4}   -> {verdict}")
    print("----" * 10)


if __name__ == "__main__":
    import sys
    compare(sys.argv[1], sys.argv[2], "data/golden_set.jsonl")