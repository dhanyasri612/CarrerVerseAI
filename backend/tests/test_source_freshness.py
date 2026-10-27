from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.github_service import SYNC_FRESHNESS as GITHUB_FRESHNESS, _is_fresh as github_is_fresh
from app.services.leetcode_service import SYNC_FRESHNESS as LEETCODE_FRESHNESS, _is_fresh as leetcode_is_fresh
from app.services.hackerrank_service import SYNC_FRESHNESS as HACKERRANK_FRESHNESS, _is_fresh as hackerrank_is_fresh


def source(username, age):
    return SimpleNamespace(username=username, updated_at=datetime.utcnow() - age)


def test_github_freshness_reuses_matching_source():
    assert github_is_fresh(source("octocat", GITHUB_FRESHNESS - timedelta(seconds=1)), "octocat")


def test_github_stale_or_different_source_requires_refresh():
    assert not github_is_fresh(source("octocat", GITHUB_FRESHNESS + timedelta(seconds=1)), "octocat")
    assert not github_is_fresh(source("octocat", timedelta(minutes=1)), "other")


def test_leetcode_freshness_policy():
    assert leetcode_is_fresh(source("candidate", LEETCODE_FRESHNESS - timedelta(seconds=1)), "candidate")
    assert not leetcode_is_fresh(source("candidate", LEETCODE_FRESHNESS + timedelta(seconds=1)), "candidate")


def test_hackerrank_freshness_policy():
    assert hackerrank_is_fresh(source("candidate", HACKERRANK_FRESHNESS - timedelta(seconds=1)), "candidate")
    assert not hackerrank_is_fresh(source("candidate", HACKERRANK_FRESHNESS + timedelta(seconds=1)), "candidate")
