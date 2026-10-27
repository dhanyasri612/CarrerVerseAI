import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.teaching_progress import TeachingProgress
from app.ai.providers.factory import get_model_provider
from app.schemas.teaching import (
    TeachingCurriculumResponse,
    TeachingEvaluationRequest,
    TeachingEvaluationResponse,
    TeachingInteractionRequest,
    TeachingInteractionResponse,
    TeachingLesson,
    TeachingProgressResponse,
    TeachingSection,
    TeachingChatRequest,
    TeachingChatResponse,
    TeachingChatTurn,
    SkillLearningPathResponse,
    ProjectLearningJourneyResponse,
    RepositoryUnderstandingModel,
)
from app.services.unified_profile_service import build_unified_candidate_profile
from app.ai.knowledge_graph.graph_queries import graph_query_service
from app.services.learner_knowledge_service import build_learner_knowledge_profile
from app.services.teaching_resource_service import retrieve_teaching_resources_for_lesson
from app.ai.knowledge_graph.concept_graph_service import concept_graph_service
from app.schemas.learner_knowledge import ConceptMapResponse

logger = logging.getLogger(__name__)


def get_teaching_concept_map(
    db: Session,
    current_user: User,
    lesson_id: Optional[str] = None,
) -> ConceptMapResponse:
    """
    Returns the interactive Neo4j concept map for the learner, connecting
    prerequisites, related topics, and verified candidate projects.
    """
    profile = build_learner_knowledge_profile(db, current_user)
    return concept_graph_service.get_concept_map(
        candidate_id=current_user.id,
        current_lesson_id=lesson_id,
        skills_inventory=profile.skills_inventory,
        verified_projects=profile.verified_projects,
    )



def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"[-\s]+", "-", s) or "lesson"


# ── CURATED PEDAGOGICAL SKILL TEMPLATES ───────────────────────────────────────
CURATED_SKILL_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "python": {
        "title": "Python • GIL, Memory Model & Asyncio Invariants",
        "topic": "Memory Allocation, GIL, Generators & Async Event Loop",
        "difficulty": "Medium to Hard",
        "summary": "Master Python's memory management, reference counting, GIL implications on CPU vs I/O concurrency, and cooperative multitasking with asyncio.",
        "question": (
            "Explain how Python's Global Interpreter Lock (GIL) dictates CPU-bound vs I/O-bound concurrency.\n\n"
            "How does Python's asyncio event loop achieve 10,000+ concurrent network connections on a single OS thread, "
            "and when would you choose multiprocessing or C-extensions over asyncio?"
        ),
        "code": (
            "import asyncio\n\n"
            "async def concurrent_fetch(urls: list[str]):\n"
            "    # Implement non-blocking concurrent task batching\n"
            "    pass\n"
        ),
        "constraints": ["Zero thread-blocking operations inside event loop", "Graceful exception handling across gathered tasks"],
        "hints": [
            "Remember that asyncio is single-threaded cooperative multitasking; blocking calls stall the entire event loop.",
            "Use asyncio.gather with return_exceptions=True or TaskGroups to handle individual task failures cleanly.",
        ],
    },
    "fastapi": {
        "title": "FastAPI • Asynchronous DI, Middleware & Pydantic V2",
        "topic": "Dependency Injection, Async Route Scheduling & Lifecycle Handlers",
        "difficulty": "Medium",
        "summary": "Understand how FastAPI dispatches async def vs def endpoints, yields database sessions via Depends(), and validates payloads using Pydantic V2 Rust core.",
        "question": (
            "How does FastAPI differentiate between 'async def' and synchronous 'def' path operations under high concurrency?\n\n"
            "Walk me through how FastAPI's Depends() dependency injection works, and how yield dependencies guarantee resource cleanup (e.g. database transactions or Redis pools)."
        ),
        "code": (
            "from fastapi import FastAPI, Depends\n"
            "from sqlalchemy.orm import Session\n\n"
            "# Implement yield dependency with transactional rollback on failure\n"
            "def get_db_session():\n"
            "    pass\n"
        ),
        "constraints": ["Non-blocking async execution", "Deterministic database session teardown", "Sub-10ms route overhead"],
        "hints": [
            "FastAPI runs async def endpoints directly on the main event loop, while def endpoints are offloaded to an AnyIO threadpool.",
            "Yield dependencies execute the cleanup phase in a finally block after the endpoint finishes processing.",
        ],
    },
    "react": {
        "title": "React • Fiber Reconciliation, State Batching & Memoization",
        "topic": "Virtual DOM Reconciliation, Fiber Trees, Hooks & Re-renders",
        "difficulty": "Medium",
        "summary": "Master the React Fiber reconciliation engine, automatic state update batching, and surgical performance optimizations with useMemo, useCallback, and React.memo.",
        "question": (
            "Walk me through how React's Fiber reconciler determines what DOM nodes need updating across re-renders.\n\n"
            "Why do unnecessary re-renders occur in deeply nested trees, and what are the exact rules for using useCallback, useMemo, and custom selector hooks without causing stale closures?"
        ),
        "code": (
            "import React, { useState, useCallback, useMemo } from 'react';\n\n"
            "// Optimize a high-frequency rendered item list\n"
            "export const FilterableList = ({ items, onItemSelect }) => {\n"
            "    // Implement memoized filter and stable callback\n"
            "};\n"
        ),
        "constraints": ["Zero unnecessary child re-renders", "No stale state closures in async effects"],
        "hints": [
            "React compares Object.is on state updates; passing new inline object/array references triggers child re-renders if children are wrapped in React.memo.",
            "useCallback returns a memoized function reference, but if its dependency array is incomplete, it will capture stale outer scope variables.",
        ],
    },
    "typescript": {
        "title": "TypeScript • Structural Typing, Generics & Discriminated Unions",
        "topic": "Structural Subtyping, Conditional Types & Exhaustive Matching",
        "difficulty": "Medium",
        "summary": "Leverage TypeScript's structural type system, generic constraints, conditional types, and discriminated unions to enforce compile-time domain correctness.",
        "question": (
            "Explain the difference between TypeScript's structural type system (duck typing) and nominal typing in Java or C#.\n\n"
            "How do discriminated unions with exhaustive never checking eliminate runtime bugs in complex asynchronous state machines?"
        ),
        "code": (
            "type AsyncState<T> =\n"
            "  | { status: 'idle' }\n"
            "  | { status: 'loading' }\n"
            "  | { status: 'success'; data: T }\n"
            "  | { status: 'error'; error: Error };\n\n"
            "function renderState<T>(state: AsyncState<T>): string {\n"
            "  // Implement exhaustive type-safe switch matching\n"
            "}\n"
        ),
        "constraints": ["Strict compile-time type safety", "Exhaustive branch handling using never type assertion"],
        "hints": [
            "TypeScript checks whether an object satisfies the required properties (structure), not where or how it was instantiated.",
            "In the default case of a discriminated union switch, assigning state to a const _exhaustive: never = state verifies that all possible states were handled.",
        ],
    },
    "postgresql": {
        "title": "PostgreSQL • B-Trees, MVCC & Query Optimization",
        "topic": "Index Design, MVCC Vacuuming, Transaction Isolation & EXPLAIN ANALYZE",
        "difficulty": "Hard",
        "summary": "Master Multi-Version Concurrency Control (MVCC), composite B-Tree column ordering, partial indexes, and diagnosing sequential table scans.",
        "question": (
            "How does PostgreSQL's Multi-Version Concurrency Control (MVCC) prevent SELECT queries from blocking UPDATE/INSERT transactions?\n\n"
            "Given a table with 50 million records and a query filtering by both user_id (equality) and created_at (range), how would you design the optimal composite B-Tree index, and what does the leftmost prefix rule mandate?"
        ),
        "code": (
            "-- Propose composite index and EXPLAIN query plan\n"
            "CREATE INDEX idx_orders_user_created ON orders (...);\n"
            "EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42 AND created_at > '2026-01-01';\n"
        ),
        "constraints": ["Equality columns must precede range columns", "Prevent sequential disk table scans"],
        "hints": [
            "In composite B-Tree indexes, equality filter columns must always precede range filter columns so the B-Tree can narrow the search interval efficiently.",
            "MVCC writes a new row version (tuple) with xmin and xmax on every update; autovacuum reclaims dead tuples to prevent table bloat.",
        ],
    },
    "redis": {
        "title": "Redis • In-Memory Data Structures, Caching & Lua Atomicity",
        "topic": "Cache-Aside, Thundering Herd Prevention, Eviction & Distributed Locks",
        "difficulty": "Medium to Hard",
        "summary": "Architect resilient caching layers with Redis, handle cache invalidation, thundering herds, and ensure atomic execution with Lua scripts.",
        "question": (
            "How do you design a resilient Cache-Aside pattern with Redis that prevents both Cache Stampede (Thundering Herd) and Cache Penetration?\n\n"
            "Why is executing multiple commands inside a Redis Lua script guaranteed to be atomic, and how does this enable distributed mutex locking (Redlock)?"
        ),
        "code": (
            "# Redis atomic lock acquisition and cache-aside lookup\n"
            "def get_or_compute_cached_value(key: str, ttl: int):\n"
            "    pass\n"
        ),
        "constraints": ["Sub-5ms cache lookup", "Zero duplicate database queries under concurrent cold cache stampede"],
        "hints": [
            "Use mutex locks (SET NX PX) or probabilistic early expiration (XFetch) to ensure only one worker recomputes cold cache.",
            "Redis executes Lua scripts in a single atomic tick; no other client command can interleave while a Lua script is running.",
        ],
    },
    "docker": {
        "title": "Docker • Multi-Stage Builds, Layer Caching & Container Security",
        "topic": "Image Size Optimization, Layer Ordering, Cgroups & Non-Root Execution",
        "difficulty": "Medium",
        "summary": "Optimize Docker containerization with multi-stage builds, strategic layer caching, cgroup resource limits, and non-root security boundaries.",
        "question": (
            "How do multi-stage Docker builds reduce production image attack surfaces and disk footprints from 1.5GB down to < 100MB?\n\n"
            "How does Docker layer caching evaluate RUN, COPY, and WORKDIR directives, and why should dependencies (package.json / requirements.txt) be copied before source code?"
        ),
        "code": (
            "# Multi-stage Dockerfile blueprint\n"
            "FROM python:3.11-slim AS builder\n"
            "WORKDIR /build\n"
            "# Install dependencies\n\n"
            "FROM python:3.11-slim AS runner\n"
            "WORKDIR /app\n"
            "# Copy only necessary wheels/artifacts\n"
        ),
        "constraints": ["Production image size < 150MB", "Run as unprivileged non-root user (USER 1001)"],
        "hints": [
            "Docker checks if files copied in COPY instructions have changed. Putting source code after dependency install prevents reinstalling packages on every code edit.",
            "Multi-stage builds leave compiler toolchains, header files, and devDependencies behind in the builder stage.",
        ],
    },
    "git": {
        "title": "Git • Directed Acyclic Graph (DAG), Rebase vs Merge & Bisect",
        "topic": "Commit Graphs, Fast-Forward Merges, Interactive Rebase & Debugging",
        "difficulty": "Medium",
        "summary": "Master Git's internal DAG model, blobs, trees, commit objects, clean linear histories with interactive rebasing, and binary-searching bugs with git bisect.",
        "question": (
            "Explain how Git internally models version history as a Directed Acyclic Graph (DAG) of cryptographically hashed objects (blobs, trees, commits).\n\n"
            "When should an engineering team use 'git rebase' versus 'git merge'? What does interactive rebase (git rebase -i) allow you to do with commit history?"
        ),
        "code": (
            "# Interactive Git workflow and history inspection\n"
            "git rebase -i HEAD~3\n"
            "git bisect start HEAD v1.0.0\n"
        ),
        "constraints": ["Maintain clean, bisectable commit history", "Zero accidental merge conflict overwrites"],
        "hints": [
            "Rebase reapplies commits on top of another base commit, creating a clean linear history, while merge preserves the exact chronological branching timeline.",
            "Git bisect uses binary search over commits (O(log N)) to pinpoint the exact commit that introduced a test failure.",
        ],
    },
    "langchain": {
        "title": "LangChain & LangGraph • Multi-Agent Orchestration & Tool Routing",
        "topic": "Stateful Agent Graphs, Tool Calling, Determinism & Memory Management",
        "difficulty": "Hard",
        "summary": "Design cyclic multi-agent systems with LangGraph, managing shared state schemas, conditional router edges, and tool call retry policies.",
        "question": (
            "Explain how LangGraph represents multi-agent coordination as a state graph with nodes, conditional routing edges, and shared state schemas.\n\n"
            "How do you prevent infinite execution loops when an agent calls external tools, and how do you handle partial failures or context overflow in long conversations?"
        ),
        "code": (
            "from langgraph.graph import StateGraph, END\n\n"
            "# Define typed state and conditional routing edge\n"
            "class AgentState(dict):\n"
            "    messages: list\n"
            "    next_node: str\n"
        ),
        "constraints": ["Strict recursion limits (e.g. max 10 steps)", "Exhaustive error handling on tool call failure"],
        "hints": [
            "Use recursion_limit in graph execution to hard-cap agent execution steps.",
            "Conditional routing functions evaluate agent messages and decide whether to route to a tool node or terminate at END.",
        ],
    },
    "rag": {
        "title": "RAG • Chunking Strategies, Vector Search & Hybrid Re-ranking",
        "topic": "Semantic Chunking, Dense Vector Embeddings, BM25 Keyword Search & Cross-Encoders",
        "difficulty": "Hard",
        "summary": "Architect production Retrieval-Augmented Generation (RAG) pipelines combining dense vector similarity with sparse BM25 retrieval and cross-encoder re-ranking.",
        "question": (
            "What are the trade-offs between fixed-size chunking and semantic chunking based on document structure?\n\n"
            "Why does hybrid retrieval (combining dense vector cosine similarity with sparse BM25 keyword search) out-perform vector search alone, and how do cross-encoder re-rankers filter out retrieval hallucinations?"
        ),
        "code": (
            "# Hybrid RAG retrieval and cross-encoder re-ranking pipeline\n"
            "def retrieve_and_rerank(query: str, top_k: int = 5):\n"
            "    # 1. Retrieve dense vector candidates\n"
            "    # 2. Retrieve BM25 keyword candidates\n"
            "    # 3. Reciprocal Rank Fusion & Cross-Encoder scoring\n"
            "    pass\n"
        ),
        "constraints": ["Sub-150ms retrieval latency", "High context precision to minimize LLM token waste"],
        "hints": [
            "Dense vector embeddings struggle with exact acronyms, numbers, or unique IDs where BM25 keyword search excels.",
            "Cross-encoders jointly process the query and document chunk together, providing higher precision ranking than bi-encoder cosine distance.",
        ],
    },
    "generative ai": {
        "title": "Generative AI • Prompt Steering, Guardrails & Deterministic Outputs",
        "topic": "System Prompts, Few-Shot In-Context Learning, JSON Schemas & Latency",
        "difficulty": "Medium to Hard",
        "summary": "Master prompt engineering, structured JSON output enforcement, temperature tuning, and mitigating hallucination risks in enterprise AI systems.",
        "question": (
            "How do you enforce deterministic structured JSON outputs from Large Language Models for downstream API integration without parser crashes?\n\n"
            "What are the trade-offs between fine-tuning vs in-context learning with dynamic RAG context injection, and how do you monitor for hallucination drift in production?"
        ),
        "code": (
            "# Structured generation schema enforcement\n"
            "from pydantic import BaseModel\n\n"
            "class StructuredOutput(BaseModel):\n"
            "    summary: str\n"
            "    confidence_score: float\n"
            "    recommended_actions: list[str]\n"
        ),
        "constraints": ["100% valid JSON adherence", "Sub-1s time-to-first-token streaming"],
        "hints": [
            "Use tool calling or JSON schema validation modes to constrain generation at the token sampling level.",
            "In-context learning with dynamic RAG provides fresh grounded facts without the high compute cost and staleness of model retraining.",
        ],
    },
    "javascript": {
        "title": "JavaScript • Event Loop, Microtasks & Prototype Chain",
        "topic": "Call Stack, Macrotask vs Microtask Queues, Closures & Garbage Collection",
        "difficulty": "Medium",
        "summary": "Understand JavaScript execution semantics: the call stack, microtask queue (Promises), macrotask queue (timers/events), and closures.",
        "question": (
            "In what order do synchronous code, Promise.then() microtasks, and setTimeout() macrotasks execute in the JavaScript V8 engine?\n\n"
            "How do lexical closures retain scope references, and how can unreleased event listeners or intervals create severe browser memory leaks?"
        ),
        "code": (
            "console.log('1');\n"
            "setTimeout(() => console.log('2'), 0);\n"
            "Promise.resolve().then(() => console.log('3'));\n"
            "console.log('4');\n"
            "// Output order: 1, 4, 3, 2\n"
        ),
        "constraints": ["Single-threaded non-blocking runtime", "Clean listener teardown on component unmount"],
        "hints": [
            "Microtasks (Promises, queueMicrotask) execute immediately after the current call stack clears, before any pending macrotask.",
            "Closures keep references alive in the heap as long as the containing function or callback remains referenced.",
        ],
    },
    "java": {
        "title": "Java • JVM Memory Architecture, Garbage Collection & Concurrency",
        "topic": "Young/Old Gen Heap, G1/ZGC Collectors, Volatile & Synchronization",
        "difficulty": "Hard",
        "summary": "Master the Java Virtual Machine (JVM) memory model, generational garbage collection (Eden, Survivor, Tenured), and multi-threaded synchronization primitives.",
        "question": (
            "Explain how the JVM manages memory between the Young Generation (Eden, S0, S1) and Old Generation.\n\n"
            "What does the 'volatile' keyword guarantee in terms of memory visibility and instruction reordering under the Java Memory Model?"
        ),
        "code": (
            "import java.util.concurrent.atomic.AtomicInteger;\n\n"
            "public class ThreadSafeCounter {\n"
            "    private final AtomicInteger count = new AtomicInteger(0);\n"
            "    // Explain atomic compare-and-swap (CAS)\n"
            "}\n"
        ),
        "constraints": ["Thread-safe state transitions", "Zero race conditions across concurrent threads"],
        "hints": [
            "Objects are allocated in Eden; survivors of minor GC cycles are copied between Survivor spaces before promotion to Old Gen.",
            "Volatile prevents CPU cache incoherence by ensuring reads and writes go directly to main memory with memory barriers.",
        ],
    },
    "mysql": {
        "title": "MySQL • InnoDB Storage Engine, Next-Key Locks & ACID",
        "topic": "InnoDB Buffer Pool, Row-Level Locking, Phantom Reads & Deadlock Detection",
        "difficulty": "Medium to Hard",
        "summary": "Master MySQL InnoDB internals, clustered vs secondary indexes, buffer pool caching, and row-level next-key locks under Repeatable Read.",
        "question": (
            "How does MySQL InnoDB implement row-level locking with Next-Key Locks to eliminate Phantom Reads under the Repeatable Read isolation level?\n\n"
            "How does InnoDB detect and resolve transaction deadlocks, and how can application developers prevent deadlocks in high-throughput workloads?"
        ),
        "code": (
            "-- Inspect deadlock state and optimize transactional locks\n"
            "SHOW ENGINE INNODB STATUS;\n"
            "SELECT * FROM accounts WHERE id = 1 FOR UPDATE;\n"
        ),
        "constraints": ["Consistent locking order across transactions", "Keep transactions minimal in duration"],
        "hints": [
            "Next-Key Lock combines an index-record lock with a gap lock on the gap preceding the index record.",
            "Always access tables and rows in a globally consistent order across all application transactions to eliminate cyclic wait chains.",
        ],
    },
    "deep learning": {
        "title": "Deep Learning • Backpropagation, Optimizers & Regularization",
        "topic": "Gradient Descent, Vanishing Gradients, Batch Normalization & Dropout",
        "difficulty": "Hard",
        "summary": "Understand gradient descent mathematics, chain rule backpropagation, vanishing/exploding gradients, and modern regularization techniques.",
        "question": (
            "Walk me through the mathematical mechanics of backpropagation using the multivariate chain rule.\n\n"
            "Why do deep neural networks suffer from vanishing gradients with sigmoid activations, and how do ReLU activations, Batch Normalization, and Residual connections (ResNets) solve this?"
        ),
        "code": (
            "import tensorflow as tf\n\n"
            "# Implement residual block with batch normalization and skip connection\n"
        ),
        "constraints": ["Stable gradient propagation across 50+ layers", "Prevent overfitting on small validation splits"],
        "hints": [
            "Vanishing gradients occur when derivative terms (< 1.0) multiply repeatedly through deep layers, shrinking earlier layer weight updates to zero.",
            "Residual skip connections allow gradients to flow directly back through identity shortcuts without diminishing.",
        ],
    },
    "computer vision": {
        "title": "Computer Vision • Convolutions, Feature Hierarchies & Detection",
        "topic": "Spatial Convolutions, Receptive Fields, Pooling & Data Augmentation",
        "difficulty": "Medium to Hard",
        "summary": "Master 2D convolution kernels, spatial feature maps, receptive fields, transfer learning, and handling medical or domain-specific image datasets.",
        "question": (
            "How does a 2D convolution operation extract hierarchical spatial features (edges $\to$ textures $\to$ object parts) from raw pixel arrays?\n\n"
            "When training computer vision models on medical imaging or custom datasets, how do data augmentation and transfer learning mitigate severe overfitting?"
        ),
        "code": (
            "import cv2\n"
            "import numpy as np\n\n"
            "# Image normalization and contrast enhancement pipeline (CLAHE)\n"
            "def preprocess_image(img_path: str):\n"
            "    pass\n"
        ),
        "constraints": ["Consistent input normalization (e.g. [0, 1] or mean/std normalization)", "Robust handling of varying aspect ratios"],
        "hints": [
            "Convolution kernels slide across the spatial grid computing element-wise dot products that activate on specific patterns.",
            "Transfer learning uses pre-trained weights (e.g. ImageNet) to provide robust low-level edge and texture detectors for free.",
        ],
    },
    "natural language processing": {
        "title": "NLP • Tokenization, Attention Mechanisms & Transformers",
        "topic": "Subword BPE, Self-Attention (Q, K, V) & Positional Embeddings",
        "difficulty": "Hard",
        "summary": "Master modern Natural Language Processing: Byte-Pair Encoding (BPE), scaled dot-product self-attention, and contextual semantic embeddings.",
        "question": (
            "Why did the self-attention mechanism in Transformers replace recurrent neural networks (RNNs and LSTMs) for sequential language processing?\n\n"
            "Explain how the Query, Key, and Value matrices interact in scaled dot-product attention: Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V."
        ),
        "code": (
            "# Scaled Dot-Product Attention formulation in Python / NumPy\n"
            "import numpy as np\n\n"
            "def self_attention(Q, K, V):\n"
            "    pass\n"
        ),
        "constraints": ["O(1) path length between any two tokens in a sequence", "Softmax normalization over key dimension"],
        "hints": [
            "Transformers process all tokens in parallel rather than sequentially, enabling massive parallel GPU training.",
            "The division by sqrt(d_k) prevents the dot products from growing excessively large for large dimensions, which would push softmax into regions with vanishingly small gradients.",
        ],
    },
}


def _build_lesson_for_skill(skill_name: str, index: int) -> TeachingLesson:
    """
    Constructs a high-grade pedagogical lesson for ANY skill.
    Uses curated deep-dive template if available; otherwise dynamically generates a rigorous lesson.
    """
    key = skill_name.strip().lower()

    # Look up direct or partial match in curated templates
    matched_template = None
    for cur_key, tmpl in CURATED_SKILL_TEMPLATES.items():
        if cur_key == key or cur_key in key or key in cur_key:
            matched_template = tmpl
            break

    if matched_template:
        return TeachingLesson(
            id=f"skill-{_slugify(skill_name)}",
            title=matched_template["title"],
            topic=matched_template["topic"],
            difficulty=matched_template["difficulty"],
            concept_summary=matched_template["summary"],
            challenge_question=matched_template["question"],
            grounding_source=f"Verified Candidate Skill: {skill_name}",
            learning_objective=f"Master production performance, concurrency invariants, and state management in {skill_name}.",
            prerequisites=[f"Core {skill_name} syntax and semantics", "Production deployment patterns"],
            diagnostic_question=f"Under what runtime conditions does {skill_name} incur catastrophic performance degradation?",
            source_references=[f"Official {skill_name} Documentation", "High-Performance Systems Architecture"],
            starter_code=matched_template["code"],
            constraints=matched_template["constraints"],
            hints=matched_template["hints"],
            status="not_started",
        )

    # Dynamic generation for any other technical skill
    return TeachingLesson(
        id=f"skill-{_slugify(skill_name)}",
        title=f"{skill_name} • Core Invariants & Production Deep Dive",
        topic=f"{skill_name} Architecture, Concurrency & Performance Gotchas",
        difficulty="Medium",
        concept_summary=(
            f"Master production engineering with {skill_name}. Analyze execution mechanics, memory lifecycle, "
            f"concurrency trade-offs, and critical anti-patterns that cause bottlenecks in production."
        ),
        challenge_question=(
            f"In a high-scale production service utilizing {skill_name}, what are the most common performance bottlenecks "
            f"or failure modes engineers encounter?\n\n"
            f"How do you profile, debug, and architect resilient solutions with {skill_name} when traffic surges by 10x?"
        ),
        grounding_source=f"Verified Candidate Skill: {skill_name}",
        learning_objective=f"Master scalable architecture and reliability engineering with {skill_name}.",
        prerequisites=[f"Basic familiarity with {skill_name}", "Backend service fundamentals"],
        diagnostic_question=f"How does {skill_name} handle connection pools, memory leaks, or thread contention under 10k requests/sec?",
        source_references=[f"Verified Technical Skills: {skill_name}", "Production Reliability Engineering"],
        starter_code=f"# {skill_name} Architectural Blueprint & Implementation\n",
        constraints=["Production reliability & failover", "Graceful resource cleanup", "Sub-second response latency"],
        hints=[
            f"Think about how {skill_name} allocates resources and manages state under concurrent operations.",
            f"Discuss metrics, profiling, and telemetry used to monitor {skill_name} health in staging and production.",
        ],
        status="not_started",
    )


def _build_lesson_for_repo(repo: Any, index: int) -> TeachingLesson:
    """
    Constructs an authentic pedagogical lesson walking through a specific GitHub repository.
    """
    name = getattr(repo, "name", None) or (repo.get("name") if isinstance(repo, dict) else f"Repository-{index}")
    language = getattr(repo, "language", None) or (repo.get("language") if isinstance(repo, dict) else "Full Stack") or "Full Stack"
    desc = getattr(repo, "description", None) or (repo.get("description") if isinstance(repo, dict) else "") or ""
    topics = getattr(repo, "topics", None) or (repo.get("topics") if isinstance(repo, dict) else []) or []
    if isinstance(topics, list) and topics:
        topics_str = ", ".join(str(t) for t in topics[:4])
    else:
        topics_str = ""

    # Synthesize tailored architectural lesson
    summary_text = (
        f"Master the codebase modularity and architectural design of '{name}'. "
        + (f"Description: {desc}. " if desc else "")
        + f"Evaluate how the {language} stack coordinates state, business logic, and API contracts."
    )

    challenge_text = (
        f"Walk me through the architecture and engineering design decisions of your repository '{name}'.\n\n"
        f"1. Problem Domain: What problem does '{name}' solve, and what guided your choice of {language} "
        + (f"and technologies ({topics_str})?" if topics_str else "for this codebase?\n")
        + f"\n2. Modularity & Flow: How is the codebase structured between presentation, business logic, and persistence layers?\n"
        f"3. Production Resilience: What was the most challenging technical hurdle, performance bottleneck, or edge-case failure you resolved in this repository?"
    )

    return TeachingLesson(
        id=f"proj-{_slugify(name)}",
        title=f"{name} • Architecture & Codebase Modularity",
        topic=f"System Design & Engineering Trade-Offs in {name} ({language})",
        difficulty="Medium" if index < 4 else "Hard",
        concept_summary=summary_text,
        challenge_question=challenge_text,
        grounding_source=f"GitHub Repository: {name} ({language})",
        learning_objective=f"Deeply understand architectural decomposition, service decoupling, and resilience in {name}.",
        prerequisites=["Git version control", f"{language} project structure"],
        diagnostic_question=f"Where are the module boundaries and contracts defined in {name}, and how are side-effects isolated?",
        source_references=[f"Candidate GitHub Repository: {name}", f"{language} Architecture Patterns"],
        starter_code=(
            f"# Architectural Decomposition of '{name}'\n"
            f"# Tech Stack: {language}\n"
            f"# 1. API & Entrypoint Boundaries\n"
            f"# 2. Core Service Logic\n"
            f"# 3. Data Flow & State Persistence\n"
        ),
        constraints=[
            f"Language & Stack: {language}",
            "Decoupled module boundaries with minimal circular dependencies",
            "Comprehensive error handling and graceful degradation",
        ],
        hints=[
            f"Focus on how modules in '{name}' communicate and avoid tight coupling.",
            f"Discuss how data mutations, caching, or background operations are handled in {language}.",
            "Highlight measurable performance improvements or architectural trade-offs you made.",
        ],
        status="not_started",
    )


# ── CORE CURRICULUM RETRIEVAL ────────────────────────────────────────────────
def get_teaching_curriculum(db: Session, current_user: User) -> TeachingCurriculumResponse:
    """
    Builds a personalized, multi-lesson pedagogical curriculum grounded in the
    candidate's authentic resources (LeetCode, HackerRank, EVERY GitHub repository, EVERY skill, Resume).
    """
    candidate_id = current_user.id
    candidate_name = (
        getattr(current_user, "name", None)
        or getattr(current_user, "full_name", None)
        or getattr(current_user, "username", None)
        or getattr(current_user, "email", "Candidate")
    )
    target_role = getattr(current_user, "target_role", None) or "Software Engineer (SDE)"

    # 1. Fetch learner knowledge profile (evidence, prerequisites, and gaps)
    knowledge_profile = build_learner_knowledge_profile(db, current_user)
    prof = None
    try:
        prof = build_unified_candidate_profile(db, current_user)
    except Exception as exc:
        logger.warning("Could not build unified profile for teaching curriculum: %s", exc)

    # 2. Fetch existing candidate progress
    user_progress_map: Dict[str, str] = {}
    user_stage_map: Dict[str, str] = {}
    progress_records: List[TeachingProgress] = []
    try:
        progress_records = db.query(TeachingProgress).filter(TeachingProgress.candidate_id == candidate_id).all()
        for p in progress_records:
            user_progress_map[p.lesson_id] = p.status
            if p.current_stage:
                user_stage_map[p.lesson_id] = p.current_stage
    except Exception as exc:
        logger.warning("Could not query teaching progress: %s", exc)

    # ── SECTION 1: DSA & ALGORITHMIC INVARIANTS (10 Core Patterns) ───────────
    dsa_lessons: List[TeachingLesson] = [
        TeachingLesson(
            id="dsa-two-sum",
            title="Array Lookups & Invariant Complements",
            topic="Two Sum (Hash Map Lookup Invariant)",
            difficulty="Easy to Medium",
            concept_summary="Learn to replace O(N²) quadratic nested loops with O(N) single-pass state lookup by tracking mathematical complements.",
            challenge_question=(
                "Given an array of integers nums and an integer target, write your approach to return indices of the two numbers that add up to target.\n\n"
                "Think through: What invariant can you store as you iterate? What are the time and space trade-offs?"
            ),
            grounding_source="HackerRank & LeetCode Grounding",
            starter_code=(
                "def two_sum(nums: list[int], target: int) -> list[int]:\n"
                "    # Step 1: Clarify state container\n"
                "    # Step 2: Iterate and check invariant\n"
                "    pass\n"
            ),
            constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "Exactly one valid answer exists"],
            hints=[
                "What is target - current element? Can you find it in O(1) time?",
                "Store elements you have already seen in an auxiliary dictionary.",
            ],
        ),
        TeachingLesson(
            id="dsa-two-pointers",
            title="Two Pointers & In-Place Boundary Shrinking",
            topic="Container With Most Water (Greedy Boundary Invariant)",
            difficulty="Medium",
            concept_summary="Master two-pointer converging boundaries where narrowing from the shorter line guarantees that no larger container is missed.",
            challenge_question=(
                "Given an array height representing vertical lines, find two lines that form a container holding the maximum water.\n\n"
                "Why is moving the pointer at the shorter line mathematically guaranteed to never skip the optimal maximum area?"
            ),
            grounding_source="LeetCode Problem Solving",
            starter_code=(
                "def max_area(height: list[int]) -> int:\n"
                "    # Left and right pointer convergence\n"
                "    pass\n"
            ),
            constraints=["2 <= height.length <= 10^5", "0 <= height[i] <= 10^4"],
            hints=[
                "Area is bounded by min(height[left], height[right]) * (right - left).",
                "Moving the taller pointer cannot increase area because width decreases and height is still limited by the shorter pointer.",
            ],
        ),
        TeachingLesson(
            id="dsa-sliding-window",
            title="Sliding Window & Substring Bounds",
            topic="Longest Substring Without Repeating Characters",
            difficulty="Medium",
            concept_summary="Master dynamic contiguous window boundaries with two pointers, expanding the right pointer while contracting the left.",
            challenge_question=(
                "Given a string s, find the length of the longest substring without duplicate characters.\n\n"
                "Explain your thought process: How do you adjust window pointers when you encounter a duplicate?"
            ),
            grounding_source="LeetCode Problem Solving",
            starter_code=(
                "def length_of_longest_substring(s: str) -> int:\n"
                "    # Two-pointer sliding window\n"
                "    pass\n"
            ),
            constraints=["0 <= s.length <= 5 * 10^4", "s consists of standard ASCII characters"],
            hints=[
                "Use a hash map to remember the last seen index of each character.",
                "If the character is seen inside the current window, jump left pointer to last_index + 1.",
            ],
        ),
        TeachingLesson(
            id="dsa-binary-search",
            title="Binary Search & Monotonic State Spaces",
            topic="Search in Rotated Sorted Array",
            difficulty="Medium",
            concept_summary="Apply logarithmic division on non-strictly monotonic arrays by identifying which half is guaranteed to remain sorted.",
            challenge_question=(
                "An array sorted in ascending order is rotated at an unknown pivot index. Given target, return its index in O(log N) time.\n\n"
                "How do you determine which half of the array is sorted at any iteration, and how do you branch your search boundaries?"
            ),
            grounding_source="LeetCode Binary Search Mastery",
            starter_code=(
                "def search(nums: list[int], target: int) -> int:\n"
                "    # O(log N) binary search on rotated array\n"
                "    pass\n"
            ),
            constraints=["1 <= nums.length <= 5000", "All values in nums are unique", "Must achieve O(log N) runtime"],
            hints=[
                "At least one half (left..mid or mid..right) is guaranteed to be strictly sorted.",
                "Check if target falls within the sorted half's bounds; if so, search that half, otherwise search the other half.",
            ],
        ),
        TeachingLesson(
            id="dsa-linked-list",
            title="Fast & Slow Pointers (Floyd's Tortoise & Hare)",
            topic="Linked List Cycle Detection & Meeting Points",
            difficulty="Medium",
            concept_summary="Eliminate auxiliary hash sets by moving two pointers at different speeds (1x vs 2x) to detect cycles in O(1) space.",
            challenge_question=(
                "Given the head of a linked list, determine if it has a cycle and find the node where the cycle begins without modifying the list.\n\n"
                "Why are fast and slow pointers guaranteed to meet within the cycle, and what is the mathematical proof for finding the cycle entry?"
            ),
            grounding_source="HackerRank Linked Lists",
            starter_code=(
                "def detect_cycle(head):\n"
                "    # Fast and slow pointers\n"
                "    pass\n"
            ),
            constraints=["Nodes: 0 to 10^4", "Must use O(1) auxiliary memory"],
            hints=[
                "If fast reaches None, there is no cycle.",
                "When fast and slow collide, resetting one pointer to head and stepping both at 1x speed leads them to meet at the cycle entry.",
            ],
        ),
        TeachingLesson(
            id="dsa-trees-lca",
            title="Binary Trees & Depth-First Search Recursion",
            topic="Lowest Common Ancestor (DFS Post-Order Traversal)",
            difficulty="Medium",
            concept_summary="Traverse tree hierarchies using post-order DFS to bubble up matching nodes and identify common ancestors.",
            challenge_question=(
                "Given a binary tree and two nodes p and q, find their Lowest Common Ancestor (LCA).\n\n"
                "How does bottom-up recursive backtracking allow parent nodes to recognize when p and q reside in opposing subtrees?"
            ),
            grounding_source="LeetCode Tree Bank",
            starter_code=(
                "def lowest_common_ancestor(root, p, q):\n"
                "    # Post-order DFS traversal\n"
                "    pass\n"
            ),
            constraints=["2 <= Number of nodes <= 10^5", "All node values are unique", "p and q exist in the tree"],
            hints=[
                "If root is None or matches p or q, return root.",
                "Recurse left and right; if both subtrees return non-null, root is the LCA.",
            ],
        ),
        TeachingLesson(
            id="dsa-heap-topk",
            title="Heaps & Priority Queues",
            topic="Top K Frequent Elements (Min-Heap Bounded Window)",
            difficulty="Medium",
            concept_summary="Reduce sorting from O(N log N) to O(N log K) by maintaining a bounded min-heap of size K while counting frequencies.",
            challenge_question=(
                "Given an integer array nums and an integer k, return the k most frequent elements.\n\n"
                "Why is a min-heap of size k superior to sorting the full frequency map, and how can Bucket Sort achieve O(N) linear time?"
            ),
            grounding_source="LeetCode Problem Solving",
            starter_code=(
                "import heapq\nfrom collections import Counter\n\n"
                "def top_k_frequent(nums: list[int], k: int) -> list[int]:\n"
                "    pass\n"
            ),
            constraints=["1 <= nums.length <= 10^5", "k is in range [1, number of unique elements]"],
            hints=[
                "Count frequencies with Counter(nums).",
                "Push (frequency, num) into a min-heap. When heap size exceeds k, pop the smallest element so only top k remain.",
            ],
        ),
        TeachingLesson(
            id="dsa-graphs-bfs",
            title="Graph Traversal & Connected Components",
            topic="Number of Islands (Grid BFS / DFS Traversal)",
            difficulty="Medium",
            concept_summary="Model 2D grids as graphs, traversing adjacent land cells (up, down, left, right) to count connected components.",
            challenge_question=(
                "Given an m x n 2D binary grid representing a map of '1's (land) and '0's (water), return the number of islands.\n\n"
                "How do you track visited cells to avoid infinite loops, and what are the recursion stack implications of DFS vs queue BFS on large grids?"
            ),
            grounding_source="LeetCode Graphs Mastery",
            starter_code=(
                "def num_islands(grid: list[list[str]]) -> int:\n"
                "    # BFS or DFS island sinking\n"
                "    pass\n"
            ),
            constraints=["m == grid.length", "n == grid[i].length", "1 <= m, n <= 300"],
            hints=[
                "Whenever you encounter a '1', increment island count and trigger a BFS/DFS to sink or mark all connected '1's as visited.",
                "For very large grids, iterative BFS avoids Python's default recursion stack limit.",
            ],
        ),
        TeachingLesson(
            id="dsa-dp-robber",
            title="Dynamic Programming & Recurrence Relations",
            topic="House Robber (Optimal Substructure & Memoization)",
            difficulty="Medium",
            concept_summary="Formulate recurrence relations by deciding between local choice trade-offs and caching subproblem solutions.",
            challenge_question=(
                "You want to maximize total money robbed along a street without triggering alarms (cannot rob two adjacent houses).\n\n"
                "What is the recurrence relation? How do you transition from an O(2^N) recursion to an O(N) DP or O(1) space solution?"
            ),
            grounding_source="Algorithmic Mastery",
            starter_code=(
                "def rob(nums: list[int]) -> int:\n"
                "    # Recurrence: max(rob(i-1), rob(i-2) + nums[i])\n"
                "    pass\n"
            ),
            constraints=["1 <= nums.length <= 100", "0 <= nums[i] <= 400"],
            hints=[
                "At house i, you either skip it (keep money from house i-1) or rob it (take nums[i] + money from i-2).",
                "Notice that you only need the previous two computed values, not the entire array!",
            ],
        ),
        TeachingLesson(
            id="dsa-dp-coin-change",
            title="Unbounded Knapsack & State Transitions",
            topic="Coin Change (Bottom-Up DP Invariant)",
            difficulty="Medium",
            concept_summary="Solve unbounded knapsack optimization by building a 1D DP table representing the minimum steps to reach each amount.",
            challenge_question=(
                "Given integer array coins and integer amount, return the fewest number of coins needed to make up that amount, or -1 if impossible.\n\n"
                "Explain the state transition dp[i] = min(dp[i], dp[i - coin] + 1). Why does a greedy choice fail on arbitrary coin denominations?"
            ),
            grounding_source="LeetCode DP Mastery",
            starter_code=(
                "def coin_change(coins: list[int], amount: int) -> int:\n"
                "    # Bottom-up DP array initialization\n"
                "    pass\n"
            ),
            constraints=["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31 - 1", "0 <= amount <= 10^4"],
            hints=[
                "Initialize dp array of size amount + 1 with infinity, and set dp[0] = 0.",
                "For every coin and for every amount from coin to target amount, update dp[i] with min(dp[i], dp[i - coin] + 1).",
            ],
        ),
    ]

    dsa_section = TeachingSection(
        id="dsa",
        title="Data Structures & Algorithms",
        badge=f"Section 01 • {len(dsa_lessons)} Algorithmic Invariants",
        description="Master problem solving, invariant state tracking, and Big-O trade-offs through progressive Socratic lessons.",
        icon="code",
        accent_color="#6366f1",
        grounding_platforms=["LeetCode Problem Bank", "HackerRank Problem Solving"],
        lessons=dsa_lessons,
    )

    # ── SECTION 2: TECHNICAL SKILLS & SYSTEM ARCHITECTURE ─────────────────────
    # Collect candidate skills from unified profile, graph queries, and resume
    raw_skills: List[str] = []
    if prof and prof.unified_skills:
        for s in prof.unified_skills:
            if s.name and isinstance(s.name, str):
                raw_skills.append(s.name.strip())

    try:
        g_skills = graph_query_service.get_candidate_skills(candidate_id) or []
        for gs in g_skills:
            s_name = gs.name if hasattr(gs, "name") else (gs.get("name") if isinstance(gs, dict) else str(gs))
            if s_name and isinstance(s_name, str):
                raw_skills.append(s_name.strip())
    except Exception as exc:
        logger.warning("Could not query candidate skills for teaching: %s", exc)

    # Filter out non-technical challenge titles (e.g., '30 Days of Code')
    ignored_skill_terms = {"30 days of code", "10 days of js", "10 days of statistics", "problem solving", "projects"}
    seen_skills: Set[str] = set()
    cleaned_skills: List[str] = []
    for sk in raw_skills:
        sk_clean = sk.strip()
        sk_lower = sk_clean.lower()
        if sk_lower in ignored_skill_terms or len(sk_clean) < 2:
            continue
        if sk_lower not in seen_skills:
            seen_skills.add(sk_lower)
            cleaned_skills.append(sk_clean)

    # If candidate has few skills, augment with core engineering skills
    fallback_skills = ["FastAPI", "React", "Python", "PostgreSQL", "Redis", "Docker", "Git", "System Design"]
    for fb in fallback_skills:
        if fb.lower() not in seen_skills:
            seen_skills.add(fb.lower())
            cleaned_skills.append(fb)

    # Generate dedicated lesson for EVERY skill
    skill_lessons: List[TeachingLesson] = [
        _build_lesson_for_skill(skill, idx) for idx, skill in enumerate(cleaned_skills)
    ]

    skills_section = TeachingSection(
        id="skills",
        title="Technical Skills & System Architecture",
        badge=f"Section 02 • {len(skill_lessons)} Candidate Skills",
        description="Master production execution, concurrency patterns, and architectural trade-offs for every verified technical skill.",
        icon="layers",
        accent_color="#ec4899",
        grounding_platforms=["Verified Technical Skills", "System Design Standards"],
        lessons=skill_lessons,
    )

    # ── SECTION 3: REAL GITHUB PROJECTS (Walk through EVERY Repository) ──────
    repos: List[Any] = []
    try:
        gh_profile = db.query(GitHubProfile).filter(GitHubProfile.user_id == candidate_id).first()
        if gh_profile:
            repos = (
                db.query(GitHubRepository)
                .filter(GitHubRepository.github_profile_id == gh_profile.id)
                .all()
            )
    except Exception as exc:
        logger.warning("Could not query GitHub repos from SQL: %s", exc)

    # Fallback/merge from unified profile projects where source == 'github'
    if not repos and prof and prof.projects:
        repos = [p for p in prof.projects if getattr(p, "source", "") == "github" or getattr(p, "url", None)]

    # Filter out empty or dot-folders (.github) while keeping ALL candidate repos
    cleaned_repos: List[Any] = []
    seen_repo_names: Set[str] = set()
    for r in repos:
        r_name = getattr(r, "name", None) or (r.get("title") if isinstance(r, dict) else (r.get("name") if isinstance(r, dict) else ""))
        if not r_name or r_name.startswith(".") or r_name.lower() in seen_repo_names:
            continue
        seen_repo_names.add(r_name.lower())
        cleaned_repos.append(r)

    # If no connected repositories, provide transparent software architecture & CI/CD lessons (never fake repos)
    if not cleaned_repos:
        project_lessons = [
            TeachingLesson(
                id="proj-architecture-modularity",
                title="Codebase Architecture & Modularity Standards",
                topic="Repository Layout, Service Decoupling & Clean Architecture",
                difficulty="Medium",
                concept_summary="You have not connected a GitHub repository yet. Learn professional repository organization, layer separation (controllers, domain services, persistence), and interface contracts.",
                challenge_question=(
                    "How do you structure a production-scale backend repository to ensure minimal coupling and maximum testability?\n\n"
                    "Walk through your preferred directory layout, how you enforce boundary contracts between services, "
                    "and how you structure dependency injection to mock database and network calls in tests."
                ),
                grounding_source="Software Architecture Standards (GitHub Not Connected)",
                learning_objective="Master professional repository architecture, dependency isolation, and decoupled design patterns.",
                prerequisites=["Basic Git version control", "Backend project organization"],
                diagnostic_question="Why should database transactions never be handled directly inside API route controllers?",
                source_references=["GitHub Architecture Standards", "Clean Architecture Principles"],
                starter_code=(
                    "# Production Architecture Blueprint\n"
                    "# 1. Presentation: API Routers & Controllers\n"
                    "# 2. Domain: Service Logic & Invariants\n"
                    "# 3. Persistence: Repository / ORM layer\n"
                ),
                constraints=["Layered separation of concerns", "No circular dependency imports"],
                hints=[
                    "Keep API endpoints thin by delegating business logic to service modules.",
                    "Define schemas/contracts for input validation and serialized outputs.",
                    "Connect your real GitHub account in settings to unlock customized repository reviews!",
                ],
                status="not_started",
            ),
            TeachingLesson(
                id="proj-cicd-code-quality",
                title="CI/CD Pipelines & Automated Code Quality",
                topic="Automated Linting, Container Builds & Regression Prevention",
                difficulty="Medium",
                concept_summary="Establish robust continuous integration pipelines that run automated unit and integration tests, lint checks, and containerized deployments on every pull request.",
                challenge_question=(
                    "In a modern CI/CD pipeline, how do you balance thorough regression test suites with fast deployment turnaround?\n\n"
                    "What stages do you include in your workflow, and how do you handle secrets, database migrations, and zero-downtime rollouts?"
                ),
                grounding_source="DevOps & CI/CD Standards (GitHub Not Connected)",
                learning_objective="Implement automated CI/CD checks, containerized pipelines, and safe production deployment workflows.",
                prerequisites=["Git workflow (branching, PRs)", "Docker and CI configuration"],
                diagnostic_question="What is the difference between blue/green deployments and canary rollouts in preventing regressions?",
                source_references=["DevOps Best Practices", "GitHub Actions CI/CD Patterns"],
                starter_code=(
                    "# CI/CD Workflow Pipeline Blueprint\n"
                    "# Steps: Lint -> Typecheck -> Unit Tests -> Integration Tests -> Container Build\n"
                ),
                constraints=["Deterministic test execution", "Zero credential leakage in build logs"],
                hints=[
                    "Run fast static analysis and unit tests before long-running integration tests.",
                    "Use branch protection rules and automated status checks on pull requests.",
                ],
                status="not_started",
            ),
        ]
    else:
        project_lessons = [
            _build_lesson_for_repo(r, idx) for idx, r in enumerate(cleaned_repos)
        ]

    projects_section = TeachingSection(
        id="projects",
        title="Real GitHub Projects & Codebases" if cleaned_repos else "Codebase Architecture & Engineering Projects",
        badge=f"Section 03 • {len(project_lessons)} {'Connected Repositories' if cleaned_repos else 'Architecture Guides'}",
        description=(
            f"Walk through architectural decisions, modularity boundaries, and technical trade-offs across all {len(project_lessons)} connected repositories."
            if cleaned_repos
            else "Connect your GitHub account in settings to review your authentic repositories. In the meantime, master production architecture and CI/CD foundations."
        ),
        icon="git-branch",
        accent_color="#f97316",
        grounding_platforms=[f"{len(project_lessons)} GitHub Repositories", "Codebase Modularity"] if cleaned_repos else ["Software Architecture Standards", "CI/CD Best Practices"],
        lessons=project_lessons,
    )

    # ── SECTION 4: RESUME & STAR BEHAVIORAL SCENARIOS ─────────────────────────
    resume_lessons: List[TeachingLesson] = []

    # 1. Real Resume Work Experience & Projects
    if prof and prof.projects:
        for p_idx, pr in enumerate(prof.projects[:6]):
            p_title = getattr(pr, "title", "Project")
            p_desc = getattr(pr, "description", "") or ""
            p_techs = getattr(pr, "technologies", []) or []
            tech_label = ", ".join(p_techs[:3]) if p_techs else "Core Tech"

            resume_lessons.append(
                TeachingLesson(
                    id=f"star-proj-{_slugify(p_title)}",
                    title=f"STAR Walkthrough: {p_title[:42]}",
                    topic=f"Executive Delivery & Engineering Impact ({tech_label})",
                    difficulty="Medium",
                    concept_summary=(
                        f"Articulate technical ownership for {p_title}. "
                        + (f"Project Details: {p_desc[:120]}. " if p_desc else "")
                        + "Frame your explanation using the STAR framework to highlight technical complexity and business results."
                    ),
                    challenge_question=(
                        f"In your resume project '{p_title}', walk me through your engineering contribution.\n\n"
                        "Structure your response using STAR:\n"
                        "• Situation: What was the technical context or user problem?\n"
                        "• Task: What specific mandate did you own?\n"
                        "• Action: What architectural choices, tools, or algorithms did you implement?\n"
                        "• Result: What quantifiable performance metric, latency improvement, or outcome was achieved?"
                    ),
                    grounding_source=f"Resume Project: {p_title}",
                    starter_code=None,
                    constraints=["Must provide concrete metrics or qualitative outcomes", "Focus on actions YOU personally drove"],
                    hints=[
                        "Avoid vague statements like 'we improved it'. Specify: 'I optimized queries, dropping latency by 35%'.",
                        "Highlight how you validated correctness through automated testing or benchmarking.",
                    ],
                )
            )

    # 2. Senior Engineering Leadership & Behavioral Scenarios
    resume_lessons.extend([
        TeachingLesson(
            id="star-incident-rca",
            title="Production Outages & Root Cause Analysis (RCA)",
            topic="High-Severity Latency Debugging & Blameless Post-Mortems",
            difficulty="Hard",
            concept_summary="Learn to articulate how you diagnosed and resolved an elusive engineering bug or production slowdown under live traffic.",
            challenge_question=(
                "Tell me about a time when a critical feature or service suffered severe latency or failed in production.\n\n"
                "Structure your response using STAR: Situation (the incident), Task (your mitigation mandate), "
                "Action (how you traced root cause using logs, profiling, and telemetry), Result (mean time to recovery and lasting prevention)."
            ),
            grounding_source="Engineering Incident Response Framework",
            starter_code=None,
            constraints=["Include specific diagnostic tooling (e.g. APM, EXPLAIN, distributed tracing)", "Focus on systematic isolation"],
            hints=[
                "Mention hypotheses you tested and ruled out before discovering the root cause.",
                "Conclude with the lasting automated regression test, alert, or circuit breaker implemented.",
            ],
        ),
        TeachingLesson(
            id="star-arch-disagreement",
            title="Architectural Disagreements & Team Alignment",
            topic="Advocating Technical Perspectives with Benchmarks & Trade-Offs",
            difficulty="Medium",
            concept_summary="Frame technical disagreements around data-driven proof-of-concept benchmarks rather than emotional debates.",
            challenge_question=(
                "Describe a time when you and a teammate or lead disagreed on an architectural decision or library choice.\n\n"
                "How did you navigate the discussion to reach consensus without stalling project velocity? What role did empirical data play?"
            ),
            grounding_source="Behavioral Leadership Standards",
            starter_code=None,
            constraints=["Constructive resolution", "Focus on technical merits and customer velocity"],
            hints=[
                "Highlight building a quick prototype or benchmark test to let empirical data decide.",
                "Demonstrate mutual respect and full commitment to team velocity once a consensus was reached.",
            ],
        ),
        TeachingLesson(
            id="star-tech-debt-velocity",
            title="Eliminating Tech Debt vs. Feature Velocity",
            topic="Refactoring Legacy Codebases without Disrupting Sprints",
            difficulty="Medium",
            concept_summary="Demonstrate how to incrementally refactor high-risk legacy modules using Strangler Fig patterns while continuing to deliver product features.",
            challenge_question=(
                "How do you balance paying down technical debt against shipping customer-facing features on tight sprint deadlines?\n\n"
                "Give an example where you successfully advocated for and executed a critical refactoring that unlocked team velocity."
            ),
            grounding_source="Software Engineering Practices",
            starter_code=None,
            constraints=["Quantifiable velocity or stability improvement", "Zero customer-facing downtime during refactoring"],
            hints=[
                "Explain how you tied technical debt to business metrics (e.g., bug rate, deployment frequency, onboarding time).",
                "Describe incremental migration strategies rather than risky 'big bang' rewrites.",
            ],
        ),
        TeachingLesson(
            id="star-ambiguous-requirements",
            title="Driving Ambiguous Requirements to Delivery",
            topic="Scoping Underspecified Features & Cross-Functional Alignment",
            difficulty="Medium",
            concept_summary="Showcase how you take a vague user request, collaborate with product stakeholders, define boundary contracts, and ship iteratively.",
            challenge_question=(
                "Tell me about a project where the requirements were vague or constantly shifting.\n\n"
                "How did you establish clarity, define technical specifications, and ensure alignment across engineering and product teams?"
            ),
            grounding_source="Product Engineering Standards",
            starter_code=None,
            constraints=["Proactive stakeholder communication", "Milestone-based phased delivery"],
            hints=[
                "Describe writing an RFC (Request for Comments) or architectural design document to solicit early feedback.",
                "Show how you decoupled core must-have deliverables from future enhancements.",
            ],
        ),
        TeachingLesson(
            id="star-mentorship-standards",
            title="Elevating Team Engineering Standards & Mentorship",
            topic="Code Reviews, Onboarding & Engineering Culture",
            difficulty="Medium",
            concept_summary="Demonstrate leadership by sharing knowledge, establishing rigorous code review practices, and mentoring junior engineers.",
            challenge_question=(
                "Describe a situation where you helped elevate code quality or mentored a teammate on an engineering concept.\n\n"
                "How do you approach code reviews to balance educational feedback with maintaining high velocity?"
            ),
            grounding_source="Engineering Mentorship Framework",
            starter_code=None,
            constraints=["Empathetic communication", "Constructive, actionable review commentary"],
            hints=[
                "Give an example of turning a recurring bug into a team knowledge-sharing session or shared utility library.",
                "Emphasize phrasing review comments as curious questions rather than rigid directives.",
            ],
        ),
    ])

    resume_section = TeachingSection(
        id="resume",
        title="Resume & STAR Behavioral Mastery",
        badge=f"Section 04 • {len(resume_lessons)} Behavioral Scenarios",
        description="Master the STAR method across your authentic resume projects and senior engineering leadership scenarios.",
        icon="file-text",
        accent_color="#10b981",
        grounding_platforms=["Candidate Resume", "Engineering Leadership Framework"],
        lessons=resume_lessons,
    )

    all_sections = [dsa_section, skills_section, projects_section, resume_section]
    
    # Enrich all lessons with required pedagogical metadata, RAG resources, and user progress status
    for sec in all_sections:
        for l in sec.lessons:
            if not l.learning_objective:
                l.learning_objective = f"Master core algorithmic and engineering principles for {l.topic}."
            if not l.prerequisites:
                l.prerequisites = ["Basic programming syntax", "Algorithmic thinking"]
            if not l.diagnostic_question:
                l.diagnostic_question = f"What is the time complexity and space trade-off of the naive approach to {l.topic}?"
            if not l.source_references:
                l.source_references = [l.grounding_source]
            l.status = user_progress_map.get(l.id, "not_started")
            l.current_stage = user_stage_map.get(l.id, "objective")
            l.why_matters_for_role = f"Core competency for {target_role} responsibilities."
            l.assessment_question = f"How would you explain the fundamental principle of {l.topic} to a peer, and what edge cases would you guard against?"
            l.practice_exercise = f"Apply {l.topic} to design an optimal, production-ready solution respecting bounded memory constraints."

            # Ground with candidate project if matching
            matching_proj = next(
                (p for p in knowledge_profile.verified_projects if any(t in l.topic.lower() or t in l.id.lower() for t in [str(x).lower() for x in p.get("technologies", [])])),
                None
            )
            if matching_proj:
                l.candidate_project_connection = f"Demonstrated in your repository project '{matching_proj.get('title')}'."

            # Retrieve real technical documentation / resources
            res_items = retrieve_teaching_resources_for_lesson(
                concept_title=l.topic,
                candidate_projects=knowledge_profile.verified_projects,
                limit=3,
            )
            l.resources = [r.model_dump() for r in res_items]

    # Compute recommended start lesson based on knowledge profile gaps and prerequisites
    recommended_start = None
    for gap in knowledge_profile.recommended_learning_order:
        for sec in all_sections:
            for l in sec.lessons:
                if (gap.lower() in l.id.lower() or gap.lower() in l.topic.lower()) and l.status not in ("completed", "mastered"):
                    recommended_start = l.id
                    break
            if recommended_start:
                break
        if recommended_start:
            break
    if not recommended_start and dsa_lessons:
        recommended_start = dsa_lessons[0].id

    # Background sync to Neo4j
    try:
        completed_ids = [p.lesson_id for p in progress_records if p.status in ("completed", "mastered")]
        mastered_ids = [p.lesson_id for p in progress_records if p.status == "mastered"]
        concept_graph_service.sync_candidate_concept_graph(
            candidate_id=candidate_id,
            skills_inventory=knowledge_profile.skills_inventory,
            verified_projects=knowledge_profile.verified_projects,
            completed_lessons=completed_ids,
            mastered_lessons=mastered_ids,
        )
    except Exception as exc:
        logger.debug("Background Neo4j sync non-blocking warning: %s", exc)

    total_count = sum(len(s.lessons) for s in all_sections)

    return TeachingCurriculumResponse(
        sections=all_sections,
        total_lessons=total_count,
        candidate_name=candidate_name,
        target_role=target_role,
        recommended_start_lesson_id=recommended_start,
        knowledge_profile_summary={
            "gaps_count": len(knowledge_profile.knowledge_gaps),
            "strengths_count": len(knowledge_profile.demonstrated_strengths),
            "top_gaps": knowledge_profile.knowledge_gaps[:5],
            "top_strengths": knowledge_profile.demonstrated_strengths[:5],
        },
    )



# ── EVALUATION & TEACHING ENGINE ─────────────────────────────────────────────
LANGUAGE_NAMES_MAP: Dict[str, str] = {
    "en": "English",
    "ta": "Tamil (தமிழ் / Conversational Tanglish)",
    "hi": "Hindi (हिन्दी / Conversational Hinglish)",
    "te": "Telugu (తెలుగు)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "es": "Spanish (Español)",
    "fr": "French (Français)",
    "de": "German (Deutsch)",
}


def evaluate_and_teach(
    req: TeachingEvaluationRequest,
    current_user: User,
) -> TeachingEvaluationResponse:
    """
    Evaluates candidate's thoughts and code, highlighting what they got right,
    what they got wrong or missed, and delivering a comprehensive pedagogical masterclass
    in the candidate's selected language.
    """
    user_thoughts = (req.candidate_thoughts or "").strip()
    code = (req.candidate_code or "").strip()
    prompt_topic = req.concept_title or "Engineering Concept"
    question = req.question_prompt or "Technical Scenario"
    role = req.role or "Software Engineer"
    section = req.section_id or "dsa"
    lang_code = (req.language or "en").strip().lower()
    target_lang_name = LANGUAGE_NAMES_MAP.get(lang_code, "English")

    multilingual_clause = ""
    if lang_code != "en":
        multilingual_clause = (
            f"\n\nCRITICAL MULTILINGUAL PEDAGOGY DIRECTIVE:\n"
            f"The candidate has requested learning and pedagogical feedback in {target_lang_name}.\n"
            f"You MUST write 'what_is_right', 'what_is_wrong', 'masterclass_lesson', 'key_takeaway', and 'suggested_follow_up' "
            f"in fluent, natural conversational {target_lang_name}.\n"
            f"Keep programming syntax, keywords, and code identifiers in standard English/code format, "
            f"but explain the intuition, logic, mistakes, and masterclass breakdown entirely in {target_lang_name}.\n"
        )

    system_prompt = (
        "You are Dr. Cyra Vance, Master AI Technical Educator & Lead Tech Mentor at CareerVerse AI. "
        "You are NOT acting as a cold interviewer. You are a warm, rigorous, world-class TEACHER & MENTOR. "
        "Your teaching goal is to help the candidate master this concept by clearly showing what they got RIGHT, "
        "what they got WRONG or MISSED, and delivering an unforgettable pedagogical MASTERCLASS LESSON. "
        f"Candidate Target Role: {role}. "
        f"Curriculum Section: {section.upper()}. "
        f"Concept Being Mastered: {prompt_topic}. "
        f"Question / Challenge: {question}."
        f"{multilingual_clause}\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        f'  "what_is_right": "Detailed, encouraging breakdown in {target_lang_name} of what the candidate got right, praising their correct intuition, good complexity reasoning, or clean choices.",\n'
        f'  "what_is_wrong": "Direct, constructive, kind explanation in {target_lang_name} of what was incorrect, missing, sub-optimal (e.g. quadratic runtime, unhandled duplicates, edge cases, missing metric).",\n'
        f'  "masterclass_lesson": "Comprehensive masterclass lesson in {target_lang_name} covering: 1) Core Mental Model & Intuitive Analogy, 2) The Top-Tier 4-Step Solution Framework elite candidates use, 3) Critical Complexity & Scalability Trade-offs.",\n'
        '  "optimal_solution": "The clean, production-grade code snippet or architectural diagram blueprint representing the gold standard answer.",\n'
        f'  "key_takeaway": "One punchy, memorable engineering principle in {target_lang_name} to remember forever in technical interviews.",\n'
        f'  "suggested_follow_up": "One engaging check-in concept question in {target_lang_name} to verify candidate understanding."\n'
        "}"
    )

    user_payload = (
        f"Candidate's Thought Process & Explanation:\n{user_thoughts}\n\n"
        f"Candidate's Workspace Code (if any):\n```{code}```\n"
    )

    try:
        provider = get_model_provider()
        res = provider.generate_text(
            system_prompt=system_prompt,
            user_message=user_payload,
            temperature=0.3,
            max_completion_tokens=1000,
        )
        if res and res.content and res.content.strip():
            raw_text = res.content.strip()
            # Clean possible markdown wrap
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            parsed = json.loads(raw_text.strip())

            return TeachingEvaluationResponse(
                what_is_right=parsed.get("what_is_right", "You demonstrated great initial intuition and clear problem dissection."),
                what_is_wrong=parsed.get("what_is_wrong", "Watch out for edge constraints like boundary sizes and duplicate keys."),
                masterclass_lesson=parsed.get("masterclass_lesson", "In technical interviews, state tracking invariants turn quadratic work into linear lookups."),
                optimal_solution=parsed.get("optimal_solution", "# Optimal Solution\n# State tracking with hash map\ndef solution():\n    pass"),
                key_takeaway=parsed.get("key_takeaway", "Trade auxiliary space for time whenever lookups dominate the bottleneck."),
                suggested_follow_up=parsed.get("suggested_follow_up", "How would your solution adapt if memory was strictly capped?"),
            )
    except Exception as exc:
        logger.warning("Error in evaluate_and_teach LLM generation: %s", exc)

    # Localized high-quality fallback pedagogical responses
    if lang_code == "ta":
        fallback_right = (
            "✅ **நீங்கள் சரியாகப் புரிந்து கொண்டவை (What You Got Right)**:\n"
            "பிரச்சனையின் அடிப்படை நோக்கத்தை நீங்கள் சரியாகக் கண்டறிந்துள்ளீர்கள். "
            "மதிப்புகளுக்கிடையேயான தொடர்பை யோசித்து அணுகிய விதம் ஒரு சிறந்த பொறியியல் குணம்."
        )
        fallback_wrong = (
            "⚠️ **மேம்படுத்த வேண்டியவை (What Was Sub-Optimal)**:\n"
            "துணை state container (Hash Map) இல்லாமல் முந்தைய உறுப்புகளை மீண்டும் மீண்டும் ஸ்கேன் செய்வது O(N²) நேர விரயத்தை உண்டாக்கும். "
            "மேலும் empty arrays மற்றும் boundary conditions-களை கவனித்து கையாள வேண்டும்."
        )
        fallback_lesson = (
            "🎓 **Dr. Cyra-வின் மாஸ்டர்கிளாஸ் பாடம் (Masterclass Breakdown)**:\n\n"
            "💡 **1. முக்கிய சிந்தனை முறை (Mental Model)**:\n"
            "ஒவ்வொரு முறையும் பின்னோக்கிச் சென்று பார்க்காமல், நீங்கள் கடந்து வந்த மதிப்புகளை ஒரு பாக்கெட் டைரியில் (Hash Map) குறித்துக் கொள்ளுங்கள். புதிய உறுப்பைப் பார்க்கும்போது O(1) நேரத்தில் சரிபார்க்கலாம்.\n\n"
            "📐 **2. 4-படி தீர்வு முறை (4-Step Framework)**:\n"
            "• படி 1: எல்கை மற்றும் duplicate வரம்புகளை உறுதி செய்யுங்கள்.\n"
            "• படி 2: கணித invariant-ஐ வரையறுக்கவும் (`complement = target - num`).\n"
            "• படி 3: O(N) ஒற்றை pass hash map lookup பயன்படுத்தவும்.\n"
            "• படி 4: Base case மற்றும் boundary-களை கையாளவும்.\n\n"
            "⚖️ **3. Complexity சமநிலை**:\n"
            "நேர சிக்கலானது O(N²)-லிருந்து O(N)-ஆகக் குறைகிறது."
        )
        fallback_takeaway = "தேடல்களை O(1) நேரத்திற்கு மாற்ற auxiliary hash map அல்லது two-pointer உத்திகளை எப்போதும் பயன்படுத்துங்கள்."
        fallback_followup = "கொடுக்கப்பட்ட array ஏற்கனவே ascending order-ல் sort செய்யப்பட்டு இருந்தால் உங்கள் அணுகுமுறை எவ்வாறு மாறும்?"
    elif lang_code == "hi":
        fallback_right = (
            "✅ **आपने क्या सही समझा (What You Got Right)**:\n"
            "आपने समस्या के मुख्य उद्देश्य को सही पहचाना और महसूस किया कि एक व्यवस्थित iterative दृष्टिकोण की आवश्यकता है। "
            "मानों के बीच संबंधों पर विचार करने का आपका अंतर्ज्ञान एक बेहतरीन संकेत है।"
        )
        fallback_wrong = (
            "⚠️ **कहाँ सुधार की आवश्यकता है (What Was Sub-Optimal)**:\n"
            "बिना किसी सहायक container (Hash Map) के पिछले तत्वों को दोबारा स्कैन करने पर O(N²) समय लग जाता है। "
            "साथ ही खाली इनपुट और सीमा सीमाओं (boundary conditions) को भी संभालना जरूरी है।"
        )
        fallback_lesson = (
            "🎓 **Dr. Cyra का मास्टरक्लास सबक (Masterclass Breakdown)**:\n\n"
            "💡 **1. मुख्य मानसिक मॉडल (Mental Model)**:\n"
            "हर बार पीछे मुड़कर देखने के बजाय, जो कुछ आपने देखा उसे एक पॉकेट डायरी (Hash Map) में नोट कर लें। नया तत्व आने पर O(1) समय में तुरंत जांच लें।\n\n"
            "📐 **2. 4-चरणीय ढांचा (4-Step Framework)**:\n"
            "• चरण 1: डुप्लीकेट और सीमाओं की पुष्टि करें।\n"
            "• चरण 2: गणितीय invariant परिभाषित करें (`complement = target - num`)।\n"
            "• चरण 3: O(N) सिंगल-पास हैश मैप लूकअप अपनाएं।\n"
            "• चरण 4: शून्य या खाली इनपुट को संभालें।\n\n"
            "⚖️ **3. ट्रेड-ऑफ**:\n"
            "रनटाइम O(N²) से घटकर O(N) हो जाता है।"
        )
        fallback_takeaway = "जब भी बार-बार खोजने की बात आए, auxiliary memory का उपयोग करके समय बचाइए।"
        fallback_followup = "यदि इनपुट पहले से ही आरोही क्रम (sorted order) में होता, तो आपका समाधान कैसे बदलता?"
    else:
        fallback_right = (
            "✅ **What You Got Right**:\n"
            "You correctly identified the core objective of the problem and realized that an iterative approach is required. "
            "Your intuition to consider how values relate to each other is a strong engineering signal."
        )
        fallback_wrong = (
            "⚠️ **What Was Wrong or Sub-Optimal**:\n"
            "Without an auxiliary state container, checking previous elements requires rescanning, leading to O(N²) time complexity. "
            "Furthermore, edge cases like empty inputs, single-element arrays, and negative bounds must be checked explicitly."
        )
        fallback_lesson = (
            "🎓 **Dr. Cyra's Masterclass Breakdown**:\n\n"
            "💡 **1. Core Mental Model & Intuition**:\n"
            "Think of this problem like keeping a ledger while walking down a conveyor belt. Instead of stopping and turning around to re-inspect every item you passed, you write down what you saw in a pocket ledger (Hash Map). When you pick up a new item, you check your ledger in O(1) time.\n\n"
            "📐 **2. The Top-Tier 4-Step Framework**:\n"
            "• Step 1: Clarify boundaries and duplicate handling.\n"
            "• Step 2: Define the mathematical invariant (e.g. `complement = target - num`).\n"
            "• Step 3: Use single-pass hash lookups to maintain O(N) runtime.\n"
            "• Step 4: Handle zero or empty boundary states.\n\n"
            "⚖️ **3. Complexity Trade-Offs**:\n"
            "Runtime drops from O(N²) to O(N), trading O(N) auxiliary memory space."
        )
        fallback_takeaway = "Always evaluate whether a hash map or two-pointer window can eliminate quadratic rescans in O(1) lookup time."
        fallback_followup = "What would you change if the input array was already guaranteed to be sorted in ascending order?"

    fallback_sol = (
        "def two_sum(nums: list[int], target: int) -> list[int]:\n"
        "    seen = {}\n"
        "    for idx, num in enumerate(nums):\n"
        "        diff = target - num\n"
        "        if diff in seen:\n"
        "            return [seen[diff], idx]\n"
        "        seen[num] = idx\n"
        "    return []\n"
    )

    return TeachingEvaluationResponse(
        what_is_right=fallback_right,
        what_is_wrong=fallback_wrong,
        masterclass_lesson=fallback_lesson,
        optimal_solution=fallback_sol,
        key_takeaway=fallback_takeaway,
        suggested_follow_up=fallback_followup,
    )


# ── INTERACTIVE SOCRATIC TEACHING ENGINE & PROGRESS ──────────────────────────
def interact_with_teaching_lesson(
    db: Session,
    current_user: User,
    req: TeachingInteractionRequest,
) -> TeachingInteractionResponse:
    """
    Handles interactive multi-turn Socratic pedagogy for a teaching lesson.
    Actions supported:
      - 'hint': Reveals the next hint without giving away the full answer.
      - 'simpler': Offers a reduced, concrete toy example with smaller numbers.
      - 'explain': Delivers step-by-step masterclass breakdown.
      - 'code': Demonstrates reference starter/optimal code.
      - 'answer': Evaluates candidate thoughts/code, provides Socratic feedback,
                  and tracks lesson completion / mastery.
    """
    curriculum = get_teaching_curriculum(db, current_user)
    target_lesson: Optional[TeachingLesson] = None
    for sec in curriculum.sections:
        if sec.id == req.section_id:
            for les in sec.lessons:
                if les.id == req.lesson_id:
                    target_lesson = les
                    break
            if target_lesson:
                break

    if not target_lesson:
        for sec in curriculum.sections:
            for les in sec.lessons:
                if les.id == req.lesson_id:
                    target_lesson = les
                    break
            if target_lesson:
                break

    if not target_lesson:
        target_lesson = TeachingLesson(
            id=req.lesson_id,
            title="Interactive Technical Lesson",
            topic="Core Engineering Concepts",
            difficulty="Medium",
            concept_summary="Master this engineering concept through guided Socratic problem solving.",
            challenge_question="Walk through your algorithmic approach and constraints.",
            grounding_source="Socratic Masterclass",
            starter_code="# Implement your approach\npass\n",
            hints=[
                "Break the problem down into smaller invariant subproblems.",
                "Consider which data structure offers optimal lookup time.",
            ],
            constraints=["Input boundaries and edge cases"],
        )

    progress = (
        db.query(TeachingProgress)
        .filter(
            TeachingProgress.candidate_id == current_user.id,
            TeachingProgress.section_id == req.section_id,
            TeachingProgress.lesson_id == req.lesson_id,
        )
        .first()
    )
    if not progress:
        progress = TeachingProgress(
            candidate_id=current_user.id,
            section_id=req.section_id,
            lesson_id=req.lesson_id,
            status="in_progress",
            turns=[],
            hints_used=0,
            current_stage="objective",
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    lang_code = (req.language or "en").strip().lower()
    action = (req.action or "answer").strip().lower()

    # Stages: objective -> explanation -> question -> feedback -> practice -> assessment -> completed
    stage_sequence = ["objective", "explanation", "question", "feedback", "practice", "assessment", "completed"]
    current_stage = progress.current_stage or "objective"
    next_stage = None

    teaching_message = ""
    what_right: Optional[str] = None
    what_wrong: Optional[str] = None
    step_by_step: Optional[str] = None
    example_grounding: Optional[str] = None
    code_demo: Optional[str] = None
    follow_up: Optional[str] = None
    hint_revealed: Optional[str] = None
    practice_exercise: Optional[str] = None
    assessment_evaluation: Optional[Dict[str, Any]] = None
    is_complete: bool = False

    # Retrieve real resources
    retrieved_resources = retrieve_teaching_resources_for_lesson(
        concept_title=target_lesson.topic,
        candidate_projects=[],
        limit=3,
    )
    resource_dicts = [r.model_dump() for r in retrieved_resources]

    if action == "hint":
        hints = target_lesson.hints or [
            "Consider tracking state with an auxiliary container to avoid quadratic scans.",
            "Formulate a mathematical invariant connecting current element to target.",
        ]
        hints_used = progress.hints_used or 0
        if hints_used < len(hints):
            hint_revealed = hints[hints_used]
            progress.hints_used = hints_used + 1
        else:
            hint_revealed = hints[-1] + " (All hints unlocked! Synthesize these insights into your solution.)"

        if lang_code == "ta":
            teaching_message = f"💡 **குறிப்பு #{progress.hints_used} (Hint)**:\n{hint_revealed}\n\nஇந்தக் குறிப்பை வைத்து உங்கள் அடுத்த படிநிலையை விளக்குங்கள்!"
        elif lang_code == "hi":
            teaching_message = f"💡 **संकेत #{progress.hints_used} (Hint)**:\n{hint_revealed}\n\nइस संकेत के आधार पर अपने अगले कदम और विचार स्पष्ट करें!"
        else:
            teaching_message = f"💡 **Hint #{progress.hints_used}**:\n{hint_revealed}\n\nHow does this change your approach? Formulate your next step."

    elif action == "simpler":
        if "two sum" in target_lesson.topic.lower() or "two-sum" in target_lesson.id.lower():
            if lang_code == "ta":
                example_grounding = (
                    "🔍 **எளிய உதாரணம் (Toy Example)**:\n"
                    "எடுத்துக்காட்டாக: `nums = [2, 7, 11, 15]`, `target = 9`.\n"
                    "• படி 1: 2-ஐப் பார்க்கும்போது, `9 - 2 = 7` தேவை. Map காலியாக உள்ளது -> `{2: 0}`-ஐ பதிவு செய்கிறோம்.\n"
                    "• படி 2: 7-ஐப் பார்க்கும்போது, `9 - 7 = 2` Map-ல் index 0-ல் உள்ளது! உடனே `[0, 1]` விடையாகக் கிடைக்கிறது."
                )
            elif lang_code == "hi":
                example_grounding = (
                    "🔍 **सरल उदाहरण (Toy Example)**:\n"
                    "मान लीजिए: `nums = [2, 7, 11, 15]`, `target = 9`.\n"
                    "• चरण 1: जब 2 देखते हैं, हमें `9 - 2 = 7` चाहिए। मैप खाली है -> `{2: 0}` दर्ज करें।\n"
                    "• चरण 2: जब 7 देखते हैं, `9 - 7 = 2` पहले से इंडेक्स 0 पर मौजूद है! तुरंत उत्तर `[0, 1]`।"
                )
            else:
                example_grounding = (
                    "🔍 **Concrete Toy Example**:\n"
                    "Let `nums = [2, 7, 11, 15]` and `target = 9`.\n"
                    "• Step 1: Examine 2. Complement needed is `9 - 2 = 7`. Map is empty -> record `{2: 0}`.\n"
                    "• Step 2: Examine 7. Complement needed is `9 - 7 = 2`. 2 is already in the map at index 0! Return `[0, 1]` in O(1) lookup."
                )
        else:
            example_grounding = (
                f"🔍 **Simplified Intuitive Walkthrough for {target_lesson.topic}**:\n"
                f"Imagine the smallest possible valid input (e.g. 2-3 items). Instead of considering complex constraints, "
                f"trace the invariant step by step: {target_lesson.concept_summary}"
            )
        teaching_message = example_grounding

    elif action == "explain":
        current_stage = "explanation"
        step_by_step = (
            f"🎓 **Masterclass Breakdown: {target_lesson.title}**\n\n"
            f"💡 **1. Core Mental Model & Intuition**:\n{target_lesson.concept_summary}\n\n"
            f"📐 **2. 4-Step Solution Framework**:\n"
            f"• Step 1: Clarify boundaries ({', '.join(target_lesson.constraints[:2]) if target_lesson.constraints else 'boundary bounds'}).\n"
            f"• Step 2: Define mathematical invariant or state container.\n"
            f"• Step 3: Iterate with state lookups to eliminate quadratic scans.\n"
            f"• Step 4: Handle zero or empty boundary cases.\n\n"
            f"⚖️ **3. Complexity Trade-Offs**:\nTrades minimal auxiliary memory to drop runtime to optimal linear/logarithmic bounds."
        )
        teaching_message = step_by_step

    elif action == "why":
        teaching_message = (
            f"🧠 **Architectural & Invariant Proof for {target_lesson.topic}**:\n\n"
            f"• **Why does this pattern exist?** Brute-force scanning explores redundant permutations, incurring O(N²) or exponential bounds.\n"
            f"• **The Mathematical/System Invariant**: By maintaining state (e.g. Hash complement, Monotonic bounds, or ACID transaction isolation), "
            f"every element visited prunes impossible candidate states immediately.\n"
            f"• **Production Impact**: In live systems, transforming an O(N²) quadratic operation to O(N) reduces CPU wall-clock latency from seconds to milliseconds under high concurrent traffic."
        )

    elif action == "code":
        code_demo = target_lesson.starter_code or "# Reference optimal implementation\npass"
        teaching_message = f"💻 **Reference Blueprint & Starter Code**:\n```python\n{code_demo}\n```"

    elif action == "practice":
        current_stage = "practice"
        practice_exercise = (
            f"🛠️ **Interactive Practice Exercise for {target_lesson.topic}**:\n\n"
            f"**Task**: {target_lesson.challenge_question}\n\n"
            f"**Constraints to satisfy**:\n" + "\n".join(f"• {c}" for c in (target_lesson.constraints or ['O(N) time complexity', 'Bounded memory'])) + "\n\n"
            f"Draft your approach or workspace code in the editor, then submit to test your solution!"
        )
        teaching_message = practice_exercise

    elif action == "assess":
        current_stage = "assessment"
        cand_resp = (req.candidate_response or "").strip()
        cand_code = (req.candidate_code or "").strip()
        combined_text = (cand_resp + " " + cand_code).lower()

        # Score assessment objectively (0-100)
        score = 0
        feedback_notes = []

        if len(cand_resp) >= 40 or len(cand_code) >= 30:
            score += 30
            feedback_notes.append("Thorough and detailed response provided.")
        else:
            feedback_notes.append("Response is brief; consider elaborating on trade-offs and edge cases.")

        has_invariants = any(w in combined_text for w in ["invariant", "complement", "hash", "pointer", "boundary", "window", "binary", "dp", "memo", "tree", "index"])
        if has_invariants:
            score += 35
            feedback_notes.append("Correct core algorithmic invariants and state structures identified.")
        else:
            feedback_notes.append("Missing explicit formulation of the core invariant or state lookup.")

        has_complexity = any(w in combined_text for w in ["o(n)", "o(log", "o(1)", "time complexity", "space complexity", "runtime"])
        if has_complexity:
            score += 20
            feedback_notes.append("Big-O time and space complexity explicitly addressed.")
        else:
            feedback_notes.append("Specify time and auxiliary space bounds to demonstrate production rigor.")

        has_edge_cases = any(w in combined_text for w in ["empty", "null", "none", "duplicate", "zero", "negative", "boundary", "edge"])
        if has_edge_cases:
            score += 15
            feedback_notes.append("Edge cases and boundary conditions accounted for.")

        # Configurable mastery policy: score >= 80 marks mastered
        is_mastered = score >= 80
        if is_mastered:
            is_complete = True
            progress.status = "mastered"
            current_stage = "completed"
            teaching_message = (
                f"🏆 **Assessment Passed with Mastery! (Score: {score}/100)**\n\n"
                f"You demonstrated rigorous understanding of {target_lesson.topic}.\n\n"
                + "\n".join(f"✅ {note}" for note in feedback_notes)
                + f"\n\nConcept has been updated to **MASTERED** in your knowledge profile."
            )
        else:
            progress.status = "in_progress"
            teaching_message = (
                f"📝 **Assessment Feedback (Score: {score}/100)**\n\n"
                f"You made solid progress on {target_lesson.topic}, but haven't demonstrated complete mastery yet (Target: 80+).\n\n"
                + "\n".join(f"• {note}" for note in feedback_notes)
                + "\n\nReview the hints, simplify the problem with a toy example, and submit an updated formulation!"
            )

        progress.assessment_score = score
        progress.mastery_evidence = {
            "score": score,
            "status": progress.status,
            "evaluated_at": datetime.utcnow().isoformat(),
            "notes": feedback_notes,
        }
        assessment_evaluation = progress.mastery_evidence

    elif action == "next_stage":
        idx = stage_sequence.index(current_stage) if current_stage in stage_sequence else 0
        if idx < len(stage_sequence) - 1:
            current_stage = stage_sequence[idx + 1]
            teaching_message = f"Transitioned to stage: **{current_stage.upper()}**."
        else:
            teaching_message = "Lesson already in final completed stage."

    elif action == "answer":
        cand_resp = (req.candidate_response or "").strip()
        cand_code = (req.candidate_code or "").strip()

        eval_req = TeachingEvaluationRequest(
            section_id=req.section_id,
            lesson_id=req.lesson_id,
            concept_title=target_lesson.topic,
            question_prompt=target_lesson.challenge_question,
            candidate_thoughts=cand_resp or (cand_code if cand_code else "Candidate approach formulation."),
            candidate_code=cand_code or None,
            role=curriculum.target_role,
            language=req.language or "en",
        )
        eval_res = evaluate_and_teach(eval_req, current_user)
        what_right = eval_res.what_is_right
        what_wrong = eval_res.what_is_wrong
        step_by_step = eval_res.masterclass_lesson
        code_demo = eval_res.optimal_solution
        follow_up = eval_res.suggested_follow_up

        combined_text = (cand_resp + " " + cand_code).lower()
        has_substance = len(cand_resp) >= 30 or len(cand_code) >= 20
        has_optimal_signal = any(
            term in combined_text
            for term in ["hash", "map", "dict", "o(n)", "pointer", "complement", "window", "binary", "tree", "heap", "stack"]
        )

        if has_substance and has_optimal_signal:
            is_complete = True
            progress.status = "mastered" if (progress.hints_used or 0) == 0 else "completed"
            current_stage = "completed"
        elif len(cand_resp) >= 40:
            is_complete = True
            progress.status = "completed"
            current_stage = "practice"
        else:
            is_complete = False
            progress.status = "in_progress"
            current_stage = "feedback"

        teaching_message = f"{what_right}\n\n{what_wrong}\n\n{step_by_step}"

    # Determine recommended next lesson
    recommended_next_id = None
    all_lessons_in_sec = [l.id for sec in curriculum.sections if sec.id == req.section_id for l in sec.lessons]
    if req.lesson_id in all_lessons_in_sec:
        curr_idx = all_lessons_in_sec.index(req.lesson_id)
        if curr_idx < len(all_lessons_in_sec) - 1:
            recommended_next_id = all_lessons_in_sec[curr_idx + 1]

    progress.current_stage = current_stage
    progress.recommended_next_lesson_id = recommended_next_id

    turn_record = {
        "action": action,
        "current_stage": current_stage,
        "candidate_response": req.candidate_response,
        "candidate_code": req.candidate_code,
        "teaching_message": teaching_message[:500] if teaching_message else "",
        "is_complete": is_complete,
    }
    turns = list(progress.turns or [])
    turns.append(turn_record)
    progress.turns = turns
    db.commit()
    db.refresh(progress)

    return TeachingInteractionResponse(
        section_id=req.section_id,
        lesson_id=req.lesson_id,
        action=action,
        teaching_message=teaching_message,
        current_stage=current_stage,
        next_stage=next_stage,
        what_is_right=what_right,
        what_is_wrong=what_wrong,
        step_by_step_explanation=step_by_step,
        example_grounding=example_grounding,
        code_demonstration=code_demo,
        follow_up_question=follow_up,
        hint_revealed=hint_revealed,
        practice_exercise=practice_exercise,
        assessment_evaluation=assessment_evaluation,
        resources=resource_dicts,
        is_lesson_complete=is_complete,
        mastery_status=progress.status,
        recommended_next_lesson_id=recommended_next_id,
    )


def get_candidate_teaching_progress(db: Session, current_user: User) -> TeachingProgressResponse:
    """
    Returns candidate progress metrics across all teaching sections and lessons,
    including active stages and verified mastery evidence.
    """
    records = db.query(TeachingProgress).filter(TeachingProgress.candidate_id == current_user.id).all()
    completed = [r.lesson_id for r in records if r.status in ("completed", "mastered")]
    mastered = [r.lesson_id for r in records if r.status == "mastered"]

    sec_counts: Dict[str, Dict[str, Any]] = {
        "dsa": {"completed": 0, "mastered": 0, "total": 10},
        "skills": {"completed": 0, "mastered": 0, "total": 8},
        "projects": {"completed": 0, "mastered": 0, "total": 2},
        "resume": {"completed": 0, "mastered": 0, "total": 6},
    }
    lesson_stages: Dict[str, str] = {}
    mastery_evidence: Dict[str, Any] = {}

    for r in records:
        s = r.section_id
        if s not in sec_counts:
            sec_counts[s] = {"completed": 0, "mastered": 0, "total": 1}
        if r.status in ("completed", "mastered"):
            sec_counts[s]["completed"] += 1
        if r.status == "mastered":
            sec_counts[s]["mastered"] += 1
        if r.current_stage:
            lesson_stages[r.lesson_id] = r.current_stage
        if r.mastery_evidence:
            mastery_evidence[r.lesson_id] = r.mastery_evidence

    return TeachingProgressResponse(
        completed_lessons=completed,
        mastered_lessons=mastered,
        section_progress=sec_counts,
        lesson_stages=lesson_stages,
        mastery_evidence=mastery_evidence,
    )


# ── CONVERSATIONAL TUTOR: DR. CYRA VANCE ─────────────────────────────────────
def chat_with_teaching_mentor(
    db: Session,
    current_user: User,
    req: TeachingChatRequest,
) -> TeachingChatResponse:
    """
    Persistent conversational tutor (Dr. Cyra Vance):
    - Grounded in verified candidate repositories, skills, and official documentation
    - Answers natural questions ('Explain simply', 'Why do we need this?', 'Code walkthrough', 'Repo connection')
    - Separates ordinary tutoring from assessment mode (never grades ordinary Q&A)
    - Persists conversation turns in PostgreSQL TeachingProgress
    """
    from app.services.skill_learning_service import build_skill_learning_path
    from app.services.repository_understanding_service import (
        build_project_interview_prep,
        build_project_learning_journey,
        build_repository_understanding,
        find_related_implementation_files,
        extract_code_structure_and_loops,
    )

    mode = (req.mode or "skill").strip().lower()
    target_id = req.target_id.strip()
    lesson_id = req.lesson_id or f"{mode}-{_slugify(target_id)}"
    user_msg = req.message.strip()
    is_assessment = bool(req.is_assessment)
    code_ws = (req.code_workspace or req.workspace_code or req.active_file_content or "").strip()
    lang_code = (req.language or "en").strip().lower()
    target_lang = LANGUAGE_NAMES_MAP.get(lang_code, "English")

    context_summary = ""
    citations: List[Dict[str, Any]] = []
    companion_files: List[Dict[str, Any]] = []
    active_path: Optional[str] = None
    limitations_note: Optional[str] = None
    current_lesson_title = "Technical Learning Session"
    connected_projects_info = ""

    # Mode A: Skill Learning Context
    if mode == "skill":
        try:
            skill_path = build_skill_learning_path(db, target_id, current_user)
            context_summary = f"Skill: {skill_path.skill_name}. Total Stages: {skill_path.total_stages}. "
            if skill_path.connected_projects:
                connected_projects_info = (
                    f"Candidate has demonstrated {skill_path.skill_name} in their connected GitHub repository: "
                    f"'{skill_path.connected_projects[0].get('title')}'."
                )

            # Find matching lesson if lesson_id provided
            target_lesson = None
            for stage in skill_path.stages:
                for les in stage.lessons:
                    if les.id == req.lesson_id:
                        target_lesson = les
                        break
                if target_lesson:
                    break

            if target_lesson:
                current_lesson_title = target_lesson.title
                context_summary += (
                    f"Active Lesson: {target_lesson.title}. Topic: {target_lesson.topic}. "
                    f"Learning Objective: {target_lesson.learning_objective}. "
                    f"Summary: {target_lesson.concept_summary}."
                )
                for res in target_lesson.resources[:2]:
                    citations.append({
                        "title": res.get("title", "Official Documentation"),
                        "url": res.get("canonical_url", ""),
                        "source": res.get("source", "Technical Documentation"),
                    })
        except Exception as exc:
            logger.warning("Error building skill context for chat: %s", exc)
            context_summary = f"Skill: {target_id}."

    # Mode B: Repository Understanding Context
    elif mode == "project":
        try:
            # Resolve repository
            repo_record = None
            if req.repository_id:
                repo_record = db.query(GitHubRepository).filter(GitHubRepository.id == req.repository_id).first()
            if not repo_record and target_id.isdigit():
                repo_record = db.query(GitHubRepository).filter(GitHubRepository.id == int(target_id)).first()
            if not repo_record:
                gh_prof = db.query(GitHubProfile).filter(GitHubProfile.user_id == current_user.id).first()
                if gh_prof:
                    repo_record = (
                        db.query(GitHubRepository)
                        .filter(
                            GitHubRepository.github_profile_id == gh_prof.id,
                            GitHubRepository.name.ilike(f"%{target_id}%"),
                        )
                        .first()
                    )

            # Resolve active file
            active_path = req.file_path or (target_id if ("/" in target_id or "." in target_id) else None)

            if repo_record and active_path:
                file_rec = (
                    db.query(GitHubRepositoryFile)
                    .filter(
                        GitHubRepositoryFile.github_repository_id == repo_record.id,
                        GitHubRepositoryFile.file_path == active_path,
                    )
                    .first()
                )

                if not code_ws:
                    if file_rec and file_rec.content:
                        code_ws = file_rec.content
                    elif file_rec and current_user:
                        try:
                            from app.services.github_service import fetch_repository_file_content
                            refreshed = fetch_repository_file_content(db, file_rec.id, current_user)
                            if refreshed and getattr(refreshed, "content", None):
                                code_ws = refreshed.content
                        except Exception:
                            pass

                companion_files = find_related_implementation_files(db, repo_record.id, active_path, current_user)
                current_lesson_title = f"{os.path.basename(active_path)} in {repo_record.name}"

                citations.append({
                    "file_path": active_path,
                    "description": f"Active inspecting file in {repo_record.name}",
                    "verified": True,
                })

                companion_summary = ""
                if companion_files and companion_files[0].get("content"):
                    comp = companion_files[0]
                    citations.append({
                        "file_path": comp["file_path"],
                        "description": f"Verified companion source code ({comp['file_name']})",
                        "verified": True,
                    })
                    comp_analysis = extract_code_structure_and_loops(comp["content"])
                    companion_summary = (
                        f"\nVerified Companion Source Implementation: `{comp['file_path']}`.\n"
                        f"Code Loop/Condition Analysis: {comp_analysis['summary']}.\n"
                    )
                    if comp_analysis.get("small_input_walkthrough"):
                        companion_summary += f"{comp_analysis['small_input_walkthrough']}\n"
                    if comp_analysis.get("derived_output"):
                        companion_summary += f"Expected Output:\n```\n{comp_analysis['derived_output']}\n```\n"
                    companion_summary += f"Companion Source Snippet:\n```\n{comp['content'][:1500]}\n```\n"
                elif active_path.lower().endswith((".md", ".markdown")):
                    dir_part = os.path.dirname(active_path)
                    companion_summary = (
                        f"\nVerified Finding: No companion source code implementation file was located in '{dir_part or '.'}'. "
                        f"Do NOT invent companion source files or code functions. Explain the specification from {active_path} only."
                    )

                active_analysis = extract_code_structure_and_loops(code_ws) if code_ws else None

                context_summary = (
                    f"Selected File: {active_path} ({os.path.basename(active_path)})\n"
                    f"Repository: {repo_record.name} ({repo_record.full_name or repo_record.name})\n"
                    f"Active File Content:\n```\n{code_ws[:2000] if code_ws else 'No content retrieved'}\n```\n"
                    f"{companion_summary}"
                )
                if active_analysis and active_analysis.get("has_loops"):
                    context_summary += f"\nActive File Loop Analysis: {active_analysis['summary']}\n"

            elif repo_record:
                repo_model = build_repository_understanding(db, repo_record.id, current_user)
                current_lesson_title = f"{repo_model.repository_name} Architecture"
                context_summary = (
                    f"Repository: {repo_model.repository_name} ({repo_model.full_name}). "
                    f"Tech Stack: {', '.join(repo_model.main_technologies)}. "
                    f"Purpose: {repo_model.project_purpose}. "
                    f"Request Flow: {repo_model.request_flow}. "
                    f"Database Flow: {repo_model.database_flow}. "
                    f"Auth/Security: {repo_model.auth_security_flow}. "
                    f"Entry Points: {', '.join(repo_model.application_entry_points)}. "
                )
                for cit in repo_model.source_evidence_citations[:4]:
                    citations.append({
                        "file_path": cit.get("file_path", "README.md"),
                        "description": cit.get("description", "Repository source file"),
                        "verified": True,
                    })
            else:
                context_summary = f"Project: {target_id}."
        except Exception as exc:
            logger.warning("Error building repo context for chat: %s", exc)
            context_summary = f"Project: {target_id}."

    # Fallback to general DSA / Curriculum
    else:
        context_summary = f"Topic: {target_id}."

    # Multilingual clause
    multilingual_clause = ""
    if lang_code != "en":
        multilingual_clause = (
            f"\n\nCRITICAL MULTILINGUAL PEDAGOGY DIRECTIVE:\n"
            f"You MUST deliver your entire explanation and follow-up guidance in fluent, natural {target_lang}.\n"
            f"Keep code syntax, variable names, and code snippets in standard English programming format, "
            f"but explain the reasoning, concepts, and analogies in {target_lang}.\n"
        )

    # Build Socratic System Prompt
    assessment_prompt_part = ""
    if is_assessment:
        assessment_prompt_part = (
            "THE LEARNER HAS SUBMITTED AN ASSESSMENT ATTEMPT FOR EVALUATION.\n"
            f"Skill being assessed: {target_id}.\n"
            f"Lesson/topic: {current_lesson_title}.\n"
            "Evaluate their understanding rigorously:\n"
            "1) Praise what they got right.\n"
            "2) Explain what was wrong, sub-optimal, or missing.\n"
            "3) Deliver the core masterclass takeaway.\n"
            "4) Provide the optimal code snippet if applicable.\n"
            "5) Assign a score out of 100.\n"
            "Format the response clearly with labeled sections:\n"
            "✅ What You Got Right\n⚠️ What Was Sub-Optimal\n🎓 Masterclass Takeaway\n💻 Optimal Solution\n📊 Score: [0-100]\n"
            "IMPORTANT: The learner's actual submitted answer is included in the user message below. "
            "Your feedback MUST address what they specifically wrote, not a generic answer."
        )
    else:
        assessment_prompt_part = (
            "THE LEARNER IS IN ORDINARY TUTORING / EXPLORATION MODE.\n"
            "DO NOT grade or mark their message as wrong. DO NOT assign numerical scores.\n"
            "Answer their question directly with warmth, clarity, intuitive analogies, and step-by-step code walkthroughs.\n"
            "If they ask to explain simply, use an everyday metaphor.\n"
            "If they ask about their project, connect the concept directly to their repository files.\n"
            "End with 2 concise suggested follow-up questions to deepen their understanding."
        )

    system_prompt = (
        "You are Dr. Cyra Vance, Master AI Technical Educator & Lead Tech Mentor at CareerVerse AI. "
        "You are a warm, brilliant, world-class software engineering mentor. "
        "Your mission is to guide the candidate to deep conceptual understanding and technical interview mastery. "
        f"Candidate Target Role: {getattr(current_user, 'target_role', 'Software Engineer')}. "
        f"Session Mode: {mode.upper()}. "
        f"Context & Grounding:\n{context_summary}\n"
        f"{connected_projects_info}\n\n"
        "CRITICAL ANTI-HALLUCINATION & RELEVANCE DIRECTIVE:\n"
        "- Ground your explanations strictly in the verified repository evidence above.\n"
        "- DO NOT invent or mention Gang of Four design patterns (such as Singleton, Factory Method, Adapter, Bridge, Strategy) "
        "unless they are genuinely present in the code evidence.\n"
        "- If teaching a specific pattern problem (such as Hollow Square, star pattern, matrix problem), explain the actual loops, invariants, conditions, variables, and small sample inputs (e.g. n=3).\n"
        "- If companion implementation code was found, reference its actual lines and statements. If not, state that only the documentation is present and do not fabricate implementation code.\n\n"
        f"{assessment_prompt_part}\n"
        f"{multilingual_clause}"
    )

    history_lines = []
    if req.chat_history:
        for turn in req.chat_history[-6:]:
            role_label = "Learner" if turn.role == "user" else "Dr. Cyra Vance"
            history_lines.append(f"{role_label}: {turn.content}")

    user_payload = ""
    if history_lines:
        user_payload += "Previous Conversation Turns:\n" + "\n".join(history_lines) + "\n\n"
    user_payload += f"Learner's Question or Response:\n{user_msg}\n"
    if code_ws:
        user_payload += f"\nLearner's Workspace Code:\n```{code_ws}```\n"

    cyra_reply = ""
    demonstrated_understanding = False
    assessment_eval = None
    suggested_follow_ups: List[str] = [
        "Explain this concept with an intuitive real-world analogy.",
        "How is this pattern used in high-scale production systems?",
        "Test my understanding with an interview scenario question.",
    ]

    provider_succeeded = False
    try:
        provider = get_model_provider()
        res = provider.generate_text(
            system_prompt=system_prompt,
            user_message=user_payload,
            temperature=0.3,
            max_completion_tokens=1000,
        )
        if res and res.content and res.content.strip():
            cyra_reply = res.content.strip()
            provider_succeeded = True
    except Exception as exc:
        logger.warning("Error generating Cyra chat response: %s", exc)

    if not cyra_reply:
        if is_assessment:
            # Provider failed in assessment mode — do NOT award mastery
            cyra_reply = (
                "I couldn't evaluate your answer because the AI service is unavailable — please retry."
            )
            demonstrated_understanding = False
            limitations_note = "AI provider unavailable; assessment could not be evaluated."
        else:
            msg_lower = user_msg.lower()
            if "simply" in msg_lower or "eli5" in msg_lower or "simple" in msg_lower:
                cyra_reply = (
                    f"Let's break down **{current_lesson_title}** into plain terms.\n\n"
                    f"Imagine you are organizing a shared team workspace. Instead of every person re-verifying information from scratch, "
                    f"you establish a single source of truth that guarantees consistent inputs and predictable outputs. "
                    f"In **{target_id}**, this concept does exactly that: it abstracts complexity into modular, reusable components so you don't repeat boilerplate."
                )
            elif "different example" in msg_lower or "another example" in msg_lower:
                cyra_reply = (
                    f"Here is an alternative practical example for **{current_lesson_title}** in **{target_id}**:\n\n"
                    f"```python\n# Alternative implementation pattern for {current_lesson_title}\n"
                    f"# Demonstrates clean separation of concerns and robust error handling\n"
                    f"def execute_pipeline(payload: dict) -> dict:\n"
                    f"    if not payload:\n"
                    f"        raise ValueError('Payload cannot be empty')\n"
                    f"    return {{'status': 'success', 'topic': '{current_lesson_title}', 'data': payload}}\n```\n\n"
                    f"Notice how this decouples the configuration from the actual execution logic."
                )
            elif "hint" in msg_lower:
                cyra_reply = (
                    f"💡 **Mentor Hint for {current_lesson_title}**:\n\n"
                    f"Think about the data transformation pipeline. What is the exact state right before the operation runs? "
                    f"Check whether the required inputs or schemas match the expected structure before invoking the logic."
                )
            elif "why my answer is incorrect" in msg_lower or "incorrect" in msg_lower:
                cyra_reply = (
                    f"Let's examine why that approach might be sub-optimal in **{current_lesson_title}**:\n\n"
                    f"1. **Input Preconditions**: Verify if edge cases or unvalidated types cause unexpected runtime failures.\n"
                    f"2. **State Management**: Ensure you are not mutating shared references or bypassing framework lifecycle contracts.\n"
                    f"3. **Return Expectations**: Compare your output structure against the required schema."
                )
            elif "practical challenge" in msg_lower or "challenge" in msg_lower:
                cyra_reply = (
                    f"🎯 **Hands-On Challenge for {current_lesson_title}**:\n\n"
                    f"Build a lightweight utility function that accepts an input configuration, validates the input parameters, "
                    f"and returns a structured result without throwing unhandled exceptions. "
                    f"Write your solution in the code workspace and let me know when you're ready to review!"
                )
            elif "project" in msg_lower or "connect" in msg_lower:
                if connected_projects_info:
                    cyra_reply = (
                        f"Connecting **{current_lesson_title}** to your project:\n\n"
                        f"{connected_projects_info}\n\n"
                        f"In your repository, applying this pattern allows you to separate configuration parameters from execution logic, "
                        f"ensuring your application handles scaling gracefully without tight coupling."
                    )
                else:
                    cyra_reply = (
                        f"Connecting **{current_lesson_title}** to practical project work:\n\n"
                        f"In real-world applications using **{target_id}**, this pattern is deployed in the core business logic layer. "
                        f"It keeps your controllers/handlers thin and moves orchestration into dedicated, unit-testable modules."
                    )
            else:
                cyra_reply = (
                    f"I'm delighted you asked about that in **{current_lesson_title}**!\n\n"
                    f"Here is the core mental model: In **{target_id}**, {current_lesson_title} ensures that operations maintain predictable invariants. "
                    f"Instead of handling state transitions ad-hoc, we rely on established architectural contracts.\n\n"
                    f"Would you like me to walk through a concrete step-by-step code example, or explore how this connects to your projects?"
                )

    # Process assessment score if present — only when provider actually succeeded
    if is_assessment and provider_succeeded:
        score_match = re.search(r"score[:\s]+(\d+)", cyra_reply, re.IGNORECASE)
        if score_match:
            score_val = int(score_match.group(1))
            demonstrated_understanding = score_val >= 80
            assessment_eval = {
                "score": score_val,
                "demonstrated": demonstrated_understanding,
                "evaluated_at": datetime.utcnow().isoformat(),
            }
        else:
            # Provider replied but no explicit numeric score — conservative: do not award mastery
            demonstrated_understanding = False

    # Extract follow-ups if present in text
    fu_matches = re.findall(r"(?:•|\d\.)\s+([^\n\?]+\?)", cyra_reply)
    if fu_matches:
        suggested_follow_ups = [m.strip() for m in fu_matches[:3]]

    # ── PERSIST IN POSTGRESQL (TeachingProgress) ──────────────────────────────
    try:
        progress = (
            db.query(TeachingProgress)
            .filter(
                TeachingProgress.candidate_id == current_user.id,
                TeachingProgress.section_id == mode,
                TeachingProgress.lesson_id == lesson_id,
            )
            .first()
        )
        if not progress:
            progress = TeachingProgress(
                candidate_id=current_user.id,
                section_id=mode,
                lesson_id=lesson_id,
                status="in_progress",
                turns=[],
                hints_used=0,
                current_stage="explanation" if not is_assessment else "completed",
            )
            db.add(progress)
            db.flush()

        current_turns = list(progress.turns or [])
        current_turns.append({
            "role": "user",
            "content": user_msg,
            "code": code_ws or None,
            "is_assessment": is_assessment,
            "timestamp": datetime.utcnow().isoformat(),
        })
        current_turns.append({
            "role": "cyra",
            "content": cyra_reply,
            "citations": citations,
            "is_assessment": is_assessment,
            "demonstrated_understanding": demonstrated_understanding,
            "timestamp": datetime.utcnow().isoformat(),
        })
        progress.turns = current_turns

        if demonstrated_understanding:
            progress.status = "mastered"
            progress.current_stage = "completed"
            if assessment_eval:
                progress.assessment_score = assessment_eval["score"]
                progress.mastery_evidence = assessment_eval

        db.commit()
    except Exception as exc:
        logger.warning("Could not persist teaching chat turn in PostgreSQL: %s", exc)
        db.rollback()

    return TeachingChatResponse(
        reply=cyra_reply,
        teaching_mode=mode,
        target_id=target_id,
        lesson_id=lesson_id,
        current_stage="completed" if demonstrated_understanding else "explanation",
        citations=citations,
        suggested_follow_ups=suggested_follow_ups,
        is_assessment=is_assessment,
        assessment_evaluation=assessment_eval,
        demonstrated_understanding=demonstrated_understanding,
        recommended_next_action="Continue to next lesson" if demonstrated_understanding else "Ask Dr. Cyra a follow-up question",
        file_path=active_path,
        companion_files=companion_files,
        limitations=limitations_note if not provider_succeeded and is_assessment else limitations_note,
    )


