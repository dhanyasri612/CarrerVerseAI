from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.user import User
from app.parsers.skill_normalizer import get_canonical_skill_name


SKILL_LEARNING_PATHS = {
    "python": "Master Python fundamentals, OOP, data structures, asynchronous programming, and typing.",
    "fastapi": "Master FastAPI routing, request validation with Pydantic, dependency injection, and asynchronous API performance.",
    "postgresql": "Learn PostgreSQL relational modeling, indexing, query optimization, joins, and transactions.",
    "docker": "Master containerization, multi-stage Dockerfiles, networking, volumes, and Docker Compose.",
    "javascript": "Master ES6+ features, closures, event loop, asynchronous promises/async-await, and DOM manipulation.",
    "typescript": "Master TypeScript static typing, generics, interfaces, union types, and tsconfig tooling.",
    "react": "Master React functional components, hooks, state management, routing, and component architecture.",
    "next.js": "Learn Next.js server-side rendering (SSR), static site generation (SSG), App Router, and full-stack API routes.",
    "node.js": "Master Node.js event-driven architecture, Express/Fastify APIs, middleware, and streams.",
    "mongodb": "Learn MongoDB document modeling, indexing, aggregation pipelines, and schema validation.",
    "redis": "Master Redis in-memory data structures, caching patterns, pub/sub, and session management.",
    "aws": "Master core AWS services: EC2, S3, RDS, Lambda, IAM, API Gateway, and CloudFront.",
    "azure": "Learn Azure compute, App Services, Blob Storage, Azure SQL, and Azure Active Directory.",
    "google cloud platform": "Learn GCP compute engine, Cloud Run, BigQuery, Cloud Storage, and IAM.",
    "kubernetes": "Master Kubernetes architecture: Pods, Deployments, Services, ConfigMaps, Ingress, and Helm.",
    "ci/cd": "Master CI/CD pipelines with GitHub Actions or GitLab CI, automated testing, and automated deployment.",
    "machine learning": "Master supervised/unsupervised learning, scikit-learn, feature engineering, and model evaluation.",
    "deep learning": "Learn PyTorch/TensorFlow, neural networks, backpropagation, CNNs, RNNs, and transformer architectures.",
    "generative ai": "Learn LLM architectures, prompt engineering, RAG (Retrieval-Augmented Generation), embeddings, and LangChain/LlamaIndex.",
    "prompt engineering": "Master system prompt design, few-shot prompting, chain-of-thought, and LLM output structuring.",
    "data structures & algorithms": "Master arrays, hash maps, linked lists, trees, graphs, dynamic programming, and LeetCode problem patterns.",
    "sql": "Master relational database querying, window functions, subqueries, CTEs, and query execution plans.",
    "git": "Master Git version control, branching workflows, rebasing, merge conflict resolution, and PR reviews."
}


def analyze_career_roadmap(
    db: Session,
    resume_id: int,
    job_id: int,
    current_user: User
):
    # 1. Check resume ownership
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # 2. Get parsed resume
    parsed_resume = (
        db.query(ParsedResume)
        .filter(
            ParsedResume.resume_id == resume.id
        )
        .first()
    )

    if not parsed_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parsed resume not found"
        )

    # 3. Get target job
    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # 4. Normalize resume skills
    current_skills_map = {}
    for skill in (parsed_resume.skills or []):
        if skill and isinstance(skill, str):
            canonical = get_canonical_skill_name(skill)
            if canonical:
                current_skills_map[canonical.lower()] = canonical

    # 5. Normalize required job skills
    required_skills_map = {}
    for skill in (job.required_skills or []):
        if skill and isinstance(skill, str):
            canonical = get_canonical_skill_name(skill)
            if canonical:
                required_skills_map[canonical.lower()] = canonical

    # 6. Find missing skills
    missing_keys = set(required_skills_map.keys()) - set(current_skills_map.keys())
    missing_skills = [required_skills_map[k] for k in sorted(missing_keys)]
    current_skills = sorted(list(current_skills_map.values()))

    # 7. Create roadmap
    roadmap = []
    for index, skill_name in enumerate(missing_skills, start=1):
        description = SKILL_LEARNING_PATHS.get(
            skill_name.lower(),
            f"Master {skill_name} fundamentals, explore industry best practices, and build real-world portfolio projects."
        )

        roadmap.append({
            "step": index,
            "skill": skill_name,
            "description": description
        })

    return {
        "resume_id": resume_id,
        "job_id": job_id,
        "current_skills": current_skills,
        "missing_skills": missing_skills,
        "roadmap": roadmap
    }