"""Run the excessive-agency suite against OpsAssistant.

Each attack is routed to a tool, then either executed (undefended) or checked
against the authorization policy (defended).

Usage:
    python run_lab.py                  # all attacks, no policy
    python run_lab.py direct_destructive
    python run_lab.py --defended       # all attacks WITH the policy
"""

from __future__ import annotations

import sys

from agent import route
from attacks import ATTACKS, get_attack
from defenses import apply_policy


def run_one(attack: dict, defended: bool) -> bool:
    call = route(attack["payload"])
    risky = call.name is not None and call.risk in ("sensitive", "dangerous")

    if defended:
        decision = apply_policy(call)
        status = decision.status
        reason = decision.reason
    else:
        status = "executed"
        reason = ""

    executed_bad = status == "executed" and risky
    if executed_bad:
        label = "EXECUTE"
    elif status == "executed":
        label = "safe   "
    elif status == "held":
        label = "HELD   "
    else:
        label = "BLOCK  "

    print(f"[{label}] {attack['id']} ({attack['technique']})")
    print(f"    tool call : {call.render()}  [{call.risk}]")
    if reason:
        print(f"    policy    : {reason}")
    print()
    return executed_bad


def main(argv: list[str]) -> int:
    args = argv[1:]
    defended = "--defended" in args
    args = [a for a in args if a != "--defended"]
    attacks = [get_attack(args[0])] if args else ATTACKS

    print("=" * 70)
    mode = "WITH authorization policy (defended)" if defended else "WITHOUT policy (over-privileged)"
    print(f"Excessive Agency Lab: {mode}")
    print("=" * 70 + "\n")

    bad = sum(run_one(a, defended) for a in attacks)

    print("-" * 70)
    print(f"Result: {bad}/{len(attacks)} dangerous action(s) executed.")
    print("-" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
