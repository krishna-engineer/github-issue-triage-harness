import argparse
from .core_service_runner import run
from .score_single_run import score
from .compare_two_runs import compare

def main():
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the service over the golden set")
    r.add_argument("label", help="name for this run")

    s = sub.add_parser("score", help="score one run")
    s.add_argument("results")

    c = sub.add_parser("compare", help="compare two runs on the shared set")
    c.add_argument("run_a")
    c.add_argument("run_b")

    args = p.parse_args()
    golden = "data/golden_set.jsonl"
    if args.cmd == "run":
        run(label=args.label)
    elif args.cmd == "score":
        score(args.results, golden)
    else:
        compare(args.run_a, args.run_b, golden)