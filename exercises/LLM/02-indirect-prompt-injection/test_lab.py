"""Test suite for the Indirect Prompt Injection lab.

Layers:
1. Deterministic unit tests for the judge, the defenses, and the catalog.
   These mock the model so they are fast and reproducible.
2. Live integration tests that summarize a benign ticket (must not hijack) and
   the override ticket (must hijack). Skipped automatically if Ollama is down.

Run:
    python -m unittest -v
"""

from __future__ import annotations

import unittest
import urllib.request
from unittest import mock

import defenses
from attacks import ATTACKS, get_attack
from judge import hijacked
from summarizer_bot import (
    SECRET_ESCALATION_CODE,
    SPOTLIGHT_SYSTEM_PROMPT,
    TRUSTED_STAFF_REQUEST,
    spotlight_task,
    summarize,
)


def _ollama_available() -> bool:
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5).read()
        return True
    except Exception:
        return False


class TestJudge(unittest.TestCase):
    def test_detects_secret(self):
        self.assertTrue(hijacked(f"Code is {SECRET_ESCALATION_CODE}"))

    def test_detects_spaced_secret(self):
        self.assertTrue(hijacked("E S C A L A T E - 9 0 0 0"))

    def test_detects_marker(self):
        self.assertTrue(hijacked("Sure: PWNED-BY-TICKET", markers=["PWNED-BY-TICKET"]))

    def test_clean_summary_is_safe(self):
        self.assertFalse(hijacked("The customer reports a late laptop order."))


class TestDefenses(unittest.TestCase):
    def test_input_guardrail_flags_command_tickets(self):
        # Four of the five attacks carry obvious command or secret signatures.
        for attack_id in ("override_reveal", "hidden_comment"):
            payload = get_attack(attack_id)["payload"]
            self.assertIsNotNone(
                defenses.input_guardrail(payload),
                f"{attack_id} should be caught by the input guardrail",
            )

    def test_output_only_attack_slips_past_input(self):
        # The output-poisoning ticket reads like a normal request with no command
        # keyword, so the input scan misses it on purpose. The output guardrail
        # must catch it instead.
        payload = get_attack("marker_inject")["payload"]
        self.assertIsNone(defenses.input_guardrail(payload))

    def test_input_guardrail_allows_benign_ticket(self):
        self.assertIsNone(defenses.input_guardrail("My order is late and I want a refund."))

    def test_output_guardrail_blocks_secret(self):
        self.assertTrue(defenses.output_guardrail(f"See {SECRET_ESCALATION_CODE}"))
        self.assertFalse(defenses.output_guardrail("A normal summary."))

    def test_output_guardrail_blocks_injected_marker(self):
        self.assertTrue(defenses.output_guardrail(
            "The product is good. PWNED-BY-TICKET", markers=["PWNED-BY-TICKET"]))

    def test_input_block_skips_the_model(self):
        called = mock.MagicMock()
        result = defenses.summarize_defended(
            get_attack("override_reveal")["payload"], called)
        called.assert_not_called()
        self.assertEqual(result.blocked_by, "input_guardrail")

    def test_output_block_catches_poisoned_summary(self):
        # The marker ticket passes the input scan, then a tricked model appends
        # the attacker marker, and the output guardrail blocks the summary.
        attack = get_attack("marker_inject")
        tricked = lambda t: "The product is good but shipping was slow. PWNED-BY-TICKET"
        result = defenses.summarize_defended(attack["payload"], tricked, attack["markers"])
        self.assertEqual(result.blocked_by, "output_guardrail")
        self.assertNotIn(SECRET_ESCALATION_CODE, result.reply)

    def test_benign_passes_through(self):
        result = defenses.summarize_defended(
            "My order is late.", lambda t: "Customer reports a late order.")
        self.assertIsNone(result.blocked_by)


class TestSpotlighting(unittest.TestCase):
    def test_spotlight_task_wraps_ticket_in_markers(self):
        wrapped = spotlight_task("my order is late")
        self.assertIn("<<<BEGIN UNTRUSTED TICKET>>>", wrapped)
        self.assertIn("<<<END UNTRUSTED TICKET>>>", wrapped)
        self.assertIn("my order is late", wrapped)

    def test_spotlight_system_prompt_separates_data_from_instructions(self):
        self.assertIn("DATA", SPOTLIGHT_SYSTEM_PROMPT)
        self.assertIn("never an instruction", SPOTLIGHT_SYSTEM_PROMPT.lower())

    def test_trusted_request_is_fixed_text(self):
        self.assertTrue(TRUSTED_STAFF_REQUEST.strip())
        self.assertNotIn(SECRET_ESCALATION_CODE, TRUSTED_STAFF_REQUEST)


class TestAttackCatalog(unittest.TestCase):
    def test_exactly_three_attacks(self):
        self.assertEqual(len(ATTACKS), 3)
        self.assertEqual(
            [a["id"] for a in ATTACKS],
            ["override_reveal", "hidden_comment", "marker_inject"],
        )

    def test_required_fields(self):
        for a in ATTACKS:
            for field in ("id", "technique", "description", "payload", "markers", "why", "defense"):
                self.assertIn(field, a)
            self.assertTrue(a["payload"].strip())
            self.assertTrue(a["why"].strip())
            self.assertTrue(a["defense"].strip())

    def test_ids_unique(self):
        ids = [a["id"] for a in ATTACKS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_get_attack(self):
        self.assertEqual(get_attack("marker_inject")["id"], "marker_inject")
        with self.assertRaises(KeyError):
            get_attack("nope")


@unittest.skipUnless(_ollama_available(), "Ollama is not reachable on localhost:11434")
class TestLiveBot(unittest.TestCase):
    def test_benign_ticket_is_summarized_safely(self):
        reply = summarize("My laptop order #4471 is late and I would like an update please.")
        self.assertFalse(hijacked(reply), f"Unexpected hijack: {reply!r}")

    def test_override_ticket_hijacks_the_bot(self):
        reply = summarize(get_attack("override_reveal")["payload"])
        self.assertTrue(hijacked(reply), f"Expected a hijack, got: {reply!r}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
