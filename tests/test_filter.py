"""Tests for pipeline/filter.py — pure scoring functions.

`score_transcript` and `score_clip` are heuristic 0-1 scorers with no
external dependencies, so they're testable as pure functions.
"""

import pytest

from pipeline.filter import score_clip, score_transcript


class TestScoreTranscript:
    def test_empty_string_is_zero(self):
        assert score_transcript("") == 0.0

    def test_whitespace_only_is_zero(self):
        assert score_transcript("       ") == 0.0

    def test_below_twenty_chars_is_zero(self):
        # Length-after-strip < 20 short-circuits to 0.0.
        assert score_transcript("short text here") == 0.0

    def test_fewer_than_five_words_returns_floor(self):
        # >=20 chars but <5 words gets the 0.1 floor.
        # "aaaaaa bbbbbb cccccc xxx" → 24 chars, 4 words.
        assert score_transcript("aaaaaa bbbbbb cccccc xxx") == 0.1

    def test_math_vocabulary_boosts_score(self):
        plain = score_transcript(
            "the the the the the the the the the the the"
        )
        mathy = score_transcript(
            "equation derivative integral matrix vector proof"
        )
        assert mathy > plain

    def test_teaching_language_boosts_score(self):
        plain = score_transcript(
            "the cat sat on the mat one fine afternoon all alone today"
        )
        teaching = score_transcript(
            "let's consider step by step, first notice that, for example, remember"
        )
        assert teaching > plain

    def test_score_stays_in_unit_interval(self):
        # Pile every category in.
        text = (
            "equation derivative integral matrix vector proof theorem formula "
            "let's consider step by step, first notice, for example, remember"
        )
        s = score_transcript(text)
        assert 0.0 <= s <= 1.0

    def test_only_math_words_caps_at_max_math_contribution(self):
        # math_score component is capped at 1.0 → 0.4 max contribution.
        s = score_transcript(
            "equation derivative integral matrix vector proof theorem formula "
            "graph function quadratic linear polynomial eigenvalue determinant limit"
        )
        # math_score = 1.0, teach_score = 0, length_score = min(1, 16/30) ≈ 0.533
        # total ≈ 0.4 + 0 + 0.3 * 0.533 ≈ 0.56
        assert 0.5 < s < 0.7


class TestScoreClip:
    def test_ideal_duration_full_duration_component(self):
        # transcript_score = 0.0, duration_score = 1.0 → 0.7*0 + 0.3*1.0 = 0.3
        assert score_clip({"transcript": "", "duration": 15}) == pytest.approx(0.3)

    def test_too_short_duration_penalised(self):
        # duration_score = 0.2 → 0.06
        assert score_clip({"transcript": "", "duration": 2}) == pytest.approx(0.06)

    def test_too_long_duration_penalised(self):
        # > 60s → duration_score = 0.2 → 0.06
        assert score_clip({"transcript": "", "duration": 90}) == pytest.approx(0.06)

    def test_edge_duration_gets_partial_score(self):
        # 3 <= duration < 5 → duration_score = 0.6 → 0.18
        assert score_clip({"transcript": "", "duration": 4}) == pytest.approx(0.18)

    def test_edge_long_duration_gets_partial_score(self):
        # 30 < duration <= 60 → duration_score = 0.6 → 0.18
        assert score_clip({"transcript": "", "duration": 45}) == pytest.approx(0.18)

    def test_missing_transcript_key_defaults_to_empty(self):
        # No KeyError; transcript score should be 0.
        s = score_clip({"duration": 15})
        assert s == pytest.approx(0.3)

    def test_missing_duration_key_treated_as_zero(self):
        # No KeyError; duration of 0 < 3 → 0.2
        s = score_clip({"transcript": ""})
        assert s == pytest.approx(0.06)

    def test_combined_score_in_unit_interval(self):
        clip = {
            "transcript": (
                "equation derivative integral matrix let's consider "
                "step first notice for example remember"
            ),
            "duration": 15,
        }
        s = score_clip(clip)
        assert 0.0 <= s <= 1.0

    def test_high_quality_clip_scores_higher_than_low_quality(self):
        low = {"transcript": "uh um er ah oh wow yeah", "duration": 80}
        high = {
            "transcript": (
                "let's solve this quadratic equation step by step "
                "first notice the coefficient for example"
            ),
            "duration": 18,
        }
        assert score_clip(high) > score_clip(low)
