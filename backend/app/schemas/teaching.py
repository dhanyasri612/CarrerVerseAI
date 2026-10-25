from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TeachingEvaluationRequest(BaseModel):
    section_id: str = Field(..., description="Section id: dsa, skills, projects, or resume")
    lesson_id: str = Field(..., description="Lesson identifier")
    concept_title: str = Field(..., description="Concept title being taught")
    question_prompt: str = Field(..., description="The challenge question or scenario")
    candidate_thoughts: str = Field(..., min_length=1, max_length=10000, description="Candidate's approach or thoughts")
    candidate_code: Optional[str] = Field(None, max_length=20000, description="Optional candidate workspace code")
    role: Optional[str] = Field("Software Engineer (SDE)", max_length=100)
    language: Optional[str] = Field("en", max_length=10)


class TeachingEvaluationResponse(BaseModel):
    what_is_right: str = Field(..., description="Detailed affirmation of what the candidate got right")
    what_is_wrong: str = Field(..., description="Constructive breakdown of errors, omissions, or sub-optimal bounds")
    masterclass_lesson: str = Field(..., description="Comprehensive concept masterclass, mental model, and framework")
    optimal_solution: str = Field(..., description="Optimal code snippet or architectural diagram blueprint")
    key_takeaway: str = Field(..., description="The single most important principle to remember")
    suggested_follow_up: Optional[str] = Field(None, description="Check-in concept question")
    next_lesson_id: Optional[str] = None


class TeachingLesson(BaseModel):
    id: str
    title: str
    topic: str
    difficulty: str
    concept_summary: str
    challenge_question: str
    grounding_source: str
    stage_number: Optional[int] = 1
    stage_name: Optional[str] = "Foundations"
    learning_objective: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    diagnostic_question: Optional[str] = None
    source_references: List[str] = Field(default_factory=list)
    starter_code: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    status: Optional[str] = "not_started"
    current_stage: Optional[str] = "objective"
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    assessment_question: Optional[str] = None
    practice_exercise: Optional[str] = None
    why_matters_for_role: Optional[str] = None
    candidate_project_connection: Optional[str] = None
    estimated_effort_minutes: Optional[int] = 25
    code_walkthrough: Optional[str] = None
    repo_file_citations: List[Dict[str, Any]] = Field(default_factory=list)
    is_demonstrated: bool = False
    masterclass_solution: Optional[str] = None
    status_type: Optional[str] = "recommended"
    # Comprehensive 15-section structured teaching fields
    what_it_is: Optional[str] = None
    why_it_exists: Optional[str] = None
    detailed_explanation: Optional[str] = None
    terminology_and_mental_models: Optional[str] = None
    expected_output: Optional[str] = None
    debugging_tips: Optional[str] = None
    edge_cases_and_limitations: Optional[str] = None
    real_world_applications: Optional[str] = None
    interview_questions: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    practice_exercises: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    knowledge_check_questions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    verified_resources_count: Optional[int] = 0
    what_you_will_learn: Optional[List[str]] = Field(default_factory=list)
    key_takeaways: Optional[List[str]] = Field(default_factory=list)
    duration: Optional[str] = "12 min"
    quick_check: Optional[Dict[str, Any]] = None


class TeachingLessonDetailRequest(BaseModel):
    skill: str = Field(..., description="Selected resume skill, e.g. Python, React.js, LangChain")
    concept_title: Optional[str] = Field(None, description="Target concept title")
    concept: Optional[str] = Field(None, description="Alias for concept_title")
    lesson_id: Optional[str] = Field(None, description="Optional lesson identifier")
    learner_level: Optional[str] = Field("Intermediate", description="Beginner, Intermediate, or Advanced")
    requested_section: Optional[str] = Field(None, description="Optional specific section requested")
    section: Optional[str] = Field(None, description="Alias for requested_section")
    ai_generated: Optional[bool] = Field(False, description="When True, use AI-driven lesson generation instead of curated templates")


class TeachingLessonDetailResponse(BaseModel):
    skill: str
    concept_title: str
    lesson_id: str
    learner_level: str = "Intermediate"
    lesson: TeachingLesson
    validation_status: str = "verified_relevant"  # "verified_relevant" | "fallback_curated" | "insufficient_source"
    validation_details: Optional[str] = None
    relevance_status: Optional[str] = "verified"
    relevance_reason: Optional[str] = None
    citations: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class TeachingSection(BaseModel):
    id: str
    title: str
    badge: str
    description: str
    icon: str
    accent_color: str
    grounding_platforms: List[str]
    lessons: List[TeachingLesson]


class TeachingCurriculumResponse(BaseModel):
    sections: List[TeachingSection]
    total_lessons: int
    candidate_name: str
    target_role: str
    recommended_start_lesson_id: Optional[str] = None
    knowledge_profile_summary: Optional[Dict[str, Any]] = None


class TeachingInteractionRequest(BaseModel):
    section_id: str
    lesson_id: str
    action: str = Field("answer", description="'answer' | 'hint' | 'simpler' | 'explain' | 'code' | 'why' | 'practice' | 'assess' | 'next_stage'")
    candidate_response: Optional[str] = None
    candidate_code: Optional[str] = None
    code_language: Optional[str] = "python"
    language: Optional[str] = "en"
    current_step: int = 1
    current_stage: Optional[str] = "objective"
    chat_history: Optional[List[Dict[str, Any]]] = None
    mode: Optional[str] = None
    target_id: Optional[str] = None


class TeachingInteractionResponse(BaseModel):
    section_id: str
    lesson_id: str
    action: str
    teaching_message: str
    current_stage: str = "objective"
    next_stage: Optional[str] = None
    what_is_right: Optional[str] = None
    what_is_wrong: Optional[str] = None
    step_by_step_explanation: Optional[str] = None
    example_grounding: Optional[str] = None
    code_demonstration: Optional[str] = None
    follow_up_question: Optional[str] = None
    hint_revealed: Optional[str] = None
    practice_exercise: Optional[str] = None
    assessment_evaluation: Optional[Dict[str, Any]] = None
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    is_lesson_complete: bool = False
    mastery_status: str = "in_progress"  # "in_progress" | "completed" | "mastered" | "needs_revision" | "demonstrated_understanding"
    recommended_next_lesson_id: Optional[str] = None
    suggested_follow_ups: List[str] = Field(default_factory=list)
    repo_file_citations: List[Dict[str, Any]] = Field(default_factory=list)


class TeachingProgressResponse(BaseModel):
    completed_lessons: List[str] = Field(default_factory=list)
    mastered_lessons: List[str] = Field(default_factory=list)
    section_progress: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    lesson_stages: Dict[str, str] = Field(default_factory=dict)
    mastery_evidence: Dict[str, Any] = Field(default_factory=dict)


# ── MODE A: SKILL LEARNING PATH SCHEMAS ────────────────────────────────────────
class SkillCurriculumStage(BaseModel):
    stage_number: int
    stage_name: str
    description: str
    estimated_hours: Optional[float] = 2.0
    lessons: List[TeachingLesson]


class SkillLearningPathResponse(BaseModel):
    skill_name: str
    normalized_skill: str
    summary: str
    prerequisites: List[str] = Field(default_factory=list)
    stages: List[SkillCurriculumStage]
    total_stages: int
    total_lessons: int
    diagnostic_question: Optional[str] = None
    demonstrated_lessons_count: int = 0
    recommended_start_lesson_id: Optional[str] = None
    connected_projects: List[Dict[str, Any]] = Field(default_factory=list)
    related_skills: List[str] = Field(default_factory=list)


# ── MODE B: REPOSITORY UNDERSTANDING & LEARNING PATH SCHEMAS ──────────────────
class RepositoryComponent(BaseModel):
    name: str
    responsibility: str
    key_files: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class RepositoryUnderstandingModel(BaseModel):
    repository_id: int
    repository_name: str
    full_name: str
    project_purpose: str
    main_technologies: List[str] = Field(default_factory=list)
    repository_structure: List[str] = Field(default_factory=list)
    major_components: List[RepositoryComponent] = Field(default_factory=list)
    application_entry_points: List[str] = Field(default_factory=list)
    request_flow: str
    database_flow: str
    auth_security_flow: str
    external_integrations: List[str] = Field(default_factory=list)
    algorithms_business_logic: List[Dict[str, Any]] = Field(default_factory=list)
    error_handling_and_tests: str
    deployment_and_config: str
    architectural_strengths: List[str] = Field(default_factory=list)
    potential_improvement_areas: List[str] = Field(default_factory=list)
    source_evidence_citations: List[Dict[str, Any]] = Field(default_factory=list)
    is_limited_to_readme: bool = False
    source_file_count: int = 0
    freshness_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ProjectInterviewPrepModule(BaseModel):
    repository_name: str
    short_introduction: str
    architecture_walkthrough: str
    technical_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    important_code_walkthrough: List[Dict[str, Any]] = Field(default_factory=list)
    challenges_and_improvements: Dict[str, Any] = Field(default_factory=dict)
    sample_interview_answers: List[Dict[str, str]] = Field(default_factory=list)
    practice_interview_questions: List[str] = Field(default_factory=list)


class ProjectLearningJourneyResponse(BaseModel):
    repository_id: int
    repository_name: str
    repository_url: Optional[str] = None
    primary_language: Optional[str] = None
    understanding_model: RepositoryUnderstandingModel
    stages: List[SkillCurriculumStage]
    total_stages: int
    total_lessons: int
    interview_prep: ProjectInterviewPrepModule
    recommended_start_lesson_id: Optional[str] = None


# ── CONVERSATIONAL TUTOR (DR. CYRA VANCE) SCHEMAS ────────────────────────────
class TeachingChatTurn(BaseModel):
    role: str = Field(..., description="'user' | 'cyra' | 'system'")
    content: str
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    is_assessment: bool = False


class TeachingChatRequest(BaseModel):
    mode: str = Field("skill", description="'skill' | 'project' | 'dsa' | 'resume'")
    target_id: str = Field(..., description="Skill name (e.g. 'React') or repository id/name")
    lesson_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=10000)
    chat_history: List[TeachingChatTurn] = Field(default_factory=list)
    is_assessment: bool = False
    code_workspace: Optional[str] = None
    workspace_code: Optional[str] = None
    repository_id: Optional[int] = None
    file_path: Optional[str] = None
    file_id: Optional[int] = None
    active_file_content: Optional[str] = None
    language: Optional[str] = "en"


class TeachingChatResponse(BaseModel):
    reply: str
    teaching_mode: str
    target_id: str
    lesson_id: Optional[str] = None
    file_path: Optional[str] = None
    current_stage: str = "explanation"
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    companion_files: List[Dict[str, Any]] = Field(default_factory=list)
    suggested_follow_ups: List[str] = Field(default_factory=list)
    is_assessment: bool = False
    assessment_evaluation: Optional[Dict[str, Any]] = None
    demonstrated_understanding: bool = False
    recommended_next_action: Optional[str] = None
    audio_narrative: Optional[str] = None
    limitations: Optional[str] = None


# ── CODE UNDERSTANDING & FILE EXPLANATION SCHEMAS ────────────────────────────
class CodeQuestionRequest(BaseModel):
    repository_id: int
    file_id: Optional[int] = None
    file_path: Optional[str] = None
    category: Optional[str] = None


class CodeQuestionResponse(BaseModel):
    question_title: str
    question_prompt: str
    file_path: str
    code_snippet: str
    start_line: int = 1
    end_line: int = 1
    hints: List[str] = Field(default_factory=list)
    key_concept: str


class FileExplanationRequest(BaseModel):
    repository_id: int
    file_id: Optional[int] = None
    file_path: Optional[str] = None
    file_content: Optional[str] = None


class FileExplanationResponse(BaseModel):
    file_path: str
    file_responsibility: str
    why_it_exists: str
    important_symbols: List[Dict[str, Any]] = Field(default_factory=list)
    execution_flow: str
    dependencies: List[str] = Field(default_factory=list)
    programming_concepts: List[str] = Field(default_factory=list)
    edge_cases_and_security: str
    practical_example: str
    code_snippet: str
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    companion_files: List[Dict[str, Any]] = Field(default_factory=list)
    step_by_step_walkthrough: Optional[str] = None
    loop_conditions_and_structure: Optional[str] = None
    expected_output: Optional[str] = None
    limitations: Optional[str] = None
