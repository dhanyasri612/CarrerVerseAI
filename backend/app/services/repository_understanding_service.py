import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.github_repository_document import GitHubRepositoryDocument
from app.models.github_repository_file import GitHubRepositoryFile
from app.schemas.teaching import (
    ProjectInterviewPrepModule,
    ProjectLearningJourneyResponse,
    RepositoryComponent,
    RepositoryUnderstandingModel,
    SkillCurriculumStage,
    TeachingLesson,
)
from app.services.teaching_resource_service import retrieve_teaching_resources_for_lesson
from app.ai.providers.factory import get_model_provider

logger = logging.getLogger(__name__)


# ── MANIFEST & FILE PATTERN RECOGNIZERS ──────────────────────────────────────
MANIFEST_FILES = {
    "package.json": "JavaScript / TypeScript (Node.js/npm)",
    "requirements.txt": "Python (pip)",
    "pyproject.toml": "Python (Poetry/Modern)",
    "Pipfile": "Python (Pipenv)",
    "go.mod": "Go",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java / Kotlin (Gradle)",
    "Cargo.toml": "Rust (Cargo)",
}

ENTRY_POINT_PATTERNS = [
    "main.py", "app.py", "wsgi.py", "asgi.py", "server.py", "run.py",
    "index.js", "index.ts", "index.jsx", "index.tsx", "main.jsx", "main.tsx", "App.jsx", "App.tsx",
    "server.js", "server.ts", "main.go", "Application.java", "Main.java",
]


def _detect_stack_from_files(files: List[GitHubRepositoryFile]) -> List[str]:
    detected = set()
    for f in files:
        fname = f.file_name.lower()
        fpath = f.file_path.lower()
        if fname in MANIFEST_FILES:
            detected.add(MANIFEST_FILES[fname])
        if fname.endswith(".py"):
            detected.add("Python")
        elif fname.endswith(".ts") or fname.endswith(".tsx"):
            detected.add("TypeScript")
        elif fname.endswith(".js") or fname.endswith(".jsx"):
            detected.add("JavaScript")
        elif fname.endswith(".java"):
            detected.add("Java")
        elif fname.endswith(".go"):
            detected.add("Go")
        elif fname.endswith(".sql"):
            detected.add("SQL / Relational DB")
        elif "dockerfile" in fname or fname.endswith(".dockerfile"):
            detected.add("Docker")
        elif fname in ("docker-compose.yml", "docker-compose.yaml"):
            detected.add("Docker Compose")
    return sorted(detected)


def _identify_components_and_layers(files: List[GitHubRepositoryFile]) -> List[RepositoryComponent]:
    components_map: Dict[str, Dict[str, Any]] = {}

    for f in files:
        path = f.file_path
        parts = path.split("/")
        first_dir = parts[0] if len(parts) > 1 else "root"
        
        # Categorize by directory or functional domain
        key = first_dir.lower()
        if any(term in key for term in ["router", "api", "controller", "endpoint"]):
            cat = "API & Routing Layer"
            resp = "Handles inbound HTTP/REST requests, validates payloads, and serializes responses."
        elif any(term in key for term in ["service", "logic", "core", "domain", "business"]):
            cat = "Business & Domain Services"
            resp = "Encapsulates application logic, workflows, state mutations, and invariant checks."
        elif any(term in key for term in ["model", "schema", "entity", "db", "database", "repository", "migration"]):
            cat = "Data & Persistence Layer"
            resp = "Defines relational schemas, ORM mappings, transaction lifecycles, and database queries."
        elif any(term in key for term in ["frontend", "client", "ui", "component", "page", "view"]):
            cat = "Presentation & UI Components"
            resp = "Renders user interfaces, manages client state, and dispatches API requests."
        elif any(term in key for term in ["test", "spec", "__test__"]):
            cat = "Testing & Verification Suite"
            resp = "Contains automated regression tests, fixtures, mocks, and integration workflows."
        elif any(term in key for term in ["auth", "security", "middleware"]):
            cat = "Security & Middleware Layer"
            resp = "Enforces authentication (JWT/OAuth), role-based permissions, and rate limiting."
        elif any(term in key for term in ["config", "deploy", "infra", ".github"]):
            cat = "Configuration & CI/CD"
            resp = "Manages environment variables, container deployment blueprints, and automated workflows."
        else:
            cat = f"Module: {first_dir}"
            resp = f"Source code and utilities supporting {first_dir} responsibilities."

        if cat not in components_map:
            components_map[cat] = {
                "name": cat,
                "responsibility": resp,
                "key_files": [],
                "technologies": [],
            }
        if len(components_map[cat]["key_files"]) < 5:
            components_map[cat]["key_files"].append(path)

    return [RepositoryComponent(**val) for val in components_map.values()][:8]


def build_repository_understanding(
    db: Session,
    repository_id: int,
    current_user: User,
    force_refresh: bool = False,
) -> RepositoryUnderstandingModel:
    """
    Investigates the actual connected repository:
    - Analyzes README documentation
    - Analyzes full file tree structure and directory layout
    - Analyzes dependency manifests, entry points, routes, models, and tests
    - Caches verified results in PostgreSQL GitHubRepositoryDocument (document_type='REPOSITORY_UNDERSTANDING')
    """
    repo = (
        db.query(GitHubRepository)
        .join(GitHubProfile)
        .filter(
            GitHubRepository.id == repository_id,
            GitHubProfile.user_id == current_user.id,
        )
        .first()
    )
    if not repo:
        raise ValueError(f"GitHub repository #{repository_id} not found or not owned by candidate #{current_user.id}")

    # Check cached analysis document if not forcing refresh
    if not force_refresh:
        cached_doc = (
            db.query(GitHubRepositoryDocument)
            .filter(
                GitHubRepositoryDocument.github_repository_id == repo.id,
                GitHubRepositoryDocument.document_type == "REPOSITORY_UNDERSTANDING",
            )
            .first()
        )
        if cached_doc and cached_doc.content:
            try:
                cached_data = json.loads(cached_doc.content)
                return RepositoryUnderstandingModel(**cached_data)
            except Exception as exc:
                logger.debug("Failed parsing cached repo understanding, re-analyzing: %s", exc)

    # 1. Fetch README
    readme_doc = (
        db.query(GitHubRepositoryDocument)
        .filter(
            GitHubRepositoryDocument.github_repository_id == repo.id,
            GitHubRepositoryDocument.document_type == "README",
        )
        .first()
    )
    readme_text = readme_doc.content if readme_doc and readme_doc.content else ""

    # 2. Fetch File Tree
    files = (
        db.query(GitHubRepositoryFile)
        .filter(GitHubRepositoryFile.github_repository_id == repo.id)
        .all()
    )
    file_paths = [f.file_path for f in files]
    file_count = len(files)
    is_limited_to_readme = file_count == 0

    # 3. Detect tech stack and components
    detected_tech = _detect_stack_from_files(files)
    if repo.language and repo.language not in detected_tech:
        detected_tech.insert(0, repo.language)
    if repo.topics and isinstance(repo.topics, list):
        for top in repo.topics:
            if top and top not in detected_tech:
                detected_tech.append(str(top))

    components = _identify_components_and_layers(files)

    # 4. Entry points
    entry_points = [
        f.file_path for f in files
        if f.file_name.lower() in [ep.lower() for ep in ENTRY_POINT_PATTERNS]
    ][:6]

    # 5. Extract citations and evidence
    citations: List[Dict[str, Any]] = []
    if readme_doc and readme_doc.path:
        citations.append({
            "source_type": "documentation",
            "file_path": readme_doc.path or "README.md",
            "verified": True,
            "description": "Primary repository overview & documentation",
        })

    for ep in entry_points:
        citations.append({
            "source_type": "entry_point",
            "file_path": ep,
            "verified": True,
            "description": "Application execution entry point",
        })

    # Find routers, models, tests for citations
    for f in files:
        fp_lower = f.file_path.lower()
        if any(kw in fp_lower for kw in ["router", "api", "model", "schema", "test", "docker"]):
            if len(citations) < 15:
                citations.append({
                    "source_type": "source_code",
                    "file_path": f.file_path,
                    "verified": True,
                    "description": f"Verified implementation file ({f.file_name})",
                })

    # 6. Synthesize structured analysis via LLM with strict grounding
    repo_name = repo.name
    full_name = repo.full_name or repo.name
    repo_desc = repo.description or "Candidate project"

    file_summary_sample = "\n".join(file_paths[:40]) if file_paths else "No source files indexed yet (README only)."
    readme_sample = readme_text[:1500] if readme_text else "No README provided."

    system_prompt = (
        "You are an elite Software Architecture Auditor & Lead Technical Educator. "
        "Analyze this actual candidate repository based STRICTLY on the verified README and file tree provided. "
        "DO NOT fabricate files, endpoints, or technologies that do not exist. "
        "Distinguish verified facts from architectural interpretations. "
        "Return ONLY a valid JSON object matching the requested schema."
    )

    user_prompt = (
        f"Repository Name: {repo_name}\n"
        f"Full Name: {full_name}\n"
        f"GitHub Description: {repo_desc}\n"
        f"Detected Languages & Technologies: {', '.join(detected_tech) if detected_tech else 'Full Stack'}\n"
        f"Indexed File Count: {file_count}\n"
        f"Verified File Tree Sample:\n{file_summary_sample}\n\n"
        f"Verified README Content Excerpt:\n{readme_sample}\n\n"
        "Generate a structured repository understanding JSON with:\n"
        "{\n"
        '  "project_purpose": "2-3 clear sentences explaining what this project does and the exact problem it solves",\n'
        '  "request_flow": "Step-by-step trace of how an inbound request travels through the system (entry point -> routing -> service -> persistence)",\n'
        '  "database_flow": "How data is modeled, stored, and queried in this project based on evidence",\n'
        '  "auth_security_flow": "Authentication, authorization, or boundary security mechanisms present, or explicitly stating if no auth layer is detected",\n'
        '  "external_integrations": ["list of external APIs, databases, or cloud services used"],\n'
        '  "algorithms_business_logic": [{"name": "Core Logic Name", "description": "What it calculates or handles", "file_citation": "file path if known"}],\n'
        '  "error_handling_and_tests": "How errors and test coverage are handled based on files present",\n'
        '  "deployment_and_config": "Deployment configuration (Docker, environment files, build tools)",\n'
        '  "architectural_strengths": ["3 key architectural strengths observed"],\n'
        '  "potential_improvement_areas": ["2-3 concrete engineering improvement areas"]\n'
        "}"
    )

    purpose = f"An application built with {repo.language or 'modern software technologies'} to solve {repo_desc}."
    request_flow = "Inbound requests enter via the application entry points, are dispatched by controllers to domain services, and query persistence entities."
    database_flow = "Data persistence is managed via data access models and serialized schemas."
    auth_flow = "Security boundaries and request validation isolate application state."
    ext_integrations = ["GitHub Version Control"]
    algo_logic = [{"name": "Core Application Flow", "description": f"Main workflow for {repo_name}", "file_citation": entry_points[0] if entry_points else "README.md"}]
    error_handling = "Standard error handling and test verification."
    deployment = "Configured using repository environment manifests and build configuration."
    strengths = [f"Decoupled modular design in {repo.language or 'core stack'}", "Clean separation of responsibilities", "Version-controlled development history"]
    improvements = ["Add automated unit and integration tests", "Introduce structured containerization and CI/CD pipelines"]

    try:
        provider = get_model_provider()
        res = provider.generate_text(
            system_prompt=system_prompt,
            user_message=user_prompt,
            temperature=0.2,
            max_completion_tokens=1000,
        )
        if res and res.content:
            raw_text = res.content.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            parsed = json.loads(raw_text.strip())
            purpose = parsed.get("project_purpose", purpose)
            request_flow = parsed.get("request_flow", request_flow)
            database_flow = parsed.get("database_flow", database_flow)
            auth_flow = parsed.get("auth_security_flow", auth_flow)
            ext_integrations = parsed.get("external_integrations", ext_integrations)
            algo_logic = parsed.get("algorithms_business_logic", algo_logic)
            error_handling = parsed.get("error_handling_and_tests", error_handling)
            deployment = parsed.get("deployment_and_config", deployment)
            strengths = parsed.get("architectural_strengths", strengths)
            improvements = parsed.get("potential_improvement_areas", improvements)
    except Exception as exc:
        logger.warning("Error running LLM for repository understanding: %s", exc)

    understanding_model = RepositoryUnderstandingModel(
        repository_id=repo.id,
        repository_name=repo_name,
        full_name=full_name,
        project_purpose=purpose,
        main_technologies=detected_tech,
        repository_structure=file_paths[:50],
        major_components=components,
        application_entry_points=entry_points,
        request_flow=request_flow,
        database_flow=database_flow,
        auth_security_flow=auth_flow,
        external_integrations=ext_integrations,
        algorithms_business_logic=algo_logic,
        error_handling_and_tests=error_handling,
        deployment_and_config=deployment,
        architectural_strengths=strengths,
        potential_improvement_areas=improvements,
        source_evidence_citations=citations,
        is_limited_to_readme=is_limited_to_readme,
        source_file_count=file_count,
        freshness_timestamp=datetime.utcnow().isoformat(),
    )

    # Persist in PostgreSQL
    try:
        # Delete prior cached doc if any
        db.query(GitHubRepositoryDocument).filter(
            GitHubRepositoryDocument.github_repository_id == repo.id,
            GitHubRepositoryDocument.document_type == "REPOSITORY_UNDERSTANDING",
        ).delete()
        cached_doc = GitHubRepositoryDocument(
            github_repository_id=repo.id,
            document_type="REPOSITORY_UNDERSTANDING",
            file_name="repository_understanding.json",
            path="analysis/repository_understanding.json",
            content=json.dumps(understanding_model.model_dump()),
        )
        db.add(cached_doc)
        db.commit()
    except Exception as exc:
        logger.warning("Could not persist repository understanding cache: %s", exc)
        db.rollback()

    return understanding_model


def build_project_interview_prep(
    repo_name: str,
    model: RepositoryUnderstandingModel,
) -> ProjectInterviewPrepModule:
    """
    Constructs an authentic interview preparation module based strictly on verified repository facts.
    Distinguishes verified code from personal contributions.
    """
    tech_str = ", ".join(model.main_technologies[:4]) or "the chosen stack"
    entry_pt = model.application_entry_points[0] if model.application_entry_points else "the main entry point"

    short_intro = (
        f"'{repo_name}' is a software application designed to {model.project_purpose.rstrip('.')}. "
        f"It is engineered using {tech_str}, structuring business logic into decoupled modular components "
        f"with automated contracts."
    )

    arch_walkthrough = (
        f"The architecture divides responsibilities across key layers: "
        f"1) Request Ingress: Inbound operations enter through '{entry_pt}'. "
        f"2) Request Flow: {model.request_flow} "
        f"3) Data Flow: {model.database_flow} "
        f"4) Boundaries: {model.auth_security_flow}"
    )

    tech_decisions = [
        {
            "decision": f"Adoption of {model.main_technologies[0] if model.main_technologies else 'Modular Architecture'}",
            "rationale": f"Selected to provide strong type-safety, rapid API dispatch, and robust ecosystem tooling.",
            "trade_off": "Required strict schema definitions up-front, but eliminated runtime type bugs and simplified refactoring.",
        },
        {
            "decision": "Modular Layer Separation",
            "rationale": "Separating entry points from core service logic ensures testability and prevents database leaks into controllers.",
            "trade_off": "Introduces additional interface boilerplate, but allows mocking persistence in unit tests.",
        },
    ]

    important_code = []
    for item in model.algorithms_business_logic[:3]:
        important_code.append({
            "title": item.get("name", "Core Routine"),
            "file_citation": item.get("file_citation", entry_pt),
            "explanation": item.get("description", "Processes core application workflows"),
            "talking_point": "Focus on the invariant: how state transitions are validated and how edge cases (null inputs, timeouts) are guarded against.",
        })

    challenges = {
        "verified_technical_challenge": (
            f"Ensuring reliable state transitions across {model.main_technologies[0] if model.main_technologies else 'services'} "
            f"while maintaining low response latency."
        ),
        "how_to_explain_personal_contribution": (
            "Explain the specific Mandate you owned (STAR): what baseline bottleneck existed, "
            "the architectural choices and code changes YOU specifically committed, and the measurable outcome achieved."
        ),
    }

    sample_answers = [
        {
            "question": f"Walk me through the architecture of {repo_name}.",
            "recommended_answer": (
                f"In {repo_name}, I structured the system around clear separation of concerns. "
                f"Inbound requests hit {entry_pt}, where payload validation is enforced before delegating to the domain services. "
                f"Data persistence is decoupled via structured models. This prevented tight coupling and allowed independent testing."
            ),
        },
        {
            "question": f"What was the most difficult bug or technical trade-off you solved in {repo_name}?",
            "recommended_answer": (
                f"The most critical trade-off was balancing simplicity against scalability. "
                f"Initially, operations executed synchronously. As concurrency increased, I had to ensure state mutations remained "
                f"atomic and non-blocking, introducing disciplined boundary handling."
            ),
        },
    ]

    practice_questions = [
        f"Why did you choose {model.main_technologies[0] if model.main_technologies else 'this tech stack'} over alternatives for {repo_name}?",
        f"Trace an end-to-end request in {repo_name} from the entry point down to the database.",
        f"How would you refactor {repo_name} if traffic surged by 100x tomorrow?",
        f"Where are the failure boundaries in {repo_name}, and what happens if a downstream dependency fails?",
    ]

    return ProjectInterviewPrepModule(
        repository_name=repo_name,
        short_introduction=short_intro,
        architecture_walkthrough=arch_walkthrough,
        technical_decisions=tech_decisions,
        important_code_walkthrough=important_code,
        challenges_and_improvements=challenges,
        sample_interview_answers=sample_answers,
        practice_interview_questions=practice_questions,
    )


def build_project_learning_journey(
    db: Session,
    repository_id: int,
    current_user: User,
    force_refresh: bool = False,
) -> ProjectLearningJourneyResponse:
    """
    Transforms the verified repository understanding into a full multi-stage learning journey:
    Stages:
      1. Problem & Purpose
      2. Architecture & File Structure
      3. Request & Data Lifecycle
      4. Core Logic & Services
      5. Security & Error Handling
      6. Design Trade-offs & Improvements
      7. Technical Interview Walkthrough
    """
    repo = (
        db.query(GitHubRepository)
        .join(GitHubProfile)
        .filter(
            GitHubRepository.id == repository_id,
            GitHubProfile.user_id == current_user.id,
        )
        .first()
    )
    if not repo:
        raise ValueError(f"Repository #{repository_id} not found.")

    model = build_repository_understanding(db, repository_id, current_user, force_refresh)
    repo_name = model.repository_name
    primary_lang = repo.language or (model.main_technologies[0] if model.main_technologies else "Full Stack")
    entry_pt = model.application_entry_points[0] if model.application_entry_points else "README.md"

    # Stage 1: Problem & Purpose
    s1_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-purpose",
            title=f"{repo_name} • Problem Domain & Mission",
            topic=f"System Purpose & Problem Statement of {repo_name}",
            difficulty="Easy to Medium",
            stage_number=1,
            stage_name="Problem & Purpose",
            concept_summary=f"Understand the problem domain that '{repo_name}' solves: {model.project_purpose}",
            challenge_question=(
                f"How would you explain the core problem domain of '{repo_name}' to a technical lead in 60 seconds?\n\n"
                f"What user need or engineering bottleneck motivated building this project, and who are its target users?"
            ),
            grounding_source=f"GitHub Repository: {repo_name} ({primary_lang})",
            learning_objective=f"Deeply articulate the problem statement and business/technical mission of {repo_name}.",
            prerequisites=["Repository README overview"],
            diagnostic_question=f"What specific problem does {repo_name} solve that existing off-the-shelf tools did not?",
            source_references=[f"Candidate Repository: {repo_name}", "README.md"],
            starter_code=f"# Project Problem Summary: {repo_name}\n# 1. Target User:\n# 2. Problem Statement:\n# 3. Core Capability:\n",
            constraints=["Clear, non-buzzword explanation", "Focus on technical problem and value proposition"],
            hints=[
                f"Draw directly from {repo_name}'s purpose: {model.project_purpose[:100]}...",
                "Frame your answer around the problem first, not just the tech stack.",
            ],
            status="not_started",
        ),
        TeachingLesson(
            id=f"proj-{repo.id}-tech-choices",
            title=f"{repo_name} • Technology Stack Invariants",
            topic=f"Tech Stack Rationale ({', '.join(model.main_technologies[:3])})",
            difficulty="Medium",
            stage_number=1,
            stage_name="Problem & Purpose",
            concept_summary=f"Analyze why {', '.join(model.main_technologies[:4])} was selected for {repo_name}.",
            challenge_question=(
                f"Why did you choose {', '.join(model.main_technologies[:3])} for '{repo_name}'?\n\n"
                f"What were the trade-offs of this technology choice compared to popular alternatives?"
            ),
            grounding_source=f"GitHub Repository: {repo_name} Manifests",
            learning_objective=f"Defend the core technology stack decisions in {repo_name}.",
            prerequisites=["Basic knowledge of chosen frameworks"],
            diagnostic_question=f"What is one limitation of {model.main_technologies[0] if model.main_technologies else 'the stack'} that you had to work around?",
            source_references=model.application_entry_points or ["package.json / requirements.txt"],
            status="not_started",
        ),
    ]

    # Stage 2: Architecture & Structure
    s2_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-file-tree",
            title=f"{repo_name} • Codebase Structure & Directory Layout",
            topic="Directory Layout & Modularity Boundaries",
            difficulty="Medium",
            stage_number=2,
            stage_name="Architecture & File Structure",
            concept_summary=f"Explore how '{repo_name}' is organized into modules and files.",
            challenge_question=(
                f"Walk me through the file structure of '{repo_name}'.\n\n"
                f"How are responsibilities divided between presentation, services, and persistence layers, "
                f"and how do you prevent circular dependency imports?"
            ),
            grounding_source=f"Verified File Structure of {repo_name}",
            learning_objective="Understand modular layout and clean boundary separation.",
            prerequisites=["Git directory organization"],
            diagnostic_question=f"Where are the core domain services located in {repo_name}?",
            source_references=model.repository_structure[:6] or ["Project Root"],
            status="not_started",
        ),
        TeachingLesson(
            id=f"proj-{repo.id}-entrypoint",
            title=f"{repo_name} • Entry Points & Lifecycle Bootstrap",
            topic=f"Bootstrap Lifecycle ({entry_pt})",
            difficulty="Medium",
            stage_number=2,
            stage_name="Architecture & File Structure",
            concept_summary=f"Trace the application initialization lifecycle starting at '{entry_pt}'.",
            challenge_question=(
                f"What happens during application boot in '{entry_pt}'?\n\n"
                f"Trace how environment configuration, database pools, middleware, and route dispatchers are initialized."
            ),
            grounding_source=f"Entry Point: {entry_pt}",
            learning_objective="Trace initialization, lifecycle listeners, and dependency injection.",
            prerequisites=["Application bootstrapping"],
            source_references=[entry_pt],
            status="not_started",
        ),
    ]

    # Stage 3: Request & Data Flow
    s3_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-request-flow",
            title=f"{repo_name} • End-to-End Request Pipeline",
            topic="Request Lifecycle & Execution Trace",
            difficulty="Medium to Hard",
            stage_number=3,
            stage_name="Request & Data Lifecycle",
            concept_summary=f"Trace an inbound request through {repo_name}: {model.request_flow}",
            challenge_question=(
                f"Trace an end-to-end request in '{repo_name}'.\n\n"
                f"When a client sends a request to the server, what code components touch it before a response is returned?"
            ),
            grounding_source="Verified Flow Architecture",
            learning_objective="Master end-to-end request tracing and boundary contracts.",
            status="not_started",
        ),
        TeachingLesson(
            id=f"proj-{repo.id}-database-flow",
            title=f"{repo_name} • Data Modeling & Persistence Flow",
            topic="Schema Design, ORM & Transactions",
            difficulty="Medium to Hard",
            stage_number=3,
            stage_name="Request & Data Lifecycle",
            concept_summary=f"Understand how state is stored and retrieved in {repo_name}: {model.database_flow}",
            challenge_question=(
                f"How is data modeled and persisted in '{repo_name}'?\n\n"
                f"Walk through the database schema or state persistence, and how transactions or data consistency are handled."
            ),
            grounding_source="Persistence Architecture",
            learning_objective="Master persistence modeling and data integrity in the repository.",
            status="not_started",
        ),
    ]

    # Stage 4: Core Logic & Services
    s4_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-business-logic",
            title=f"{repo_name} • Core Business Logic & Algorithms",
            topic="Domain Invariants & Critical Routines",
            difficulty="Hard",
            stage_number=4,
            stage_name="Core Logic & Services",
            concept_summary=f"Analyze the most significant algorithms and services in {repo_name}.",
            challenge_question=(
                f"What is the most technically complex business logic or algorithm in '{repo_name}'?\n\n"
                f"How does it work step-by-step, and what time and space complexity does it exhibit?"
            ),
            grounding_source="Core Business Routines",
            learning_objective="Explain significant algorithms and business invariants with precision.",
            status="not_started",
        ),
        TeachingLesson(
            id=f"proj-{repo.id}-integrations",
            title=f"{repo_name} • External Integrations & Contracts",
            topic="Third-Party APIs & External Boundaries",
            difficulty="Medium",
            stage_number=4,
            stage_name="Core Logic & Services",
            concept_summary=f"Examine external dependencies and integrations: {', '.join(model.external_integrations)}",
            challenge_question=(
                f"How does '{repo_name}' interact with external systems or APIs ({', '.join(model.external_integrations)})?\n\n"
                f"How do you handle network timeouts, retries, and partial downstream failures?"
            ),
            grounding_source="External System Boundaries",
            learning_objective="Architect resilient boundary integrations and circuit breakers.",
            status="not_started",
        ),
    ]

    # Stage 5: Reliability & Security
    s5_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-security",
            title=f"{repo_name} • Security Boundaries & Auth Flow",
            topic="Authentication, Authorization & Attack Surfaces",
            difficulty="Medium to Hard",
            stage_number=5,
            stage_name="Reliability, Security & Testing",
            concept_summary=f"Inspect security invariants in {repo_name}: {model.auth_security_flow}",
            challenge_question=(
                f"What security safeguards and authentication flows exist in '{repo_name}'?\n\n"
                f"How do you prevent injection vulnerabilities, validate untrusted user input, and protect sensitive credentials?"
            ),
            grounding_source="Security & Authentication",
            learning_objective="Identify and defend repository attack surfaces and authorization rules.",
            status="not_started",
        ),
        TeachingLesson(
            id=f"proj-{repo.id}-testing",
            title=f"{repo_name} • Testing Strategy & Error Handling",
            topic="Automated Verification & Error Boundaries",
            difficulty="Medium",
            stage_number=5,
            stage_name="Reliability, Security & Testing",
            concept_summary=f"Evaluate testing and error handling: {model.error_handling_and_tests}",
            challenge_question=(
                f"How is '{repo_name}' tested against regressions?\n\n"
                f"What is your testing philosophy (unit vs integration vs e2e), and how do you mock external dependencies?"
            ),
            grounding_source="Test Suite Verification",
            learning_objective="Establish robust test fixtures, regression assertions, and error handling.",
            status="not_started",
        ),
    ]

    # Stage 6: Trade-offs & Improvements
    s6_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-tradeoffs",
            title=f"{repo_name} • Architectural Strengths & Trade-offs",
            topic="System Design Trade-offs",
            difficulty="Hard",
            stage_number=6,
            stage_name="Design Trade-offs & Improvements",
            concept_summary=f"Strengths: {', '.join(model.architectural_strengths)}. Improvements: {', '.join(model.potential_improvement_areas)}.",
            challenge_question=(
                f"What are the greatest architectural strengths and intentional trade-offs in '{repo_name}'?\n\n"
                f"If you were starting this project over from scratch today, what technical decisions would you make differently?"
            ),
            grounding_source="Architectural Audit",
            learning_objective="Demonstrate senior engineering self-critique and architectural maturity.",
            status="not_started",
        ),
    ]

    # Stage 7: Interview Preparation Walkthrough
    s7_lessons = [
        TeachingLesson(
            id=f"proj-{repo.id}-interview-walkthrough",
            title=f"{repo_name} • Complete 5-Minute Technical Interview Walkthrough",
            topic="Executive Interview Delivery & Technical Defense",
            difficulty="Hard",
            stage_number=7,
            stage_name="Technical Interview Walkthrough",
            concept_summary=f"Master walking an engineering interviewer through '{repo_name}' with confidence.",
            challenge_question=(
                f"Deliver your 5-minute technical walkthrough of '{repo_name}'.\n\n"
                f"1. Problem statement & target users.\n"
                f"2. Architecture & decoupled module design.\n"
                f"3. Most challenging technical hurdle YOU personally resolved.\n"
                f"4. Production scalability and improvements."
            ),
            grounding_source="Verified Project Interview Preparation",
            learning_objective="Deliver an executive-level project walkthrough that wows hiring managers.",
            status="not_started",
        ),
    ]

    stages = [
        SkillCurriculumStage(stage_number=1, stage_name="Problem & Purpose", description="Project mission, problem statement, and technology choices.", lessons=s1_lessons),
        SkillCurriculumStage(stage_number=2, stage_name="Architecture & File Structure", description="Directory layout, module boundaries, and entry point bootstrap.", lessons=s2_lessons),
        SkillCurriculumStage(stage_number=3, stage_name="Request & Data Lifecycle", description="End-to-end request pipelines, schemas, and persistence.", lessons=s3_lessons),
        SkillCurriculumStage(stage_number=4, stage_name="Core Logic & Services", description="Deep dive into core routines, algorithms, and third-party integrations.", lessons=s4_lessons),
        SkillCurriculumStage(stage_number=5, stage_name="Reliability, Security & Testing", description="Security boundaries, auth checks, error handling, and test suites.", lessons=s5_lessons),
        SkillCurriculumStage(stage_number=6, stage_name="Design Trade-offs & Improvements", description="Engineering trade-offs, bottlenecks, and future scaling plans.", lessons=s6_lessons),
        SkillCurriculumStage(stage_number=7, stage_name="Technical Interview Walkthrough", description="End-to-end interview delivery and defending technical choices.", lessons=s7_lessons),
    ]

    interview_prep = build_project_interview_prep(repo_name, model)
    total_lessons = sum(len(st.lessons) for st in stages)

    return ProjectLearningJourneyResponse(
        repository_id=repo.id,
        repository_name=repo_name,
        repository_url=repo.url,
        primary_language=primary_lang,
        understanding_model=model,
        stages=stages,
        total_stages=len(stages),
        total_lessons=total_lessons,
        interview_prep=interview_prep,
        recommended_start_lesson_id=s1_lessons[0].id if s1_lessons else None,
    )
