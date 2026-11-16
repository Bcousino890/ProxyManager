"""Offline classification of DataDome-like and generic protection responses.

This module observes response data only. It does not solve or bypass challenges.
"""

from .detector import Classified, Verdict, classify, looks_like_challenge, parse_dd

__all__ = ["Classified", "Verdict", "classify", "looks_like_challenge", "parse_dd"]
