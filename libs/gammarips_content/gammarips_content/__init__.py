"""
gammarips_content — shared primitives for GammaRips content publishers.

Used by:
- x-poster (ADK multi-agent X publisher)
- blog-generator (ADK multi-agent blog writer)

Provides:
- voice_rules:  brand voice rules + retired-alias block list
- compliance:   deterministic rubric scoring
- tweepy_helper: X API wrapper (OAuth 1.0a, media upload, QRT support)
- firestore_helpers: common reads/writes for posts + schedule docs
"""

__version__ = "0.1.0"
