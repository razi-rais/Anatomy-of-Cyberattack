"""Shared detection helpers for the lab kit.

A leak or hijack is detected by normalizing the text (so spaced out or dashed
obfuscations still match) and checking for a target string.
"""

from __future__ import annotations


def normalize(text: str) -> str:
    """Keep only alphanumeric characters, uppercased."""
    return "".join(ch for ch in text.upper() if ch.isalnum())


def contains(haystack: str, needle: str) -> bool:
    """Return True if needle appears in haystack after normalization."""
    return normalize(needle) in normalize(haystack)
