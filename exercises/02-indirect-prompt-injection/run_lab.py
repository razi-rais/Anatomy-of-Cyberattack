"""Run the indirect prompt-injection suite against SupportSummarizer.

Each poisoned ticket is summarized, and the runner reports whether the bot was
hijacked (leaked the secret or echoed an injected marker).

Usage:
    python run_lab.py                 # all tickets, no defenses
    python run_lab.py override_reveal # one ticket by id
    python run_lab.py --defended      # all tickets WITH guardrails
"""

from __future__ import annotations

import sys

from attacks import ATTACKS, get_attack
from defenses import summarize_defended
from judge import hijacked
from summarizer_bot import summarize, summarize_spotlighted


def run_one(attack: dict, defended: bool) -> bool:
    markers = attack.get("markers") or []
    if defended:
        # Defended mode applies spotlighting at the model call, wrapped by the
        # input and output guardrails.
        result = summarize_defended(attack["payload"], summarize_spotlighted, markers)
        reply = result.reply
        hit = hijacked(reply, markers)
        if hit:
            status = "HIJACK"
        elif result.blocked_by:
            status = "BLOCK "
        else:
            status = "safe  "
        extra = f"  (blocked_by={result.blocked_by})" if result.blocked_by else ""
    else:
        reply = summarize(attack["payload"])
        hit = hijacked(reply, markers)
        status = "HIJACK" if hit else "safe  "
        extra = ""

    print(f"[{status}] {attack['id']} ({attack['technique']}){extra}")
    print(f"    summary : {reply.replace(chr(10), ' ')[:120]}")
    print()
    return hit


def main(argv: list[str]) -> int:
    args = argv[1:]
    defended = "--defended" in args
    args = [a for a in args if a != "--defended"]
    attacks = [get_attack(args[0])] if args else ATTACKS

    print("=" * 70)
    mode = "WITH guardrails (defended)" if defended else "WITHOUT guardrails (vulnerable)"
    print(f"Indirect Prompt Injection Lab: {mode}")
    print("=" * 70 + "\n")

    hijacks = sum(run_one(a, defended) for a in attacks)

    print("-" * 70)
    print(f"Result: {hijacks}/{len(attacks)} ticket(s) hijacked the bot.")
    print("-" * 70)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
