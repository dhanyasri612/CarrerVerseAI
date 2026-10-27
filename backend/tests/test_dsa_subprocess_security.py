"""
Focused regression tests for DSA code execution with hardened subprocess.

These tests verify the hardened subprocess execution path (Stage 2 security fix).
All payloads are harmless. Tests that could hang (infinite loop, memory exhaustion,
output flooding) are bounded by the subprocess wall-clock timeout (12s) and
resource limits (CPU 10s, memory 256 MB), so they cannot exhaust the host.

SECURITY NOTE: Subprocess execution with resource limits is a hardening measure,
NOT a complete security sandbox. These tests verify functional behavior and
resource bounding, not sandbox escape resistance.

Input format note: _parse_dsa_input_args supports single-assignment
("nums = [1,2,3]") and tuple form ("[1,2,3], 9"). Comma-separated assignments
("nums = [1,2,3], target = 9") are NOT supported by the existing parser and
fall back to raw-string args. Tests use supported formats.
"""

import os
import glob
import time
from types import SimpleNamespace

import pytest

from app.services.dsa_service import evaluate_dsa_code_submission
from app.schemas.dsa_practice import DsaCodeExecutionResponse


def _make_req(code: str, language: str = "python", examples: list | None = None, custom_input: str | None = None):
    return SimpleNamespace(
        problem_id="dsa-test-1",
        problem_title="DSA Test",
        language=language,
        code=code,
        examples=examples or [],
        custom_input=custom_input,
        action_type="run",
    )


def _run(code: str, **kwargs):
    req = _make_req(code, **kwargs)
    return evaluate_dsa_code_submission(req, None)


# ── Category 1: Accepted solution ──


def test_accepted_solution():
    """Valid Python solution passes all example cases."""
    code = """
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i
        return []
"""
    examples = [
        {"input": "[2, 7, 11, 15], 9", "output": "[0, 1]"},
        {"input": "[3, 2, 4], 6", "output": "[1, 2]"},
    ]
    res = _run(code, examples=examples)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status == "Accepted", f"Expected Accepted, got {res.status}: {res.results}"
    assert res.passedCount == res.totalCount
    assert res.totalCount == 2


# ── Category 2: Syntax error ──


def test_syntax_error():
    """Malformed Python returns Compile Error."""
    code = "def broken(:\n    return 1"
    res = _run(code)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status == "Compile Error", f"Expected Compile Error, got {res.status}"
    assert res.passedCount == 0


# ── Category 3: Runtime error ──


def test_runtime_error():
    """Division by zero at runtime returns Runtime Error."""
    code = """
class Solution:
    def divide(self, a, b):
        return a / b
"""
    examples = [
        {"input": "10, 0", "output": "inf"},
    ]
    res = _run(code, examples=examples)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status == "Runtime Error", f"Expected Runtime Error, got {res.status}: {res.results}"
    assert res.passedCount == 0


# ── Category 4: Wrong answer ──


def test_wrong_answer():
    """Incorrect return value returns Wrong Answer with actual vs expected."""
    code = """
class Solution:
    def add(self, a, b):
        return a - b  # intentional bug: subtracts instead of adds
"""
    examples = [
        {"input": "2, 3", "output": "5"},
    ]
    res = _run(code, examples=examples)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status == "Wrong Answer", f"Expected Wrong Answer, got {res.status}: {res.results}"
    assert res.passedCount == 0
    assert res.totalCount == 1
    assert res.results[0].passed is False
    assert "Expected" in (res.results[0].error or "")


# ── Category 5: Skeleton detection ──


def test_skeleton_detection():
    """Placeholder code (pass / return 0) detected as skeleton."""
    code = "class Solution:\n    def solve(self, nums):\n        pass"
    res = _run(code)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status == "Wrong Answer", f"Expected Wrong Answer, got {res.status}"
    assert res.passedCount == 0
    assert any("skeleton" in (r.error or "").lower() for r in res.results)


# ── Category 6: Infinite loop (bounded by wall-clock timeout) ──


def test_infinite_loop_bounded():
    """Infinite loop is terminated by timeout, does not hang the host."""
    code = """
class Solution:
    def solve(self, nums):
        while True:
            pass
        return 0
"""
    examples = [
        {"input": "[1, 2, 3]", "output": "0"},
    ]
    start = time.time()
    res = _run(code, examples=examples)
    elapsed = time.time() - start
    assert elapsed < 30, f"Test took too long ({elapsed:.1f}s); timeout not enforced"
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status != "Accepted", f"Infinite loop should not be Accepted, got {res.status}"
    assert res.passedCount == 0


# ── Category 7: Memory exhaustion (bounded by RLIMIT_AS) ──


def test_memory_exhaustion_bounded():
    """Large allocation attempt is bounded by memory limit."""
    code = """
class Solution:
    def solve(self, nums):
        big = [0] * (10 ** 9)
        return len(big)
"""
    examples = [
        {"input": "[1]", "output": "0"},
    ]
    start = time.time()
    res = _run(code, examples=examples)
    elapsed = time.time() - start
    assert elapsed < 30, f"Test took too long ({elapsed:.1f}s); memory limit not enforced"
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status != "Accepted", f"Memory exhaustion should not be Accepted, got {res.status}"
    assert res.passedCount == 0


# ── Category 8: Output flooding (bounded by output byte limit) ──


def test_output_flooding_bounded():
    """Excessive stdout is truncated, does not OOM the parent."""
    code = """
class Solution:
    def solve(self, nums):
        print("x" * 10_000_000)
        return 0
"""
    examples = [
        {"input": "[1]", "output": "0"},
    ]
    res = _run(code, examples=examples)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.stdout is not None
    assert len(res.stdout.encode("utf-8")) <= 64 * 1024 + 50, (
        f"Output not truncated: {len(res.stdout.encode('utf-8'))} bytes"
    )
    assert "[output truncated]" in res.stdout or res.status != "Accepted"


# ── Category 9: Temp-file cleanup ──


def test_temp_file_cleanup():
    """No temp files left behind after subprocess execution."""
    code = """
class Solution:
    def solve(self, nums):
        return sum(nums)
"""
    examples = [
        {"input": "[1, 2, 3]", "output": "6"},
    ]
    tmpdir = "/tmp"
    before = set(glob.glob(os.path.join(tmpdir, "tmp*")))
    res = _run(code, examples=examples)
    after = set(glob.glob(os.path.join(tmpdir, "tmp*")))
    new_files = after - before
    new_py_json = [f for f in new_files if f.endswith(".py") or f.endswith(".json")]
    assert len(new_py_json) == 0, f"Temp files not cleaned up: {new_py_json}"
    assert isinstance(res, DsaCodeExecutionResponse)


# ── Category 10: Response schema ──


def test_response_schema_fields():
    """All DsaCodeExecutionResponse fields are present and correctly typed."""
    code = """
class Solution:
    def solve(self, nums):
        return len(nums)
"""
    examples = [
        {"input": "[1, 2, 3]", "output": "3"},
    ]
    res = _run(code, examples=examples)
    assert isinstance(res, DsaCodeExecutionResponse)
    assert res.status in ("Accepted", "Wrong Answer", "Runtime Error", "Compile Error")
    assert isinstance(res.passedCount, int)
    assert isinstance(res.totalCount, int)
    assert isinstance(res.results, list)
    assert res.stdout is not None
    assert isinstance(res.runtimeMs, int)
    assert isinstance(res.memoryMb, str)
    assert isinstance(res.time_complexity, str)
    assert isinstance(res.space_complexity, str)
    for r in res.results:
        assert isinstance(r.caseNumber, int)
        assert isinstance(r.input, str)
        assert isinstance(r.expected, str)
        assert isinstance(r.actual, str)
        assert isinstance(r.passed, bool)
        assert r.error is None or isinstance(r.error, str)
