from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
# config.py -> harness/ -> src/ -> project root

# USD per 1M tokens. Verify against the provider's pricing page - these change.
PRICES = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-5-nano":  {"input": 0.05, "output": 0.40},
}

RUN_CONFIG = {
    "model": "gpt-5-nano",
    # "model": "gpt-4o-mini",
    "prompt_version": "v1",
    "output_mode": "prompt_only",
    "temperature": 1,
    "max_completion_tokens": 1000,
    
    "num_runs": 2,
    "golden_set_path": PROJECT_ROOT / "data" / "golden_set.jsonl",
    "runs_dir": PROJECT_ROOT / "runs"
}


WEIGHTS = {
    "needs_human": {
        "missed_escalation": 10,   # a human was needed, we said no
        "false_escalation": 1,     # we said a human was needed, they weren't
    },

    # rows = truth, columns = prediction
    "urgency": {
        "critical": {"critical": 0, "normal": 4, "low": 10}, # truth is critical: saying "normal" costs 4, saying "low" costs 10
        "normal":   {"critical": 1, "normal": 0, "low": 4},
        "low":      {"critical": 2, "normal": 1, "low": 0},
    },

    "floors": {
        "max_missed_escalations": 1,
        "min_validity_rate": 0.95,
    }
}