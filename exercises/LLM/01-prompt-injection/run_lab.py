"""Run the full prompt-injection attack suite against the CustomerCare Bot.

For each attack it prints whether the secret leaked, then a summary. Use this
to *see* the anatomy of the attack play out live.

Usage:
    python run_lab.py                    # run all attacks (no defenses)
    python run_lab.py direct_override    # run a single attack by id
    python run_lab.py --defended         # run all attacks WITH guardrails
    python run_lab.py --defended roleplay_devmode   # one attack, defended

Tip: run it once without --defended and once with it to show the BEFORE/AFTER.
"""

from __future__ import annotations

import sys

from attacks import ATTACKS, get_attack
from customercare_bot import respond
from defenses import respond_defended
from judge import secret_leaked


def run_one(attack: dict, defended: bool) -> bool:
    if defended:
        result = respond_defended(attack["payload"])
        reply = result.reply
        leaked = secret_leaked(reply)
        if leaked:
            status = "LEAK "
        elif result.blocked_by:
            status = "BLOCK"
        else:
            status = "safe "
        extra = f"  (blocked_by={result.blocked_by})" if result.blocked_by else ""
    else:
        reply = respond(attack["payload"])
        leaked = secret_leaked(reply)
        status = "LEAK " if leaked else "safe "
        extra = ""

    print(f"[{status}] {attack['id']} ({attack['technique']}){extra}")
    print(f"    payload : {attack['payload'].splitlines()[0][:80]}")
    print(f"    reply   : {reply.replace(chr(10), ' ')[:120]}")
    print()
    return leaked


def main(argv: list[str]) -> int:
    args = argv[1:]
    defended = "--defended" in args
    args = [a for a in args if a != "--defended"]

    attacks = [get_attack(args[0])] if args else ATTACKS

    print("=" * 70)
    mode = "WITH guardrails (defended)" if defended else "WITHOUT guardrails (vulnerable)"
    print(f"Prompt Injection Lab: {mode}")
    print("=" * 70 + "\n")

    leaks = sum(run_one(attack, defended) for attack in attacks)

    print("-" * 70)
    print(f"Result: {leaks}/{len(attacks)} attack(s) leaked the secret.")
    print("-" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
