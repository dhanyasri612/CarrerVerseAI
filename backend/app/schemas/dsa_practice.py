from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TopicResource(BaseModel):
    title: str
    url: str
    resource_type: str = "Guide"  # "Cheat Sheet", "Pattern Guide", "Video Tutorial", "Reference"
    summary: str


class TopicMasteryAssessment(BaseModel):
    topic: str
    category: str = "Core DSA"
    status: str = "to_practice"  # "practiced" | "to_practice"
    solved_count: int = 0
    target_count: int = 15
    mastery_level: str = "Needs Practice"  # "Interview Ready", "Competent", "Needs Practice", "Not Started"
    is_good_enough: bool = False
    score_percent: int = 0
    assessment_verdict: str
    recommended_action: str
    resources: List[TopicResource] = Field(default_factory=list)


class DsaProblemExample(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class DsaRecommendedProblem(BaseModel):
    id: str
    title: str
    difficulty: str  # "Easy", "Medium", "Hard"
    topic: str
    platform: str = "LeetCode"  # "LeetCode" | "HackerRank"
    canonical_url: Optional[str] = None
    similar_to: Optional[str] = None
    description: str
    examples: List[DsaProblemExample] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    approach: str
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    resources: List[TopicResource] = Field(default_factory=list)
    starter_code: Dict[str, str] = Field(default_factory=dict)
    step_by_step_teaching: Optional[Dict[str, Any]] = None


class DsaRoadmapStage(BaseModel):
    stage: int
    title: str
    duration: str
    topics: List[str]
    pattern: str
    learning_goal: str
    target_problems_count: int
    status: str = "in_progress"  # "completed", "in_progress", "upcoming"
    mastery_score: int = 50
    stage_assessment: str = ""


class DsaPracticeResponse(BaseModel):
    standing_summary: str
    connected_platforms: Dict[str, bool]
    current_stats: Dict[str, Any]
    target_role: Optional[str] = "Software Developer"
    overall_readiness_score: int = 65
    readiness_verdict: str = "Good enough for standard technical phone screens; reinforce DP & Graphs for tier-1 tech."
    practiced_topics: List[TopicMasteryAssessment] = Field(default_factory=list)
    to_practice_topics: List[TopicMasteryAssessment] = Field(default_factory=list)
    dsa_roadmap: List[DsaRoadmapStage]
    recommended_problems: List[DsaRecommendedProblem]


class DsaCodeHintRequest(BaseModel):
    problem_id: str
    problem_title: str
    problem_description: str
    language: str = "python"
    code: Optional[str] = None
    user_code: Optional[str] = None
    user_query: Optional[str] = None
    target_role: Optional[str] = "Software Developer"
    action_type: str = "hint"  # "hint" | "analyze" | "submit"


class DsaCodeHintResponse(BaseModel):
    hint: str
    mistake_category: str = "Algorithmic Invariant"
    socratic_question: str
    is_on_right_track: bool = True
    status: str = "needs_tweak"  # "needs_tweak" | "on_track" | "ready_to_test"
    time_complexity_estimate: Optional[str] = None
    space_complexity_estimate: Optional[str] = None
    suggested_test_input: Optional[str] = None


class DsaCodeTestCaseResult(BaseModel):
    caseNumber: int
    input: str
    expected: str
    actual: str
    passed: bool
    error: Optional[str] = None


class DsaCodeExecutionRequest(BaseModel):
    problem_id: str
    problem_title: Optional[str] = "DSA Problem"
    language: str = "python"
    code: str = ""
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    custom_input: Optional[str] = None
    action_type: str = "run"  # "run" | "submit"


class DsaCodeExecutionResponse(BaseModel):
    status: str  # "Accepted" | "Wrong Answer" | "Runtime Error" | "Compilation Error"
    passedCount: int
    totalCount: int
    results: List[DsaCodeTestCaseResult]
    stdout: Optional[str] = ""
    runtimeMs: int = 52
    memoryMb: str = "15.8"
    time_complexity: Optional[str] = "O(N)"
    space_complexity: Optional[str] = "O(1)"



