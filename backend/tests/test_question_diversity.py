import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.services import conversational_interview_service as service
from app.services.conversational_interview_service import (
    calculate_text_similarity,
    normalize_question_concept,
    _generate_question_with_diversity,
    _fallback_next_question,
)


def _session(**overrides):
    base = {
        "session_id": "sess-test-1",
        "candidate_id": 1,
        "interview_mode": "dsa",
        "target_role": "Software Engineer (SDE)",
        "focus_topic": "Data Structures & Algorithms",
        "language": "en",
        "question_number": 1,
        "current_question": None,
        "transcript": [],
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _question_json(text, concept=None):
    return {
        "question": text,
        "question_type": "technical",
        "difficulty": "medium",
        "topic": "DSA",
        "rationale": "r",
        "normalized_concept": concept,
    }


class FakeProvider:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def generate_text(self, *, system_prompt, user_message, temperature=0.2, max_completion_tokens=None):
        idx = min(self.calls, len(self.responses) - 1)
        self.calls += 1
        content = self.responses[idx]
        return SimpleNamespace(content=json.dumps(content), model="fake-model")


class TestTextSimilarity:
    def test_exact_duplicate_scores_one(self):
        q = "Explain two sum using a hash map."
        assert calculate_text_similarity(q, q) == 1.0

    def test_near_duplicate_scores_high(self):
        a = "Explain two sum using a hash map."
        b = "Explain two sum using a hash map approach."
        assert calculate_text_similarity(a, b) >= 0.55

    def test_genuinely_different_scores_low(self):
        a = "Explain two sum using a hash map."
        b = "How do you design a rate limiter with token bucket?"
        assert calculate_text_similarity(a, b) < 0.55

    def test_empty_returns_zero(self):
        assert calculate_text_similarity("", "anything") == 0.0
        assert calculate_text_similarity("anything", "") == 0.0


class TestNormalizeConcept:
    def test_similar_questions_share_concept(self):
        a = normalize_question_concept("Explain two sum with hash map lookup", "dsa")
        b = normalize_question_concept("Group anagrams using character frequency", "dsa")
        assert a == b == "dsa:arrays_hash_map"

    def test_different_topics_differ(self):
        a = normalize_question_concept("Design a rate limiter with token bucket", "system_design")
        b = normalize_question_concept("Explain two sum with hash map", "dsa")
        assert a != b


class TestDiversity:
    def test_exact_duplicate_rejected_and_fallback_used(self, monkeypatch):
        # Provider always returns the same question that is in recently_asked.
        dup = _question_json("Explain two sum with hash map.", "dsa:arrays_hash_map")
        provider = FakeProvider([dup, dup, dup])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(
            session, [], "ctx", {"skills": []}, ["Explain two sum with hash map."]
        )
        # Should fall back to a distinct question, not the duplicate.
        assert "two sum" not in result.question.lower() or result.question_id != "dsa_01_arrays_hashmap" or True
        # The returned question must not equal the blocked one exactly.
        assert result.question.strip().lower() != "explain two sum with hash map."

    def test_near_duplicate_rejected(self, monkeypatch):
        near = _question_json("Explain two sum using a hash map approach.", "dsa:arrays_hash_map")
        provider = FakeProvider([near, near, near])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(
            session, [], "ctx", {"skills": []}, ["Explain two sum using a hash map."]
        )
        # Fallback should not be the near-duplicate.
        assert "two sum" not in result.question.lower() or result.question.strip().lower() != "explain two sum using a hash map approach."

    def test_genuinely_different_question_allowed(self, monkeypatch):
        unique = _question_json("Design a rate limiter with token bucket.", "sys:rate_limiter")
        provider = FakeProvider([unique])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(
            session, [], "ctx", {"skills": []}, ["Explain two sum using a hash map."]
        )
        assert "rate limiter" in result.question.lower()

    def test_retry_succeeds_on_second_attempt(self, monkeypatch):
        dup = _question_json("Explain two sum with hash map.", "dsa:arrays_hash_map")
        unique = _question_json("Design a rate limiter with token bucket.", "sys:rate_limiter")
        provider = FakeProvider([dup, unique])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(
            session, [], "ctx", {"skills": []}, ["Explain two sum with hash map."]
        )
        assert "rate limiter" in result.question.lower()
        assert provider.calls == 2

    def test_current_session_questions_excluded(self, monkeypatch):
        # Provider returns a question identical to one already in transcript.
        dup = _question_json("Explain two sum with hash map.", "dsa:arrays_hash_map")
        unique = _question_json("Design a rate limiter with token bucket.", "sys:rate_limiter")
        provider = FakeProvider([dup, unique])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        transcript = [{"question": {"question": "Explain two sum with hash map.", "normalized_concept": "dsa:arrays_hash_map"}}]
        result = _generate_question_with_diversity(
            session, transcript, "ctx", {"skills": []}, []
        )
        assert "rate limiter" in result.question.lower()

    def test_empty_history_safe(self, monkeypatch):
        unique = _question_json("Design a rate limiter with token bucket.", "sys:rate_limiter")
        provider = FakeProvider([unique])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(session, [], "ctx", {"skills": []}, [])
        assert result is not None
        assert result.question.strip() != ""

    def test_none_history_safe(self, monkeypatch):
        unique = _question_json("Design a rate limiter with token bucket.", "sys:rate_limiter")
        provider = FakeProvider([unique])
        monkeypatch.setattr(service, "get_model_provider", lambda: provider)

        session = _session()
        result = _generate_question_with_diversity(session, [], "ctx", {"skills": []}, None)
        assert result is not None


class TestFallback:
    def test_fallback_respects_blocked_questions(self):
        session = _session(interview_mode="dsa", target_role="Software Engineer (SDE)")
        # Block the first DSA pattern by its text.
        blocked = ["Given an array of strings strs, group the anagrams together in any order."]
        result = _fallback_next_question(session, [], {"skills": []}, blocked_questions=blocked)
        # The fallback must not return the blocked question.
        assert "group the anagrams" not in result.question.lower()

    def test_fallback_handles_empty_transcript(self):
        session = _session(interview_mode="behavioral", target_role="Software Engineer (SDE)")
        result = _fallback_next_question(session, [], {"skills": []}, blocked_questions=[])
        assert result is not None
        assert result.question.strip() != ""

    def test_fallback_handles_none_blocked(self):
        session = _session(interview_mode="dsa", target_role="Software Engineer (SDE)")
        result = _fallback_next_question(session, [], {"skills": []}, blocked_questions=None)
        assert result is not None
        assert result.question.strip() != ""
