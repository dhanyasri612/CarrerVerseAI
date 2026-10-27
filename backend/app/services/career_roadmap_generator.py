"""
Personalized Career Roadmap Generator and Adaptive Update Engine for CareerVerse AI.
Integrates unified multi-source candidate profiles (Resume, GitHub, LeetCode, Certifications)
with real-time technology trend intelligence and persistent PostgreSQL version tracking.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.career_roadmap import (
    CareerRoadmap,
    RoadmapVersion,
    RoadmapMilestone,
    RoadmapTrendSignal,
    RoadmapChangeLog,
)
from app.services.unified_profile_service import build_unified_candidate_profile
from app.services.trend_intelligence_service import trend_intelligence_service


ROLE_CURRICULUM_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "AI Engineer": [
        {
            "stage_order": 1,
            "title": "Python & Software Engineering Foundations for AI",
            "category": "Foundations",
            "description": "Master advanced Python 3.12+, asynchronous coroutines, type hints, object-oriented design, and Git development workflows.",
            "why_recommended": "Core software engineering discipline is mandatory for production AI systems and model serving pipelines.",
            "prerequisites": [],
            "estimated_effort": "2–3 weeks",
            "skills": ["Python", "Asyncio", "Object-Oriented Programming", "Git", "Typing"],
            "practical_project": "Build an asynchronous concurrent data scraper and cleaner with strict Pydantic models",
            "completion_criteria": [
                "Demonstrate asynchronous data processing with asyncio",
                "Write type-annotated, tested modular Python code",
                "Maintain clean Git version history with conventional commits"
            ],
            "learning_resources": [
                {"name": "Python Official Asyncio Documentation", "url": "https://docs.python.org/3/library/asyncio.html"},
                {"name": "Real Python: Modern Python 3 Idioms", "url": "https://realpython.com/"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Data Pipelines, Embeddings & Vector Retrieval",
            "category": "Data & Retrieval",
            "description": "Learn dense vector representations, chunking strategies, embedding models (OpenAI, HuggingFace), and vector store indices.",
            "why_recommended": "Semantic retrieval is the backbone of contextual AI applications and modern search systems.",
            "prerequisites": ["Python & Software Engineering Foundations for AI"],
            "estimated_effort": "2–3 weeks",
            "skills": ["Vector Embeddings", "ChromaDB", "pgvector", "Data Chunking", "Information Retrieval"],
            "practical_project": "Build a multi-document semantic search engine indexing PDFs and technical docs with pgvector",
            "completion_criteria": [
                "Implement hierarchical chunking with metadata preservation",
                "Index embeddings in ChromaDB / pgvector with cosine similarity",
                "Benchmark semantic retrieval latency and accuracy"
            ],
            "learning_resources": [
                {"name": "ChromaDB Documentation", "url": "https://docs.trychroma.com/"},
                {"name": "pgvector PostgreSQL Extension", "url": "https://github.com/pgvector/pgvector"}
            ]
        },
        {
            "stage_order": 3,
            "title": "Production RAG Application Engineering",
            "category": "RAG Architectures",
            "description": "Develop production Retrieval-Augmented Generation architectures with hybrid search (BM25 + Dense), re-ranking, and query decomposition.",
            "why_recommended": "Standard vector search fails on keyword-specific domain data. Enterprise AI demands hybrid reciprocal rank fusion.",
            "prerequisites": ["Data Pipelines, Embeddings & Vector Retrieval"],
            "estimated_effort": "3 weeks",
            "skills": ["RAG Architecture", "Hybrid Search", "Cohere Rerank", "Prompt Engineering", "FastAPI"],
            "practical_project": "Develop a hybrid RAG API with FastAPI, dense-sparse retrieval, and reciprocal rank fusion",
            "completion_criteria": [
                "Combine BM25 sparse search and dense embedding queries with RRF",
                "Incorporate cross-encoder re-ranking for top-5 document context",
                "Stream grounded responses with cited document references"
            ],
            "learning_resources": [
                {"name": "Cohere Rerank Documentation", "url": "https://docs.cohere.com/docs/rerank-overview"},
                {"name": "FastAPI Streaming Responses", "url": "https://fastapi.tiangolo.com/advanced/custom-response/"}
            ]
        },
        {
            "stage_order": 4,
            "title": "AI Agent Workflows & Multi-Agent Orchestration",
            "category": "Agentic Workflows",
            "description": "Orchestrate autonomous agent systems with LangGraph, cyclic execution, persistence checkpoints, and dynamic tool invocation.",
            "why_recommended": "Industry demands shifted from static one-shot prompts to stateful multi-step reasoning agents that interact with APIs.",
            "prerequisites": ["Production RAG Application Engineering"],
            "estimated_effort": "3 weeks",
            "skills": ["LangGraph", "Tool Calling", "Multi-Agent Coordination", "State Persistence", "Human-in-the-Loop"],
            "practical_project": "Build a multi-agent software architecture review assistant using LangGraph state graphs",
            "completion_criteria": [
                "Construct cyclic execution graphs with conditional edge branching",
                "Implement external API tool calling with JSON schemas",
                "Persist agent session memory across user turns with checkpoints"
            ],
            "learning_resources": [
                {"name": "LangGraph Official Guide", "url": "https://langchain-ai.github.io/langgraph/"},
                {"name": "OpenAI Function Calling Guide", "url": "https://platform.openai.com/docs/guides/function-calling"}
            ]
        },
        {
            "stage_order": 5,
            "title": "AI Evaluation, Observability & Guardrails",
            "category": "Production Engineering",
            "description": "Implement automated evaluation frameworks (Ragas), OpenTelemetry distributed trace logging, and input/output safety guardrails.",
            "why_recommended": "Enterprise deployment requires strict SLAs against hallucinations, latency tracking, and prompt injection defense.",
            "prerequisites": ["AI Agent Workflows & Multi-Agent Orchestration"],
            "estimated_effort": "2 weeks",
            "skills": ["Ragas Evaluation", "OpenTelemetry", "Arize Phoenix", "NeMo Guardrails", "AI Security"],
            "practical_project": "Deploy an evaluation suite benchmarking RAG answer faithfulness and tracing token latency",
            "completion_criteria": [
                "Automate Ragas metrics (context recall, faithfulness, answer relevancy)",
                "Export span traces to Phoenix or LangSmith",
                "Configure guardrails blocking adversarial prompt injection"
            ],
            "learning_resources": [
                {"name": "Ragas Evaluation Documentation", "url": "https://docs.ragas.io/"},
                {"name": "Anthropic AI Evaluation Guidelines", "url": "https://www.anthropic.com/research/evaluating-ai-systems"}
            ]
        },
        {
            "stage_order": 6,
            "title": "Production AI Capstone: Autonomous Engineering Assistant",
            "category": "Capstone Deliverable",
            "description": "Synthesize all skills into a deployed, containerized autonomous AI platform with CI/CD, vector storage, and automated evals.",
            "why_recommended": "Demonstrates full-lifecycle AI engineering competence to hiring managers with tangible production architecture.",
            "prerequisites": ["AI Evaluation, Observability & Guardrails"],
            "estimated_effort": "3–4 weeks",
            "skills": ["Full-Stack AI Deployment", "Docker", "Kubernetes / Cloud Run", "CI/CD", "Production Telemetry"],
            "practical_project": "Deliver an end-to-end autonomous research assistant running on cloud containers with live telemetry",
            "completion_criteria": [
                "Containerize services with multi-stage Dockerfiles",
                "Publish comprehensive architecture documentation and benchmarks",
                "Deploy with automated CI/CD pipeline and monitoring dashboard"
            ],
            "learning_resources": [
                {"name": "Docker Containerization for Python AI", "url": "https://docs.docker.com/language/python/"},
                {"name": "Cloud Run Deployment Guide", "url": "https://cloud.google.com/run/docs"}
            ]
        }
    ],
    "Full Stack Developer": [
        {
            "stage_order": 1,
            "title": "Modern TypeScript & Advanced JavaScript Foundations",
            "category": "Core Foundations",
            "description": "Master TypeScript static typing, generics, utility types, async runtime, and asynchronous event-driven patterns.",
            "why_recommended": "TypeScript is the universal industry standard for scalable full-stack codebases.",
            "prerequisites": [],
            "estimated_effort": "2 weeks",
            "skills": ["TypeScript", "JavaScript ES6+", "Generics", "Async/Await", "NPM"],
            "practical_project": "Build a strictly typed in-memory caching and event-emitter library in TypeScript",
            "completion_criteria": [
                "Zero TypeScript 'any' types in codebase",
                "Implement generic data structures and type guards",
                "100% test coverage with Vitest / Jest"
            ],
            "learning_resources": [
                {"name": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Modern Frontend Architecture with React 19 & Next.js 15",
            "category": "Frontend Architecture",
            "description": "Build high-performance web applications with React 19 Server Components, Actions, and Next.js 15 App Router.",
            "why_recommended": "Next.js 15 App Router with server-side rendering is the foremost requirement in web engineering job requisitions.",
            "prerequisites": ["Modern TypeScript & Advanced JavaScript Foundations"],
            "estimated_effort": "3 weeks",
            "skills": ["React 19", "Next.js 15", "Server Components", "Tailwind CSS", "State Management"],
            "practical_project": "Develop a responsive analytics dashboard with streaming Suspense and optimistic mutations",
            "completion_criteria": [
                "Implement nested layouts with parallel routing",
                "Apply instant optimistic updates with React 19 useOptimistic",
                "Achieve 95+ Google Lighthouse performance score"
            ],
            "learning_resources": [
                {"name": "Next.js 15 Documentation", "url": "https://nextjs.org/docs"},
                {"name": "React 19 Release Blog", "url": "https://react.dev/blog/2024/12/05/react-19"}
            ]
        },
        {
            "stage_order": 3,
            "title": "High-Throughput Backend APIs & Relational Modeling",
            "category": "Backend Systems",
            "description": "Design asynchronous REST/GraphQL APIs with FastAPI or Node.js, PostgreSQL relational modeling, and migrations.",
            "why_recommended": "Full stack engineers must architect resilient backend interfaces with ACID transactions.",
            "prerequisites": ["Modern TypeScript & Advanced JavaScript Foundations"],
            "estimated_effort": "3 weeks",
            "skills": ["FastAPI / Node.js", "PostgreSQL", "SQLAlchemy / Prisma", "Database Migrations", "Pydantic"],
            "practical_project": "Architect an order processing and inventory API with transactional locking and schema migrations",
            "completion_criteria": [
                "Implement foreign keys, composite indices, and transaction rollbacks",
                "Enforce strict schema validation and auto-generated OpenAPI specs",
                "Pass comprehensive integration test suite"
            ],
            "learning_resources": [
                {"name": "PostgreSQL Tutorial & Optimization", "url": "https://www.postgresql.org/docs/"}
            ]
        },
        {
            "stage_order": 4,
            "title": "Authentication, Distributed Caching & Message Queues",
            "category": "Distributed Systems",
            "description": "Implement OAuth2 / JWT authentication, Redis distributed caching, and asynchronous task queues.",
            "why_recommended": "Real-world web scale requires offloading heavy tasks to workers and low-latency cache layers.",
            "prerequisites": ["High-Throughput Backend APIs & Relational Modeling"],
            "estimated_effort": "2–3 weeks",
            "skills": ["Redis", "JWT Auth", "OAuth2", "Celery / BullMQ", "WebSockets"],
            "practical_project": "Build a real-time collaborative workspace with WebSocket sync and Redis pub/sub",
            "completion_criteria": [
                "Secure endpoints with token expiration and refresh rotation",
                "Implement cache-aside pattern with Redis",
                "Deliver real-time message broadcasting across client sessions"
            ],
            "learning_resources": [
                {"name": "Redis Documentation", "url": "https://redis.io/docs/"}
            ]
        },
        {
            "stage_order": 5,
            "title": "DevOps, Containerization & Automated CI/CD",
            "category": "Cloud & Operations",
            "description": "Containerize full stack applications with multi-stage Dockerfiles and deploy automated GitHub Actions pipelines.",
            "why_recommended": "Modern engineering teams expect engineers to own features through automated testing to production deployment.",
            "prerequisites": ["Authentication, Distributed Caching & Message Queues"],
            "estimated_effort": "2 weeks",
            "skills": ["Docker", "Docker Compose", "GitHub Actions", "CI/CD", "Cloud Infrastructure"],
            "practical_project": "Construct a multi-container Docker Compose staging environment with automated lint/test/deploy CI",
            "completion_criteria": [
                "Create minimal, secure multi-stage container images",
                "Write GitHub Actions workflow running tests and security scans",
                "Deploy to cloud container service with environment secrets"
            ],
            "learning_resources": [
                {"name": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions"}
            ]
        },
        {
            "stage_order": 6,
            "title": "Full-Stack Production Capstone: Enterprise Platform",
            "category": "Capstone Deliverable",
            "description": "Engineer a complete multi-tenant production web platform with payments, analytics, telemetry, and automated tests.",
            "why_recommended": "Demonstrates the complete end-to-end capability expected of mid-to-senior full-stack engineers.",
            "prerequisites": ["DevOps, Containerization & Automated CI/CD"],
            "estimated_effort": "3–4 weeks",
            "skills": ["System Design", "Cloud Architecture", "Monitoring", "Payment Gateway", "Production Security"],
            "practical_project": "Deploy a multi-tenant SaaS application with stripe billing, RBAC authorization, and OpenTelemetry",
            "completion_criteria": [
                "Complete role-based access control and billing webhook lifecycle",
                "Deploy live to public domain with SSL and monitoring",
                "Publish architectural decision records (ADRs) and API documentation"
            ],
            "learning_resources": [
                {"name": "Modern Web Architecture Patterns", "url": "https://patterns.dev/"}
            ]
        }
    ],
    "Backend Developer": [
        {
            "stage_order": 1,
            "title": "Advanced Data Structures, Algorithms & Concurrency",
            "category": "Core Foundations",
            "description": "Master algorithmic time/space complexity, hash maps, graph traversals, and multi-threaded / asynchronous concurrency.",
            "why_recommended": "Backend engineering demands deep understanding of memory, locks, and algorithmic complexity.",
            "prerequisites": [],
            "estimated_effort": "2–3 weeks",
            "skills": ["Data Structures", "Algorithms", "Concurrency", "Thread Safety", "Python / Go / Java"],
            "practical_project": "Build a concurrent worker pool with rate-limiting and graceful worker shutdown",
            "completion_criteria": [
                "Solve 30+ medium/hard algorithmic challenges on graph/DP/trees",
                "Demonstrate non-blocking concurrency without race conditions",
                "Profile CPU and memory allocation under stress"
            ],
            "learning_resources": [
                {"name": "LeetCode Practice Catalogue", "url": "https://leetcode.com/"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Relational Modeling, Indexing & Query Optimization",
            "category": "Database Engineering",
            "description": "Deep-dive into PostgreSQL query execution plans (EXPLAIN ANALYZE), B-Tree / GIN indexing, and transaction isolation levels.",
            "why_recommended": "Database bottlenecks are the #1 cause of backend outages. Indexing and query tuning are critical competencies.",
            "prerequisites": ["Advanced Data Structures, Algorithms & Concurrency"],
            "estimated_effort": "2–3 weeks",
            "skills": ["PostgreSQL", "SQL Optimization", "EXPLAIN ANALYZE", "ACID Transactions", "Connection Pooling"],
            "practical_project": "Tune a slow database schema with 1,000,000 records, reducing query latency by 80% with strategic indices",
            "completion_criteria": [
                "Interpret EXPLAIN ANALYZE query plans and eliminate sequential scans",
                "Implement connection pooling with PgBouncer",
                "Enforce ACID compliance across multi-table money transfer transactions"
            ],
            "learning_resources": [
                {"name": "Use The Index, Luke! SQL Indexing Guide", "url": "https://use-the-index-luke.com/"}
            ]
        },
        {
            "stage_order": 3,
            "title": "High-Throughput Asynchronous Microservices",
            "category": "API Architectures",
            "description": "Build high-concurrency microservices using FastAPI / Go, gRPC protocol buffers, and Pydantic v2 schemas.",
            "why_recommended": "Modern backends utilize gRPC for internal service-to-service communication and async HTTP for edge clients.",
            "prerequisites": ["Relational Modeling, Indexing & Query Optimization"],
            "estimated_effort": "3 weeks",
            "skills": ["FastAPI", "gRPC", "Protocol Buffers", "REST APIs", "Asyncio"],
            "practical_project": "Build dual REST and gRPC microservices with shared proto contracts and asynchronous handlers",
            "completion_criteria": [
                "Define Protocol Buffer service contracts and generate stubs",
                "Achieve 2,000+ requests/sec with asynchronous worker loops",
                "Validate schemas with zero runtime performance penalties"
            ],
            "learning_resources": [
                {"name": "gRPC Official Documentation", "url": "https://grpc.io/docs/"}
            ]
        },
        {
            "stage_order": 4,
            "title": "Distributed Caching, Event Streaming & Message Queues",
            "category": "Distributed Systems",
            "description": "Master Redis caching architectures, Kafka / RabbitMQ event-driven publish-subscribe, and idempotent consumers.",
            "why_recommended": "Decoupled asynchronous message brokers prevent cascading failures across cloud services.",
            "prerequisites": ["High-Throughput Asynchronous Microservices"],
            "estimated_effort": "3 weeks",
            "skills": ["Redis", "Apache Kafka / RabbitMQ", "Event-Driven Architecture", "Idempotency", "Dead-Letter Queues"],
            "practical_project": "Build an event-driven payment processing pipeline with Kafka topics and dead-letter queue error recovery",
            "completion_criteria": [
                "Ensure exactly-once processing semantics through deduplication keys",
                "Configure consumer groups and partition rebalancing",
                "Handle transient third-party failures with exponential backoff"
            ],
            "learning_resources": [
                {"name": "Confluent Kafka Fundamentals", "url": "https://developer.confluent.io/"}
            ]
        },
        {
            "stage_order": 5,
            "title": "Cloud Infrastructure, Kubernetes & OpenTelemetry",
            "category": "Cloud & Observability",
            "description": "Deploy distributed backend services onto Kubernetes with Helm charts, Ingress, and OpenTelemetry trace instrumentation.",
            "why_recommended": "Backend engineers must operate services reliably with distributed traces across network boundaries.",
            "prerequisites": ["Distributed Caching, Event Streaming & Message Queues"],
            "estimated_effort": "3 weeks",
            "skills": ["Kubernetes", "Docker", "OpenTelemetry", "Helm", "Prometheus / Grafana"],
            "practical_project": "Deploy microservices to a local Minikube / K3s cluster with automated Prometheus health alerts and Jaeger traces",
            "completion_criteria": [
                "Write Kubernetes manifests (Deployment, Service, ConfigMap, Ingress)",
                "Export span traces to Jaeger visualizing end-to-end request latency",
                "Configure automated horizontal pod autoscaling (HPA)"
            ],
            "learning_resources": [
                {"name": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/"},
                {"name": "OpenTelemetry Python Docs", "url": "https://opentelemetry.io/docs/languages/python/"}
            ]
        },
        {
            "stage_order": 6,
            "title": "Production Backend Capstone: Resilient Distributed Engine",
            "category": "Capstone Deliverable",
            "description": "Architect and deploy an enterprise-grade distributed backend system capable of handling high concurrency and node failures.",
            "why_recommended": "Tangible proof of senior backend engineering design and operational capability.",
            "prerequisites": ["Cloud Infrastructure, Kubernetes & OpenTelemetry"],
            "estimated_effort": "3–4 weeks",
            "skills": ["System Design", "Fault Tolerance", "Distributed Consensus", "Load Testing", "Disaster Recovery"],
            "practical_project": "Architect a distributed ledger or reservation system with distributed locking and stress test benchmarks",
            "completion_criteria": [
                "Demonstrate zero data corruption during simulated node crashes",
                "Conduct Locust / k6 load tests validating 99th-percentile response under 100ms",
                "Document full architecture diagram, ADRs, and runbooks"
            ],
            "learning_resources": [
                {"name": "Designing Data-Intensive Applications (Kleppmann)", "url": "https://dataintensive.net/"}
            ]
        }
    ],
    "Data Scientist": [
        {
            "stage_order": 1,
            "title": "Scientific Computing & Fast DataFrame Pipelines",
            "category": "Core Foundations",
            "description": "Master Python for data science, NumPy matrix operations, Pandas, and modern high-speed Polars dataframes.",
            "why_recommended": "Data manipulation efficiency is fundamental to all statistical modeling and feature engineering.",
            "prerequisites": [],
            "estimated_effort": "2 weeks",
            "skills": ["Python", "NumPy", "Pandas", "Polars", "Data Wrangling"],
            "practical_project": "Process and aggregate a 5M-row public dataset with Polars lazy evaluation expressions",
            "completion_criteria": [
                "Demonstrate vectorized calculations without slow Python loops",
                "Implement streaming computations with minimal memory footprint",
                "Profile memory and execution benchmarks against legacy Pandas"
            ],
            "learning_resources": [
                {"name": "Polars Documentation", "url": "https://docs.pola.rs/"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Statistical Modeling, EDA & Hypothesis Testing",
            "category": "Applied Statistics",
            "description": "Master probability distributions, hypothesis testing (t-test, ANOVA, Chi-Square), A/B testing design, and Bayesian fundamentals.",
            "why_recommended": "Rigorous statistical inference separates professional data scientists from automated model callers.",
            "prerequisites": ["Scientific Computing & Fast DataFrame Pipelines"],
            "estimated_effort": "3 weeks",
            "skills": ["Applied Statistics", "A/B Testing", "Hypothesis Testing", "Seaborn / Matplotlib", "Data Storytelling"],
            "practical_project": "Design and execute an end-to-end A/B test analysis notebook with power analysis and sample size estimation",
            "completion_criteria": [
                "Perform statistical power calculation and minimum detectable effect analysis",
                "Detect and correct for multi-testing problems (Bonferroni / FDR)",
                "Deliver clear executive visual summaries with confidence intervals"
            ],
            "learning_resources": [
                {"name": "Penn State Stat 500: Applied Statistics", "url": "https://online.stat.psu.edu/stat500/"}
            ]
        },
        {
            "stage_order": 3,
            "title": "Supervised & Unsupervised Machine Learning",
            "category": "Machine Learning",
            "description": "Train and evaluate Scikit-Learn models, gradient boosted decision trees (XGBoost, LightGBM), feature engineering, and cross-validation.",
            "why_recommended": "Tabular machine learning on structured datasets represents 80%+ of real-world business data science.",
            "prerequisites": ["Statistical Modeling, EDA & Hypothesis Testing"],
            "estimated_effort": "3 weeks",
            "skills": ["Scikit-Learn", "XGBoost", "LightGBM", "Cross-Validation", "SHAP / Explainability"],
            "practical_project": "Build a customer churn prediction pipeline with feature importance and SHAP model explainability",
            "completion_criteria": [
                "Prevent data leakage using Scikit-Learn Pipelines and ColumnTransformer",
                "Optimize hyperparameters via Bayesian search (Optuna)",
                "Explain individual predictions using SHAP values"
            ],
            "learning_resources": [
                {"name": "Scikit-Learn User Guide", "url": "https://scikit-learn.org/stable/user_guide.html"}
            ]
        },
        {
            "stage_order": 4,
            "title": "Deep Learning & Neural Network Architectures",
            "category": "Deep Learning",
            "description": "Implement feed-forward neural networks, CNNs, and sequence transformer models in PyTorch with GPU acceleration.",
            "why_recommended": "Modern data science roles increasingly require deep learning for unstructured text, image, and tabular embeddings.",
            "prerequisites": ["Supervised & Unsupervised Machine Learning"],
            "estimated_effort": "3 weeks",
            "skills": ["PyTorch", "Neural Networks", "Embeddings", "Transfer Learning", "CUDA"],
            "practical_project": "Train a custom PyTorch deep learning classifier with tensorboard loss logging and early stopping",
            "completion_criteria": [
                "Implement custom PyTorch Dataset and DataLoader classes",
                "Fine-tune a pretrained model with learning rate scheduling",
                "Evaluate model performance with ROC-AUC and precision-recall curves"
            ],
            "learning_resources": [
                {"name": "PyTorch Official Tutorials", "url": "https://pytorch.org/tutorials/"}
            ]
        },
        {
            "stage_order": 5,
            "title": "MLOps, Experiment Tracking & Model Deployment",
            "category": "MLOps",
            "description": "Track model experiments with MLflow, version datasets with DVC, and deploy prediction microservices with FastAPI.",
            "why_recommended": "Models without deployment pipelines deliver zero business value. MLOps is an essential hiring criterion.",
            "prerequisites": ["Deep Learning & Neural Network Architectures"],
            "estimated_effort": "2–3 weeks",
            "skills": ["MLflow", "FastAPI", "Docker", "Model Registry", "Data Drift Monitoring"],
            "practical_project": "Deploy a containerized model inference API logged to an MLflow registry with automated input validation",
            "completion_criteria": [
                "Log model artifacts, parameters, and metrics to MLflow server",
                "Build low-latency inference endpoint with batch prediction support",
                "Implement basic statistical data drift detection on input distributions"
            ],
            "learning_resources": [
                {"name": "MLflow Documentation", "url": "https://mlflow.org/docs/latest/index.html"}
            ]
        },
        {
            "stage_order": 6,
            "title": "Data Science Capstone: End-to-End Predictive Analytics Platform",
            "category": "Capstone Deliverable",
            "description": "Deliver a complete production data science project from raw data ingestion to deployed dashboard with live model inferences.",
            "why_recommended": "Comprehensive proof of business impact and technical depth for senior data science recruitment.",
            "prerequisites": ["MLOps, Experiment Tracking & Model Deployment"],
            "estimated_effort": "3–4 weeks",
            "skills": ["End-to-End DS", "Dashboarding", "Streamlit / React", "Business Metrics", "Cloud Deployment"],
            "practical_project": "Deploy an interactive predictive analytics portal with real-time model predictions and business KPI simulations",
            "completion_criteria": [
                "Connect production model API to an interactive user dashboard",
                "Formulate actionable business recommendations backed by confidence bounds",
                "Publish reproducible Jupyter notebook and GitHub repository"
            ],
            "learning_resources": [
                {"name": "Streamlit Documentation", "url": "https://docs.streamlit.io/"}
            ]
        }
    ],
    "UI/UX Designer": [
        {
            "stage_order": 1,
            "title": "User Research, Empathy Mapping & Information Architecture",
            "category": "UX Research",
            "description": "Master qualitative user interviews, empathy maps, user journey mapping, persona archetypes, and card sorting information architecture.",
            "why_recommended": "Understanding user mental models and task flows is the foundational prerequisite before creating visual layouts.",
            "prerequisites": [],
            "estimated_effort": "2–3 weeks",
            "skills": ["User Research", "Information Architecture", "User Journey Mapping", "Persona Modeling", "Card Sorting"],
            "practical_project": "Conduct user research interviews and deliver a comprehensive Journey Map & Information Architecture blueprint",
            "completion_criteria": [
                "Synthesize 5+ user interview transcripts into distinct problem statements",
                "Map user pain points, touchpoints, and emotional curves across an end-to-end journey",
                "Define intuitive hierarchical sitemap and navigation tree"
            ],
            "learning_resources": [
                {"name": "Nielsen Norman Group UX Research Guides", "url": "https://www.nngroup.com/articles/"},
                {"name": "Interaction Design Foundation: Information Architecture", "url": "https://www.interaction-design.org/literature/topics/information-architecture"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Wireframing, Low-to-Mid Fidelity Prototyping & UX Heuristics",
            "category": "UX Design & Heuristics",
            "description": "Translate user flows into grayscale wireframes, conduct heuristic evaluations using Nielsen's 10 usability heuristics, and build click-through prototypes.",
            "why_recommended": "Focusing on layout hierarchy and cognitive load in grayscale eliminates visual bias before high-fidelity styling.",
            "prerequisites": ["User Research, Empathy Mapping & Information Architecture"],
            "estimated_effort": "2–3 weeks",
            "skills": ["Wireframing", "Usability Heuristics", "User Flows", "Figma", "Rapid Prototyping"],
            "practical_project": "Design a 15-screen responsive wireframe prototype in Figma with complete task navigation flows",
            "completion_criteria": [
                "Audit existing product interfaces using Nielsen Norman 10 Usability Heuristics",
                "Create low-fidelity wireframe flows adhering to standard UX patterns",
                "Connect click-through interactions and validate task completion paths"
            ],
            "learning_resources": [
                {"name": "Nielsen Norman Group 10 Usability Heuristics", "url": "https://www.nngroup.com/articles/ten-usability-heuristics/"},
                {"name": "Figma Wireframing Best Practices", "url": "https://www.figma.com/resource-library/wireframing/"}
            ]
        },
        {
            "stage_order": 3,
            "title": "Visual Design Systems, Spatial Grids & Typography Mastery",
            "category": "Visual UI Design",
            "description": "Master the 8pt spatial grid system, typographic scale and vertical rhythm, chromatic harmony, and Figma Auto-Layout.",
            "why_recommended": "World-class digital products feel effortless because of mathematical spatial consistency, typography, and optical balance.",
            "prerequisites": ["Wireframing, Low-to-Mid Fidelity Prototyping & UX Heuristics"],
            "estimated_effort": "3 weeks",
            "skills": ["Visual Hierarchy", "Typography", "Color Theory", "8pt Grid System", "Figma Auto-Layout"],
            "practical_project": "Design a high-fidelity visual interface kit using Figma Auto-Layout with responsive component resizing",
            "completion_criteria": [
                "Build fluid components using nested Figma Auto-Layout with min/max constraints",
                "Establish accessible typography scale adhering to WCAG contrast standards",
                "Apply 8pt/4pt spatial rules across all paddings, margins, and component alignments"
            ],
            "learning_resources": [
                {"name": "Refactoring UI (Adam Wathan & Steve Schoger)", "url": "https://www.refactoringui.com/"},
                {"name": "Figma Auto-Layout Documentation", "url": "https://help.figma.com/hc/en-us/articles/360040451373-Explore-auto-layout-properties"}
            ]
        },
        {
            "stage_order": 4,
            "title": "Scalable Design Systems & Figma Variables Architecture",
            "category": "Design Systems",
            "description": "Build scalable multi-brand design systems using Figma Variables (modes, color tokens, spacing tokens), component properties, and atomic design.",
            "why_recommended": "Enterprise product companies require design system practitioners who can build synchronized token pipelines between Figma and code.",
            "prerequisites": ["Visual Design Systems, Spatial Grids & Typography Mastery"],
            "estimated_effort": "3 weeks",
            "skills": ["Design Systems", "Figma Variables", "Design Tokens", "Atomic Design", "Component Variants"],
            "practical_project": "Architect a comprehensive design system with light/dark theme variables and 40+ atomic component variants",
            "completion_criteria": [
                "Structure multi-tier design tokens (global, alias/semantic, component-scoped)",
                "Implement automatic Light/Dark mode switching using Figma Variable collections",
                "Publish interactive component variants with boolean, text, and instance swap properties"
            ],
            "learning_resources": [
                {"name": "Figma Guide to Variables & Modes", "url": "https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma"},
                {"name": "Design Systems Handbook by InVision", "url": "https://www.designbetter.co/design-systems-handbook"}
            ]
        },
        {
            "stage_order": 5,
            "title": "Micro-Interactions, Motion Design & Usability Testing",
            "category": "Interaction & Usability",
            "description": "Design realistic micro-animations using Figma Smart Animate and ProtoPie; conduct moderated usability sessions with SUS scoring.",
            "why_recommended": "Micro-interactions provide immediate cognitive feedback, while empirical usability testing validates user satisfaction and efficiency.",
            "prerequisites": ["Scalable Design Systems & Figma Variables Architecture"],
            "estimated_effort": "2–3 weeks",
            "skills": ["Smart Animate", "Motion Design", "ProtoPie / Principle", "Usability Testing", "System Usability Scale (SUS)"],
            "practical_project": "Conduct 5 moderated usability test sessions on an advanced animated prototype and deliver a quantitative SUS report",
            "completion_criteria": [
                "Prototype stateful micro-interactions (loaders, swipes, accordion reveals) with natural easing curves",
                "Calculate quantitative task completion rates, time-on-task, and SUS usability scores",
                "Synthesize feedback into prioritized UX recommendation matrices"
            ],
            "learning_resources": [
                {"name": "Material Design Motion Guidelines", "url": "https://m3.material.io/styles/motion/overview"},
                {"name": "MeasuringU: System Usability Scale (SUS)", "url": "https://measuringu.com/sus/"}
            ]
        },
        {
            "stage_order": 6,
            "title": "WCAG 2.2 Accessibility Auditing, Dev Handoff & Portfolio Capstone",
            "category": "Capstone Deliverable",
            "description": "Conduct rigorous accessibility audits against WCAG 2.2 AA criteria, prepare developer token handoffs, and assemble an end-to-end case study.",
            "why_recommended": "A detailed product design case study demonstrating problem framing, research, iterative testing, and accessible implementation is the single most important asset for recruitment.",
            "prerequisites": ["Micro-Interactions, Motion Design & Usability Testing"],
            "estimated_effort": "3–4 weeks",
            "skills": ["WCAG 2.2 Accessibility", "Developer Handoff", "Design Specs", "Case Study Storytelling", "Design Portfolio"],
            "practical_project": "Publish a comprehensive end-to-end Product Design Case Study with verified WCAG 2.2 accessibility compliance",
            "completion_criteria": [
                "Perform contrast, focus state, and touch target accessibility audits passing WCAG 2.2 Level AA",
                "Generate clean developer inspection specs with token aliases and responsive behaviors",
                "Document the entire design lifecycle from problem statement to validated metrics in a portfolio case study"
            ],
            "learning_resources": [
                {"name": "W3C Web Content Accessibility Guidelines (WCAG) 2.2", "url": "https://www.w3.org/TR/WCAG22/"},
                {"name": "Case Study Club: Top Product Design Case Studies", "url": "https://www.casestudy.club/"}
            ]
        }
    ],
    "Frontend Developer": [
        {
            "stage_order": 1,
            "title": "Modern CSS Architecture, Responsive Layouts & Design Tokens",
            "category": "Core Foundations",
            "description": "Master CSS cascading layers, modern flexbox/grid layouts, container queries, and Tailwind CSS v4 design token systems.",
            "why_recommended": "Deep CSS mastery and layout performance are essential for building fluid, responsive, accessible web interfaces.",
            "prerequisites": [],
            "estimated_effort": "2 weeks",
            "skills": ["CSS3", "HTML5", "Tailwind CSS v4", "Container Queries", "Responsive Layouts"],
            "practical_project": "Build an accessible design token system with container queries and fluid typography in Tailwind v4",
            "completion_criteria": [
                "Implement complex responsive layouts with CSS Grid and Container Queries",
                "Enforce semantic HTML5 and accessible keyboard focus navigation",
                "Achieve 100/100 Lighthouse accessibility score"
            ],
            "learning_resources": [
                {"name": "Tailwind CSS v4 Documentation", "url": "https://tailwindcss.com/docs"},
                {"name": "MDN Web Docs: CSS Layout", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout"}
            ]
        },
        {
            "stage_order": 2,
            "title": "Deep JavaScript Internals & Production TypeScript",
            "category": "Language Proficiency",
            "description": "Master JavaScript execution contexts, closures, event loop microtasks, asynchronous promises, and TypeScript generics.",
            "why_recommended": "Solid JavaScript and TypeScript static typing prevent subtle client-side runtime crashes.",
            "prerequisites": ["Modern CSS Architecture, Responsive Layouts & Design Tokens"],
            "estimated_effort": "2–3 weeks",
            "skills": ["JavaScript ES6+", "TypeScript", "Event Loop", "DOM Performance", "Unit Testing"],
            "practical_project": "Build a strictly-typed in-browser reactive state and event emitter library with 100% test coverage",
            "completion_criteria": [
                "Zero TypeScript 'any' types in codebase",
                "Demonstrate understanding of event loop task queues and microtasks",
                "Write thorough unit tests using Vitest"
            ],
            "learning_resources": [
                {"name": "TypeScript Official Handbook", "url": "https://www.typescriptlang.org/docs/"}
            ]
        },
        {
            "stage_order": 3,
            "title": "Modern React 19 Component Architecture & Server Actions",
            "category": "Frontend Frameworks",
            "description": "Build high-performance client applications using React 19 Hooks, Actions, useActionState, and optimistic UI mutations.",
            "why_recommended": "React 19 standardizes form actions, asset loading, and optimistic state directly in core React.",
            "prerequisites": ["Deep JavaScript Internals & Production TypeScript"],
            "estimated_effort": "3 weeks",
            "skills": ["React 19", "React Hooks", "Server Actions", "Optimistic UI", "Component Patterns"],
            "practical_project": "Develop a real-time reactive task board with React 19 Actions and instantaneous optimistic updates",
            "completion_criteria": [
                "Implement form handling with useActionState and useFormStatus",
                "Deliver zero-latency optimistic updates with useOptimistic",
                "Architect reusable, encapsulated compound components"
            ],
            "learning_resources": [
                {"name": "React 19 Official Documentation", "url": "https://react.dev/"}
            ]
        },
        {
            "stage_order": 4,
            "title": "Next.js 15 App Router Architecture & Streaming Suspense",
            "category": "Full Stack Frontend",
            "description": "Master Next.js 15 App Router, React Server Components (RSC), parallel and intercepted routes, and streaming with Suspense.",
            "why_recommended": "App Router architecture with server-side rendering is the foremost requirement in web engineering job postings.",
            "prerequisites": ["Modern React 19 Component Architecture & Server Actions"],
            "estimated_effort": "3 weeks",
            "skills": ["Next.js 15", "App Router", "React Server Components", "Streaming Suspense", "SEO Optimization"],
            "practical_project": "Build an enterprise portal with Next.js 15, dynamic route interception, and streaming skeleton loading",
            "completion_criteria": [
                "Configure asynchronous request lifecycle with cookies/headers",
                "Implement nested layout caching and streaming Suspense boundaries",
                "Achieve 95+ Core Web Vitals on mobile and desktop"
            ],
            "learning_resources": [
                {"name": "Next.js 15 Documentation", "url": "https://nextjs.org/docs"}
            ]
        },
        {
            "stage_order": 5,
            "title": "State Management, Client Caching & Automated Testing",
            "category": "Application State & Quality",
            "description": "Master TanStack Query (React Query) for server state caching, Zustand for local client state, and comprehensive Vitest/RTL testing.",
            "why_recommended": "Decoupling server cache from client state drastically reduces network overhead and avoids prop drilling.",
            "prerequisites": ["Next.js 15 App Router Architecture & Streaming Suspense"],
            "estimated_effort": "2–3 weeks",
            "skills": ["TanStack Query", "Zustand", "Vitest", "React Testing Library", "Mock Service Worker (MSW)"],
            "practical_project": "Build an offline-resilient dashboard with optimistic queries, background cache invalidation, and integration tests",
            "completion_criteria": [
                "Configure query caching with automatic stale-time revalidation",
                "Simulate API responses with Mock Service Worker (MSW)",
                "Write comprehensive integration tests covering user interaction flows"
            ],
            "learning_resources": [
                {"name": "TanStack Query Documentation", "url": "https://tanstack.com/query/latest"}
            ]
        },
        {
            "stage_order": 6,
            "title": "Production Frontend Capstone: High-Fidelity Creative Platform",
            "category": "Capstone Deliverable",
            "description": "Deliver a production web application with sub-100ms interaction latency, fluid micro-animations, and automated edge deployment.",
            "why_recommended": "A live, exceptionally responsive web platform demonstrates senior frontend engineering and design sensibilities.",
            "prerequisites": ["State Management, Client Caching & Automated Testing"],
            "estimated_effort": "3–4 weeks",
            "skills": ["Web Performance", "Core Web Vitals", "Edge Deployment", "CI/CD", "Accessibility (a11y)"],
            "practical_project": "Deploy a high-fidelity creative web application with 98+ Lighthouse scores, micro-animations, and full a11y compliance",
            "completion_criteria": [
                "Optimize bundle size with dynamic code splitting and tree-shaking",
                "Conduct automated accessibility audits with axe-core passing WCAG AA",
                "Deploy on edge CDN infrastructure with automated GitHub Actions CI"
            ],
            "learning_resources": [
                {"name": "web.dev: Learn Core Web Vitals", "url": "https://web.dev/explore/learn-core-web-vitals"}
            ]
        }
    ]
}


def _get_template_for_role(target_role: str) -> List[Dict[str, Any]]:
    """Select the best matching curriculum template for target career role."""
    role_lower = (target_role or "").lower()
    if "ui" in role_lower or "ux" in role_lower or "design" in role_lower:
        return ROLE_CURRICULUM_TEMPLATES["UI/UX Designer"]
    elif "frontend" in role_lower:
        return ROLE_CURRICULUM_TEMPLATES["Frontend Developer"]
    elif "ai" in role_lower or "nlp" in role_lower or "machine learning" in role_lower:
        return ROLE_CURRICULUM_TEMPLATES["AI Engineer"]
    elif "data" in role_lower and ("sci" in role_lower or "analyst" in role_lower):
        return ROLE_CURRICULUM_TEMPLATES["Data Scientist"]
    elif "backend" in role_lower:
        return ROLE_CURRICULUM_TEMPLATES["Backend Developer"]
    elif "full" in role_lower or "stack" in role_lower or "software" in role_lower or "developer" in role_lower:
        return ROLE_CURRICULUM_TEMPLATES["Full Stack Developer"]
    else:
        return ROLE_CURRICULUM_TEMPLATES["UI/UX Designer"] if ("designer" in role_lower or "ui" in role_lower or "ux" in role_lower) else ROLE_CURRICULUM_TEMPLATES["AI Engineer"]


def generate_or_get_personalized_roadmap(
    db: Session,
    current_user: User,
    target_role: str,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Generate or retrieve the personalized career roadmap for the user and target role.
    Integrates verified GitHub/LeetCode skills, unverified resume skills, and persistent PostgreSQL state.
    """
    effective_role = target_role or "AI Engineer"

    # 1. Fetch user's multi-source profile intelligence
    try:
        profile_data = build_unified_candidate_profile(db=db, current_user=current_user)
        profile_dict = profile_data.model_dump(mode="json") if hasattr(profile_data, "model_dump") else dict(profile_data)
    except Exception:
        profile_dict = {}

    unified_skills = profile_dict.get("unified_skills") or []
    
    # Differentiate verified skills (GitHub, LeetCode, Certifications) from unverified resume mentions
    verified_skills = []
    unverified_skills = []
    
    for s in unified_skills:
        if isinstance(s, dict):
            s_name = s.get("name") or ""
            sources = [str(src).lower() for src in s.get("sources", [])]
            # Has GitHub code repo or LeetCode/HackerRank evidence
            if any(src in ["github", "leetcode", "hackerrank", "certification"] for src in sources):
                verified_skills.append(s_name)
            else:
                unverified_skills.append(s_name)
        elif isinstance(s, str):
            unverified_skills.append(s)

    verified_set = {s.lower().strip() for s in verified_skills}

    # 2. Check if a CareerRoadmap already exists for this user and target_role in DB
    existing_roadmap = (
        db.query(CareerRoadmap)
        .filter(
            CareerRoadmap.user_id == current_user.id,
            CareerRoadmap.target_role.ilike(effective_role)
        )
        .first()
    )

    if existing_roadmap and not force_refresh:
        # Load active version and milestones
        active_version = (
            db.query(RoadmapVersion)
            .filter(
                RoadmapVersion.roadmap_id == existing_roadmap.id,
                RoadmapVersion.is_active == True
            )
            .first()
        )
        if active_version:
            milestones = (
                db.query(RoadmapMilestone)
                .filter(RoadmapMilestone.version_id == active_version.id)
                .order_by(RoadmapMilestone.stage_order.asc())
                .all()
            )
            if milestones:
                # Calculate latest readiness score
                completed_count = sum(1 for m in milestones if m.status == "completed")
                total_count = len(milestones)
                
                # Dynamic readiness scoring based on verified skills (40%) + milestone completions (60%)
                role_template = _get_template_for_role(effective_role)
                req_skills = set()
                for step in role_template:
                    for sk in step.get("skills", []):
                        req_skills.add(sk.lower())
                
                matched_verified = sum(1 for req in req_skills if any(req in vs or vs in req for vs in verified_set))
                skill_readiness = (matched_verified / max(1, len(req_skills))) * 40.0
                milestone_readiness = (completed_count / max(1, total_count)) * 60.0
                readiness_score = int(min(100, round(skill_readiness + milestone_readiness)))

                # Update roadmap aggregates
                existing_roadmap.readiness_score = readiness_score
                existing_roadmap.total_milestones = total_count
                existing_roadmap.completed_milestones = completed_count
                existing_roadmap.last_reviewed_at = datetime.now(timezone.utc)
                db.commit()

                # Evaluate trend signals
                completed_titles = [m.title for m in milestones if m.status == "completed"]
                trend_eval = trend_intelligence_service.evaluate_student_signals(
                    target_role=effective_role,
                    verified_skills=verified_skills,
                    unverified_skills=unverified_skills,
                    completed_milestone_titles=completed_titles
                )

                # Sync pending recommendations in RoadmapChangeLog
                _sync_pending_recommendations(db, existing_roadmap, trend_eval.get("suggested_updates", []))

                # Fetch change history logs
                change_logs = (
                    db.query(RoadmapChangeLog)
                    .filter(RoadmapChangeLog.roadmap_id == existing_roadmap.id)
                    .order_by(RoadmapChangeLog.created_at.desc())
                    .all()
                )

                return _format_roadmap_response(
                    roadmap=existing_roadmap,
                    version=active_version,
                    milestones=milestones,
                    change_logs=change_logs,
                    trend_eval=trend_eval,
                    verified_skills=verified_skills,
                    unverified_skills=unverified_skills
                )

    # 3. If no roadmap exists (or force_refresh requested), generate a new personalized roadmap!
    template_stages = _get_template_for_role(effective_role)

    # If existing roadmap exists on force_refresh, keep existing ID and preserve completed milestones
    completed_map = {}
    if existing_roadmap:
        old_active = (
            db.query(RoadmapVersion)
            .filter(RoadmapVersion.roadmap_id == existing_roadmap.id, RoadmapVersion.is_active == True)
            .first()
        )
        if old_active:
            for old_m in old_active.milestones:
                if old_m.status == "completed":
                    completed_map[old_m.title.lower()] = {
                        "status": old_m.status,
                        "progress_pct": old_m.progress_pct,
                        "completed_at": old_m.completed_at
                    }
        roadmap = existing_roadmap
        new_version_num = roadmap.current_version + 1
        roadmap.current_version = new_version_num
    else:
        roadmap = CareerRoadmap(
            user_id=current_user.id,
            target_role=effective_role,
            current_version=1,
            readiness_score=0,
            last_reviewed_at=datetime.now(timezone.utc)
        )
        db.add(roadmap)
        db.flush()
        new_version_num = 1

    # Deactivate prior versions
    db.query(RoadmapVersion).filter(RoadmapVersion.roadmap_id == roadmap.id).update({"is_active": False})

    new_version = RoadmapVersion(
        roadmap_id=roadmap.id,
        version_number=new_version_num,
        change_summary="Initial personalized roadmap generated based on candidate profile and verified skills." if new_version_num == 1 else "Regenerated personalized roadmap updated with latest profile evidence.",
        is_active=True
    )
    db.add(new_version)
    db.flush()

    milestone_objs = []
    completed_count = 0

    for idx, stage in enumerate(template_stages, start=1):
        stage_title = stage["title"]
        stage_skills = stage.get("skills", [])
        
        # Check if student already demonstrated proficiency in this stage's core skills!
        is_verified_stage = False
        if stage_skills and stage["category"] == "Foundations":
            matched_skills = [sk for sk in stage_skills if any(sk.lower() in vs for vs in verified_set)]
            if len(matched_skills) >= len(stage_skills) * 0.6:
                is_verified_stage = True

        # Check preserved completions
        preserved = completed_map.get(stage_title.lower())

        if preserved:
            m_status = preserved["status"]
            m_prog = preserved["progress_pct"]
            m_comp_at = preserved["completed_at"]
            completed_count += 1
        elif is_verified_stage:
            m_status = "completed"
            m_prog = 100
            m_comp_at = datetime.now(timezone.utc)
            completed_count += 1
        elif idx == 1 or (idx == 2 and completed_count >= 1):
            m_status = "in_progress"
            m_prog = 25
            m_comp_at = None
        else:
            m_status = "upcoming"
            m_prog = 0
            m_comp_at = None

        why_rec = stage.get("why_recommended", "")
        if is_verified_stage:
            why_rec += " (Prior proficiency verified through candidate coding platform/GitHub profile.)"

        milestone = RoadmapMilestone(
            version_id=new_version.id,
            stage_order=idx,
            title=stage_title,
            category=stage.get("category", "Milestone"),
            description=stage.get("description", ""),
            why_recommended=why_rec,
            prerequisites=stage.get("prerequisites", []),
            estimated_effort=stage.get("estimated_effort", "2 weeks"),
            skills=stage_skills,
            practical_project=stage.get("practical_project", ""),
            completion_criteria=stage.get("completion_criteria", []),
            learning_resources=stage.get("learning_resources", []),
            status=m_status,
            progress_pct=m_prog,
            completed_at=m_comp_at
        )
        db.add(milestone)
        milestone_objs.append(milestone)

    db.flush()

    # Calculate initial readiness score
    req_skills = set()
    for stage in template_stages:
        for sk in stage.get("skills", []):
            req_skills.add(sk.lower())

    matched_verified = sum(1 for req in req_skills if any(req in vs or vs in req for vs in verified_set))
    skill_readiness = (matched_verified / max(1, len(req_skills))) * 40.0
    milestone_readiness = (completed_count / max(1, len(milestone_objs))) * 60.0
    readiness_score = int(min(100, round(skill_readiness + milestone_readiness)))

    roadmap.readiness_score = readiness_score
    roadmap.total_milestones = len(milestone_objs)
    roadmap.completed_milestones = completed_count
    roadmap.last_reviewed_at = datetime.now(timezone.utc)

    # Initial log in RoadmapChangeLog
    init_log = RoadmapChangeLog(
        roadmap_id=roadmap.id,
        action_type="roadmap_initialized",
        title=f"Roadmap Version {new_version_num} Generated for {effective_role}",
        why_changed="Synthesized customized roadmap aligning candidate verified profile against target industry requirements.",
        proposed_action=f"Personalized sequence of {len(milestone_objs)} progressive milestones created.",
        status="applied"
    )
    db.add(init_log)
    db.commit()

    # Evaluate trend signals
    completed_titles = [m.title for m in milestone_objs if m.status == "completed"]
    trend_eval = trend_intelligence_service.evaluate_student_signals(
        target_role=effective_role,
        verified_skills=verified_skills,
        unverified_skills=unverified_skills,
        completed_milestone_titles=completed_titles
    )

    _sync_pending_recommendations(db, roadmap, trend_eval.get("suggested_updates", []))

    change_logs = (
        db.query(RoadmapChangeLog)
        .filter(RoadmapChangeLog.roadmap_id == roadmap.id)
        .order_by(RoadmapChangeLog.created_at.desc())
        .all()
    )

    return _format_roadmap_response(
        roadmap=roadmap,
        version=new_version,
        milestones=milestone_objs,
        change_logs=change_logs,
        trend_eval=trend_eval,
        verified_skills=verified_skills,
        unverified_skills=unverified_skills
    )


def _sync_pending_recommendations(
    db: Session,
    roadmap: CareerRoadmap,
    suggested_updates: List[Dict[str, Any]]
) -> None:
    """Ensure actionable trend recommendations exist as pending change logs without duplicates."""
    if not suggested_updates:
        return

    existing_logs = (
        db.query(RoadmapChangeLog)
        .filter(
            RoadmapChangeLog.roadmap_id == roadmap.id,
            RoadmapChangeLog.action_type == "adaptive_recommendation"
        )
        .all()
    )
    existing_titles = {log.title for log in existing_logs}

    for update in suggested_updates:
        title = f"Recommended Roadmap Update: {update['proposed_title']}"
        if title not in existing_titles:
            new_log = RoadmapChangeLog(
                roadmap_id=roadmap.id,
                action_type="adaptive_recommendation",
                title=title,
                why_changed=update["why_suggested"],
                proposed_action=update["proposed_action"],
                evidence_summary=update["evidence_summary"],
                evidence_source=update["evidence_source"],
                evidence_url=update["evidence_url"],
                evidence_date=update["evidence_date"],
                status="pending",
                suggested_milestone_data=update
            )
            db.add(new_log)

    db.commit()


def accept_roadmap_recommendation(
    db: Session,
    current_user: User,
    change_id: int
) -> Dict[str, Any]:
    """
    Accept an adaptive roadmap recommendation.
    Creates a new roadmap version, injects the recommended milestone in correct dependency order,
    preserves completed work, and marks change log as accepted.
    """
    change_log = (
        db.query(RoadmapChangeLog)
        .join(CareerRoadmap)
        .filter(
            RoadmapChangeLog.id == change_id,
            CareerRoadmap.user_id == current_user.id
        )
        .first()
    )

    if not change_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap recommendation not found"
        )

    if change_log.status == "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation already accepted"
        )

    roadmap = change_log.roadmap
    active_version = (
        db.query(RoadmapVersion)
        .filter(RoadmapVersion.roadmap_id == roadmap.id, RoadmapVersion.is_active == True)
        .first()
    )

    if not active_version:
        raise HTTPException(status_code=400, detail="Active roadmap version not found")

    old_milestones = (
        db.query(RoadmapMilestone)
        .filter(RoadmapMilestone.version_id == active_version.id)
        .order_by(RoadmapMilestone.stage_order.asc())
        .all()
    )

    # Create new version
    new_version_num = roadmap.current_version + 1
    roadmap.current_version = new_version_num
    active_version.is_active = False

    new_version = RoadmapVersion(
        roadmap_id=roadmap.id,
        version_number=new_version_num,
        change_summary=f"Accepted industry trend update: Added '{change_log.title}'. Supported by {change_log.evidence_source}.",
        is_active=True
    )
    db.add(new_version)
    db.flush()

    # Recreate milestones preserving previous statuses
    new_milestones = []
    milestone_data = change_log.suggested_milestone_data or {}
    injected = False

    for idx, old_m in enumerate(old_milestones, start=1):
        # Inject recommended milestone right after intermediate stages (or before capstone)
        if not injected and ("capstone" in old_m.title.lower() or idx >= 4):
            # Injected milestone
            injected_m = RoadmapMilestone(
                version_id=new_version.id,
                stage_order=len(new_milestones) + 1,
                title=milestone_data.get("proposed_title", change_log.title.replace("Recommended Roadmap Update: ", "")),
                category=milestone_data.get("category", "Industry Trend"),
                description=change_log.why_changed,
                why_recommended=f"Recommended via monitored signal from {change_log.evidence_source} ({change_log.evidence_date}).",
                prerequisites=[new_milestones[-1].title] if new_milestones else [],
                estimated_effort=milestone_data.get("estimated_effort", "2 weeks"),
                skills=[milestone_data.get("technology", "Emerging Tech")],
                practical_project=milestone_data.get("practical_project", "Build practical deliverable integrating " + str(milestone_data.get("technology", "skill"))),
                completion_criteria=milestone_data.get("completion_criteria", ["Implement practical exercises", "Complete project verification"]),
                status="in_progress" if any(m.status == "completed" for m in old_milestones) else "upcoming",
                progress_pct=15 if any(m.status == "completed" for m in old_milestones) else 0
            )
            db.add(injected_m)
            new_milestones.append(injected_m)
            injected = True

        clone_m = RoadmapMilestone(
            version_id=new_version.id,
            stage_order=len(new_milestones) + 1,
            title=old_m.title,
            category=old_m.category,
            description=old_m.description,
            why_recommended=old_m.why_recommended,
            prerequisites=old_m.prerequisites,
            estimated_effort=old_m.estimated_effort,
            skills=old_m.skills,
            practical_project=old_m.practical_project,
            completion_criteria=old_m.completion_criteria,
            learning_resources=old_m.learning_resources,
            status=old_m.status,
            progress_pct=old_m.progress_pct,
            completed_at=old_m.completed_at
        )
        db.add(clone_m)
        new_milestones.append(clone_m)

    if not injected:
        injected_m = RoadmapMilestone(
            version_id=new_version.id,
            stage_order=len(new_milestones) + 1,
            title=milestone_data.get("proposed_title", change_log.title.replace("Recommended Roadmap Update: ", "")),
            category=milestone_data.get("category", "Industry Trend"),
            description=change_log.why_changed,
            why_recommended=f"Recommended via monitored signal from {change_log.evidence_source} ({change_log.evidence_date}).",
            prerequisites=[new_milestones[-1].title] if new_milestones else [],
            estimated_effort=milestone_data.get("estimated_effort", "2 weeks"),
            skills=[milestone_data.get("technology", "Emerging Tech")],
            practical_project=milestone_data.get("practical_project", "Build practical deliverable"),
            completion_criteria=milestone_data.get("completion_criteria", ["Complete practical project"]),
            status="upcoming",
            progress_pct=0
        )
        db.add(injected_m)
        new_milestones.append(injected_m)

    # Update change log status
    change_log.status = "accepted"
    change_log.resolved_at = datetime.now(timezone.utc)

    # Add change log record for version promotion
    promo_log = RoadmapChangeLog(
        roadmap_id=roadmap.id,
        action_type="version_promoted",
        title=f"Promoted to Roadmap Version {new_version_num}",
        why_changed=f"Successfully integrated '{injected_m.title}' into curriculum.",
        proposed_action="Version upgraded while preserving existing progress.",
        evidence_source=change_log.evidence_source,
        evidence_url=change_log.evidence_url,
        evidence_date=change_log.evidence_date,
        status="applied"
    )
    db.add(promo_log)

    roadmap.total_milestones = len(new_milestones)
    roadmap.last_reviewed_at = datetime.now(timezone.utc)
    db.commit()

    return generate_or_get_personalized_roadmap(db, current_user, roadmap.target_role)


def dismiss_roadmap_recommendation(
    db: Session,
    current_user: User,
    change_id: int
) -> Dict[str, Any]:
    """Dismiss an adaptive roadmap recommendation."""
    change_log = (
        db.query(RoadmapChangeLog)
        .join(CareerRoadmap)
        .filter(
            RoadmapChangeLog.id == change_id,
            CareerRoadmap.user_id == current_user.id
        )
        .first()
    )

    if not change_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap recommendation not found"
        )

    change_log.status = "dismissed"
    change_log.resolved_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Recommendation dismissed", "id": change_id, "status": "dismissed"}


def toggle_milestone_progress(
    db: Session,
    current_user: User,
    milestone_id: int
) -> Dict[str, Any]:
    """Toggle a milestone between completed and in_progress/upcoming, recalculating readiness score."""
    milestone = (
        db.query(RoadmapMilestone)
        .join(RoadmapVersion)
        .join(CareerRoadmap)
        .filter(
            RoadmapMilestone.id == milestone_id,
            CareerRoadmap.user_id == current_user.id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    roadmap = milestone.version.roadmap

    if milestone.status == "completed":
        milestone.status = "in_progress"
        milestone.progress_pct = 50
        milestone.completed_at = None
        action_title = f"Milestone Set to In Progress: {milestone.title}"
    else:
        milestone.status = "completed"
        milestone.progress_pct = 100
        milestone.completed_at = datetime.now(timezone.utc)
        action_title = f"Completed Milestone: {milestone.title}"

    # Log completion event
    log = RoadmapChangeLog(
        roadmap_id=roadmap.id,
        action_type="milestone_completed" if milestone.status == "completed" else "milestone_status_changed",
        title=action_title,
        why_changed="Student marked milestone progress.",
        status="applied"
    )
    db.add(log)
    db.commit()

    return generate_or_get_personalized_roadmap(db, current_user, roadmap.target_role)


def _format_roadmap_response(
    roadmap: CareerRoadmap,
    version: RoadmapVersion,
    milestones: List[RoadmapMilestone],
    change_logs: List[RoadmapChangeLog],
    trend_eval: Dict[str, Any],
    verified_skills: List[str],
    unverified_skills: List[str]
) -> Dict[str, Any]:
    """Format full JSON response adhering to UI needs."""
    milestone_dicts = []
    next_milestone = None

    for m in milestones:
        m_dict = {
            "id": m.id,
            "stage": m.stage_order,
            "title": m.title,
            "category": m.category,
            "description": m.description,
            "why_recommended": m.why_recommended,
            "prerequisites": m.prerequisites or [],
            "estimated_effort": m.estimated_effort,
            "skills": m.skills or [],
            "practical_project": m.practical_project,
            "completion_criteria": m.completion_criteria or [],
            "learning_resources": m.learning_resources or [],
            "status": m.status,
            "progress_pct": m.progress_pct,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
        }
        milestone_dicts.append(m_dict)
        if not next_milestone and m.status in ("in_progress", "upcoming"):
            next_milestone = m_dict

    pending_recommendations = [
        {
            "id": log.id,
            "title": log.title,
            "why_suggested": log.why_changed,
            "proposed_action": log.proposed_action,
            "evidence_summary": log.evidence_summary,
            "evidence_source": log.evidence_source,
            "evidence_url": log.evidence_url,
            "evidence_date": log.evidence_date,
            "suggested_milestone_data": log.suggested_milestone_data,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in change_logs if log.status == "pending" and log.action_type == "adaptive_recommendation"
    ]

    history_logs = [
        {
            "id": log.id,
            "action_type": log.action_type,
            "title": log.title,
            "why_changed": log.why_changed,
            "proposed_action": log.proposed_action,
            "evidence_summary": log.evidence_summary,
            "evidence_source": log.evidence_source,
            "evidence_url": log.evidence_url,
            "evidence_date": log.evidence_date,
            "status": log.status,
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "resolved_at": log.resolved_at.isoformat() if log.resolved_at else None
        }
        for log in change_logs
    ]

    # Find skill gaps
    all_target_skills = []
    for m in milestones:
        all_target_skills.extend(m.skills or [])
    all_target_skills_unique = sorted(list(set(all_target_skills)))
    verified_lower = {v.lower() for v in verified_skills}
    key_gaps = [sk for sk in all_target_skills_unique if sk.lower() not in verified_lower][:8]

    return {
        "roadmap_id": roadmap.id,
        "target_role": roadmap.target_role,
        "readiness_score": roadmap.readiness_score,
        "current_version": roadmap.current_version,
        "total_milestones": len(milestone_dicts),
        "completed_milestones": sum(1 for m in milestone_dicts if m["status"] == "completed"),
        "last_reviewed_at": roadmap.last_reviewed_at.isoformat() if roadmap.last_reviewed_at else None,
        "next_milestone": next_milestone,
        "verified_skills": verified_skills[:12],
        "key_skill_gaps": key_gaps,
        "milestones": milestone_dicts,
        "roadmap": milestone_dicts,  # Backwards compatibility alias
        "pending_recommendations": pending_recommendations,
        "change_history": history_logs,
        "trend_signals": trend_eval.get("evaluated_trends", []),
        "version_summary": version.change_summary
    }
