import pytest
from app.database.session import SessionLocal
from app.models.user import User
from app.services.teaching_service import get_teaching_curriculum, evaluate_and_teach
from app.schemas.teaching import TeachingEvaluationRequest


@pytest.fixture
def test_context():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(
            id=1,
            email="dhanyasri@test.com",
            username="dhanyasrik",
            full_name="Dhanyasri K",
            hashed_password="hashedpassword123",
            is_active=True,
        )
    yield db, user
    db.close()


def test_get_teaching_curriculum(test_context):
    db, user = test_context
    curriculum = get_teaching_curriculum(db, user)
    assert curriculum is not None
    assert len(curriculum.sections) == 4
    section_ids = [s.id for s in curriculum.sections]
    assert "dsa" in section_ids
    assert "skills" in section_ids
    assert "projects" in section_ids
    assert "resume" in section_ids
    assert curriculum.total_lessons >= 8


def test_evaluate_and_teach_feedback(test_context):
    db, user = test_context
    req = TeachingEvaluationRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        concept_title="Two Sum (Hash Map Lookup Invariant)",
        question_prompt="Given an array of integers nums and an integer target, find two numbers that add up to target.",
        candidate_thoughts="I would use an auxiliary hash map to store each number and its index. For each number, I check if target - num exists in the map.",
        candidate_code="def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        role="Software Engineer (SDE)",
        language="en",
    )
    result = evaluate_and_teach(req, user)
    assert result is not None
    assert result.what_is_right
    assert result.what_is_wrong
    assert result.masterclass_lesson
    assert result.optimal_solution
    assert result.key_takeaway


def test_evaluate_and_teach_multilingual(test_context):
    db, user = test_context
    req = TeachingEvaluationRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        concept_title="Two Sum (Hash Map Lookup Invariant)",
        question_prompt="Given an array of integers nums and an integer target, find two numbers that add up to target.",
        candidate_thoughts="O(N) time complexity-ல் auxiliary hash map பயன்படுத்தி தீர்க்கலாம்.",
        candidate_code="def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        role="Software Engineer (SDE)",
        language="ta",
    )
    result = evaluate_and_teach(req, user)
    assert result is not None
    assert result.what_is_right
    assert result.what_is_wrong
    assert result.masterclass_lesson
    assert result.key_takeaway


def test_teaching_curriculum_enriched_metadata_and_zero_fake_repos(test_context):
    db, user = test_context
    curriculum = get_teaching_curriculum(db, user)
    
    # 1. Verify all lessons have required metadata fields
    for section in curriculum.sections:
        for lesson in section.lessons:
            assert lesson.learning_objective, f"Missing learning_objective in {lesson.id}"
            assert lesson.prerequisites is not None, f"Missing prerequisites in {lesson.id}"
            assert lesson.diagnostic_question, f"Missing diagnostic_question in {lesson.id}"
            assert lesson.source_references, f"Missing source_references in {lesson.id}"
            assert lesson.status in ("not_started", "in_progress", "completed", "mastered")

    # 2. Verify Section 3 does NOT contain fabricated repositories
    projects_sec = next(s for s in curriculum.sections if s.id == "projects")
    for lesson in projects_sec.lessons:
        assert "CareerVerseAI" not in lesson.id
        assert "Agentic-Ecomm" not in lesson.id
        assert "AlgoMentor-AI" not in lesson.id
        assert "InboxPilot-Backend" not in lesson.id


def test_interact_with_teaching_lesson_all_actions(test_context):
    db, user = test_context
    from app.services.teaching_service import interact_with_teaching_lesson, get_candidate_teaching_progress
    from app.schemas.teaching import TeachingInteractionRequest

    # Action 1: Hint
    req_hint = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="hint",
        language="en",
    )
    res_hint = interact_with_teaching_lesson(db, user, req_hint)
    assert res_hint.hint_revealed is not None
    assert "Hint" in res_hint.teaching_message

    # Action 2: Simpler toy example
    req_simpler = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="simpler",
        language="en",
    )
    res_simpler = interact_with_teaching_lesson(db, user, req_simpler)
    assert res_simpler.example_grounding is not None

    # Action 3: Step-by-step breakdown
    req_explain = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="explain",
        language="en",
    )
    res_explain = interact_with_teaching_lesson(db, user, req_explain)
    assert res_explain.step_by_step_explanation is not None

    # Action 4: Code blueprint
    req_code = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="code",
        language="en",
    )
    res_code = interact_with_teaching_lesson(db, user, req_code)
    assert res_code.code_demonstration is not None

    # Action 5: Answer submission
    req_ans = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="answer",
        candidate_response="I iterate through the array using an auxiliary hash map to track complements in O(N) linear time.",
        candidate_code="def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n    return []",
        language="en",
    )
    res_ans = interact_with_teaching_lesson(db, user, req_ans)
    assert res_ans.what_is_right is not None
    assert res_ans.is_lesson_complete is True
    assert res_ans.mastery_status in ("completed", "mastered")

    # Verify Progress Response
    progress = get_candidate_teaching_progress(db, user)
    assert "dsa-two-sum" in progress.completed_lessons or "dsa-two-sum" in progress.mastered_lessons
    assert progress.section_progress["dsa"]["completed"] >= 1


def test_teaching_concept_map(test_context):
    db, user = test_context
    from app.services.teaching_service import get_teaching_concept_map

    concept_map = get_teaching_concept_map(db, user, lesson_id="dsa-two-sum")
    assert concept_map is not None
    assert len(concept_map.nodes) > 0
    assert len(concept_map.edges) > 0
    node_ids = [n.id for n in concept_map.nodes]
    assert "two_sum" in node_ids or "dsa-two-sum" in node_ids or "dsa:arrays_hash_map" in node_ids
    assert concept_map.current_concept_id is not None


def test_socratic_why_and_practice_actions(test_context):
    db, user = test_context
    from app.services.teaching_service import interact_with_teaching_lesson
    from app.schemas.teaching import TeachingInteractionRequest

    # Action: Why
    req_why = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="why",
        language="en",
    )
    res_why = interact_with_teaching_lesson(db, user, req_why)
    assert "Architectural & Invariant Proof" in res_why.teaching_message
    assert len(res_why.resources) > 0

    # Action: Practice
    req_practice = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="practice",
        language="en",
    )
    res_practice = interact_with_teaching_lesson(db, user, req_practice)
    assert res_practice.current_stage == "practice"
    assert res_practice.practice_exercise is not None


def test_socratic_assessment_mastery_policy(test_context):
    db, user = test_context
    from app.services.teaching_service import interact_with_teaching_lesson, get_candidate_teaching_progress
    from app.schemas.teaching import TeachingInteractionRequest

    # Case 1: Partial attempt (< 80)
    req_partial = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="assess",
        candidate_response="Just use loops.",
        candidate_code="pass",
        language="en",
    )
    res_partial = interact_with_teaching_lesson(db, user, req_partial)
    assert res_partial.assessment_evaluation is not None
    assert res_partial.assessment_evaluation["score"] < 80
    assert res_partial.is_lesson_complete is False

    # Case 2: Rigorous attempt (>= 80)
    req_master = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="assess",
        candidate_response="We maintain a hash map of complements where key is the needed value and value is the original index. The invariant guarantees single-pass lookup in O(N) time complexity and O(N) auxiliary space, checking null/empty array boundary conditions.",
        candidate_code="def two_sum(nums, target):\n    if not nums: return []\n    seen = {}\n    for i, num in enumerate(nums):\n        comp = target - num\n        if comp in seen:\n            return [seen[comp], i]\n        seen[num] = i\n    return []",
        language="en",
    )
    res_master = interact_with_teaching_lesson(db, user, req_master)
    assert res_master.assessment_evaluation is not None
    assert res_master.assessment_evaluation["score"] >= 80
    assert res_master.is_lesson_complete is True
    assert res_master.mastery_status == "mastered"
    assert res_master.current_stage == "completed"

    # Verify persistent evidence and lesson stage
    progress = get_candidate_teaching_progress(db, user)
    assert "dsa-two-sum" in progress.mastered_lessons
    assert progress.lesson_stages.get("dsa-two-sum") == "completed"
    assert "dsa-two-sum" in progress.mastery_evidence


def test_rag_teaching_resources_retrieval():
    from app.services.teaching_resource_service import retrieve_teaching_resources_for_lesson

    resources = retrieve_teaching_resources_for_lesson("FastAPI Dependency Injection", candidate_projects=[], limit=2)
    assert len(resources) >= 1
    assert any("FastAPI" in r.title or "FastAPI" in r.source for r in resources)
    for r in resources:
        assert r.canonical_url.startswith("http")
        assert len(r.excerpt) > 10


def test_learner_knowledge_profile_builder(test_context):
    db, user = test_context
    from app.services.learner_knowledge_service import build_learner_knowledge_profile

    profile = build_learner_knowledge_profile(db, user)
    assert profile.candidate_id == user.id
    assert len(profile.skills_inventory) >= 0
    assert len(profile.recommended_learning_order) > 0


def test_skill_learning_path_react_multi_stage_curriculum(test_context):
    """
    Test 1, 2, 3: Selecting React creates a 7-stage curriculum rather than one question.
    Each stage contains multiple distinct lessons following prerequisite order.
    """
    db, user = test_context
    from app.services.skill_learning_service import build_skill_learning_path

    path = build_skill_learning_path(db, "React", user)
    assert path is not None
    assert path.skill_name.lower() == "react"
    assert path.total_stages == 7
    assert path.total_lessons >= 14  # At least 14 distinct lessons

    stage_names = [s.stage_name for s in path.stages]
    assert "Foundations" in stage_names
    assert "Core React" in stage_names
    assert "Hooks" in stage_names
    assert "Intermediate React" in stage_names
    assert "Advanced React" in stage_names
    assert "Real Projects" in stage_names
    assert "Interview Readiness" in stage_names

    # Check distinct lessons in Stage 1 & Stage 3
    s1 = next(s for s in path.stages if s.stage_name == "Foundations")
    assert len(s1.lessons) >= 2
    for les in s1.lessons:
        assert les.learning_objective
        assert les.prerequisites
        assert les.diagnostic_question
        assert les.concept_summary

    s3 = next(s for s in path.stages if s.stage_name == "Hooks")
    assert len(s3.lessons) >= 3
    hook_titles = [l.title for l in s3.lessons]
    assert any("useEffect" in t or "Effect" in t for t in hook_titles)
    assert any("useMemo" in t or "Callback" in t or "Hook" in t for t in hook_titles)


def test_skill_learning_path_distinctness_java_and_sql(test_context):
    """
    Test 4: Selecting Java or SQL generates an appropriate curriculum rather than reusing React content.
    """
    db, user = test_context
    from app.services.skill_learning_service import build_skill_learning_path

    path_sql = build_skill_learning_path(db, "SQL", user)
    assert path_sql.total_stages == 7
    assert path_sql.total_lessons >= 7
    sql_lesson_titles = [l.title for s in path_sql.stages for l in s.lessons]
    assert any("B-Tree" in t or "Index" in t for t in sql_lesson_titles)
    assert any("Join" in t or "Relational" in t for t in sql_lesson_titles)
    assert not any("React" in t or "Fiber" in t for t in sql_lesson_titles)

    path_java = build_skill_learning_path(db, "Java", user)
    assert path_java.total_stages == 7
    java_lesson_titles = [l.title for s in path_java.stages for l in s.lessons]
    assert not any("React" in t or "JSX" in t for t in java_lesson_titles)
    assert any("Java" in t for t in java_lesson_titles)


def test_repository_understanding_and_project_journey(test_context):
    """
    Test 8, 9, 10, 11: Selecting a GitHub repo triggers real analysis, citing real files/metadata,
    generating a 7-stage project journey and grounded interview preparation.
    """
    db, user = test_context
    from app.models.github_profile import GitHubProfile
    from app.models.github_repository import GitHubRepository
    from app.models.github_repository_document import GitHubRepositoryDocument
    from app.models.github_repository_file import GitHubRepositoryFile
    from app.services.repository_understanding_service import (
        build_repository_understanding,
        build_project_learning_journey,
    )

    # Ensure profile and mock repo with files exist for testing
    gh_profile = db.query(GitHubProfile).filter(GitHubProfile.user_id == user.id).first()
    if not gh_profile:
        gh_profile = GitHubProfile(user_id=user.id, username=user.username or "dhanya")
        db.add(gh_profile)
        db.flush()

    repo = db.query(GitHubRepository).filter(GitHubRepository.github_profile_id == gh_profile.id).first()
    if not repo:
        repo = GitHubRepository(
            github_profile_id=gh_profile.id,
            github_repo_id=99901,
            name="task-orchestrator",
            full_name=f"{gh_profile.username}/task-orchestrator",
            description="Distributed task orchestration engine with async workers and Redis queue",
            language="Python",
        )
        db.add(repo)
        db.flush()

    # Add realistic README & source files
    db.query(GitHubRepositoryDocument).filter(GitHubRepositoryDocument.github_repository_id == repo.id).delete()
    db.query(GitHubRepositoryFile).filter(GitHubRepositoryFile.github_repository_id == repo.id).delete()

    readme_doc = GitHubRepositoryDocument(
        github_repository_id=repo.id,
        document_type="README",
        file_name="README.md",
        path="README.md",
        content=f"# {repo.name}\nDistributed worker engine using Python asyncio, Redis streams, and PostgreSQL state tracking.",
    )
    db.add(readme_doc)

    files = [
        GitHubRepositoryFile(github_repository_id=repo.id, file_path="main.py", file_name="main.py", file_type="file"),
        GitHubRepositoryFile(github_repository_id=repo.id, file_path="requirements.txt", file_name="requirements.txt", file_type="file"),
        GitHubRepositoryFile(github_repository_id=repo.id, file_path="core/engine.py", file_name="engine.py", file_type="file"),
        GitHubRepositoryFile(github_repository_id=repo.id, file_path="models/task.py", file_name="task.py", file_type="file"),
        GitHubRepositoryFile(github_repository_id=repo.id, file_path="tests/test_engine.py", file_name="test_engine.py", file_type="file"),
    ]
    db.add_all(files)
    db.commit()

    # 1. Test Repository Understanding
    model = build_repository_understanding(db, repo.id, user, force_refresh=True)
    assert model.repository_name == repo.name
    assert model.source_file_count == 5
    assert model.is_limited_to_readme is False
    assert "main.py" in model.application_entry_points
    assert len(model.source_evidence_citations) >= 2
    assert model.request_flow
    assert model.database_flow
    assert model.auth_security_flow

    # 2. Test Project Learning Journey
    journey = build_project_learning_journey(db, repo.id, user, force_refresh=True)
    assert journey.total_stages == 7
    assert journey.total_lessons >= 10
    assert journey.interview_prep is not None
    assert journey.interview_prep.short_introduction
    assert journey.interview_prep.architecture_walkthrough
    assert len(journey.interview_prep.technical_decisions) >= 1
    assert len(journey.interview_prep.practice_interview_questions) >= 3


def test_conversational_tutor_dr_cyra_vance(test_context):
    """
    Test 5, 6, 7, 14: Dr. Cyra Vance answers follow-up questions without losing context,
    separates ordinary tutoring from assessment mode, and persists conversation in PostgreSQL.
    """
    db, user = test_context
    from app.services.teaching_service import chat_with_teaching_mentor
    from app.schemas.teaching import TeachingChatRequest, TeachingChatTurn
    from app.models.teaching_progress import TeachingProgress

    # Case A: Ordinary Q&A (is_assessment=False) -> No grading, informative answer, suggestions
    req_tutor = TeachingChatRequest(
        mode="skill",
        target_id="React",
        lesson_id="skill-react-s3-l1-useeffect",
        message="Explain this more simply using an everyday analogy, and how does it prevent race conditions?",
        chat_history=[
            TeachingChatTurn(role="user", content="What is useEffect?"),
            TeachingChatTurn(role="cyra", content="useEffect synchronizes your component with an external system."),
        ],
        is_assessment=False,
        language="en",
    )
    res_tutor = chat_with_teaching_mentor(db, user, req_tutor)
    assert res_tutor.reply is not None
    assert len(res_tutor.reply) > 50
    assert res_tutor.is_assessment is False
    assert res_tutor.assessment_evaluation is None
    assert len(res_tutor.suggested_follow_ups) >= 1

    # Verify persistent PostgreSQL history
    prog = db.query(TeachingProgress).filter(
        TeachingProgress.candidate_id == user.id,
        TeachingProgress.lesson_id == "skill-react-s3-l1-useeffect",
    ).first()
    assert prog is not None
    assert len(prog.turns) >= 2
    assert prog.turns[-2]["content"] == req_tutor.message
    assert prog.turns[-1]["role"] == "cyra"

    # Case B: Assessment Mode (is_assessment=True) -> Grades attempt, awards mastery if >= 80
    req_assess = TeachingChatRequest(
        mode="skill",
        target_id="React",
        lesson_id="skill-react-s3-l1-useeffect",
        message="To prevent race conditions, we declare a boolean flag inside useEffect initialized to true. In the cleanup return function, we set it to false. When the async promise resolves, we check the flag before calling setState.",
        code_workspace="useEffect(() => {\n  let active = true;\n  fetchData().then(d => { if (active) setData(d); });\n  return () => { active = false; };\n}, [query]);",
        is_assessment=True,
        language="en",
    )
    res_assess = chat_with_teaching_mentor(db, user, req_assess)
    assert res_assess.is_assessment is True
    assert res_assess.assessment_evaluation is not None
    assert res_assess.demonstrated_understanding is True
    assert res_assess.assessment_evaluation["score"] >= 80

    # Verify status in PostgreSQL
    db.refresh(prog)
    assert prog.status == "mastered"
    assert prog.current_stage == "completed"




