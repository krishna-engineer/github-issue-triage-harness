# Labeling Rubric

Decision rules for labeling the golden set. Written **before** labeling so
labels stay consistent across issues and reproducible by another reviewer.
Every issue is labeled against these rules; borderline calls get a one-line
note in the dataset explaining the choice.

---

## issue_type

What the issue fundamentally *is*, judged by content — not by what the
reporter titled it or which label the repo attached. If it describes broken
behavior, it is a `bug` even if filed as a question.

- **bug** — something is broken or behaves incorrectly versus expected.
- **feature_request** — asks for new capability or an enhancement to existing
  behavior that is not itself broken.
- **other** — anything that fits neither cleanly: questions, support, docs,
  CI/build chores, discussions.

## urgency

How much real-world impact and time pressure the issue carries, based on the
described severity — not on the reporter's tone. A calmly worded outage is
still `critical`; an angry cosmetic nitpick is still `low`.

- **critical** — production broken, users blocked, data loss, or a security
  risk. No reasonable workaround.
- **normal** — a genuine bug or wanted feature that affects some users or has
  a workaround. The default for most real issues.
- **low** — cosmetic, minor, nice-to-have, or safely deferrable indefinitely.

## needs_human

Whether a person must review this before it can be safely actioned. When
genuinely uncertain, label `true` — under-escalating a real problem is treated
as far worse than over-escalating a routine one.

- **true** — ambiguous, sensitive, security-related, high-impact, or the right
  action is not obvious from the issue alone.
- **false** — routine and self-explanatory; could be auto-labeled, routed, or
  closed without human judgment.