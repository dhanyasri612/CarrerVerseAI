import pytest
from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.dsa_practice import DsaCodeHintRequest, DsaCodeHintResponse
from app.services.dsa_service import generate_dsa_interactive_hint


@pytest.fixture
def test_user():
    db = SessionLocal()
    user = db.query(User).first()
    db.close()
    return user


def test_dsa_socratic_hint_sliding_window_js(test_user):
    req = DsaCodeHintRequest(
        problem_id="dsa-p1",
        problem_title="Max Contiguous Subarray with Bounded Distinct Elements",
        problem_description="Given array nums and k, return length of longest contiguous subarray containing at most k distinct elements.",
        user_code="function maxSubarrayLength(nums, k) {\n  let left = 0, maxLen = 0;\n  let counts = new Map();\n  for (let right = 0; right < nums.length; right++) {\n    counts.set(nums[right], (counts.get(nums[right]) || 0) + 1);\n    maxLen = Math.max(maxLen, right - left + 1);\n  }\n  return maxLen;\n}",
        language="javascript",
        target_role="Full Stack Developer",
        user_query="Why is my window not shrinking?",
    )
    res = generate_dsa_interactive_hint(req, test_user)
    assert isinstance(res, DsaCodeHintResponse)
    assert "window contraction" in res.hint.lower() or "contraction" in res.mistake_category.lower()
    # Ensure solution code is NOT spoiled
    assert "function maxSubarrayLength" not in res.hint
    assert "def " not in res.hint
    assert len(res.socratic_question) > 10


def test_dsa_socratic_hint_dp_python(test_user):
    req = DsaCodeHintRequest(
        problem_id="dsa-p3",
        problem_title="Stock Trading with Transaction Cooldown and Fee",
        problem_description="Return max profit with transaction fee.",
        user_code="def maxProfit(prices, fee):\n    cash = 0\n    for p in prices:\n        cash = max(cash, p - fee)\n    return cash",
        language="python",
        target_role="Backend Developer",
    )
    res = generate_dsa_interactive_hint(req, test_user)
    assert isinstance(res, DsaCodeHintResponse)
    assert res.mistake_category is not None
    assert res.socratic_question is not None
    # Ensure no full solution dump
    assert "return" not in res.hint.lower()


def test_dsa_socratic_hint_cpp(test_user):
    req = DsaCodeHintRequest(
        problem_id="dsa-p2",
        problem_title="Island Perimeter and River Network Diameter",
        problem_description="Return max island perimeter.",
        user_code="class Solution { public: int maxIslandPerimeter(vector<vector<int>>& grid) { return 0; } };",
        language="cpp",
        target_role="Software Developer",
    )
    res = generate_dsa_interactive_hint(req, test_user)
    assert isinstance(res, DsaCodeHintResponse)
    assert res.suggested_test_input is not None


def test_dsa_evaluate_wrong_code(test_user):
    from app.schemas.dsa_practice import DsaCodeExecutionRequest, DsaCodeExecutionResponse
    from app.services.dsa_service import evaluate_dsa_code_submission

    req = DsaCodeExecutionRequest(
        problem_id="dsa-p1",
        problem_title="Max Contiguous Subarray with Bounded Distinct Elements",
        language="python",
        code="def max_subarray(nums, k):\n    return 0",
        examples=[
            {"input": "nums = [1, 2, 1, 2, 3], k = 2", "output": "4"},
            {"input": "nums = [1, 2, 1, 3, 4], k = 3", "output": "3"},
        ],
        action_type="run",
    )
    res = evaluate_dsa_code_submission(req, test_user)
    assert isinstance(res, DsaCodeExecutionResponse)
    # MUST NOT falsely pass wrong code
    assert res.status == "Wrong Answer"
    assert res.passedCount == 0
    assert len(res.results) == 2
    assert not any(r.passed for r in res.results)


def test_cyra_chat_conversational(test_user):
    from app.schemas.interview import CyraChatRequest, CyraChatResponse
    from app.services.conversational_interview_service import generate_cyra_chat_response

    req = CyraChatRequest(
        message="I'm planning to use a two-pointer sliding window with a HashMap. How should I handle the window contraction?",
        current_question="Longest Substring with At Most K Distinct Elements",
        role="Full Stack Developer",
        action_type="approach",
    )
    res = generate_cyra_chat_response(req, test_user)
    assert isinstance(res, CyraChatResponse)
    assert len(res.reply) > 20
    assert "in canned" not in res.reply

