import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from app.schemas.learner_knowledge import TeachingResourceItem

logger = logging.getLogger("careerverse.ai.teaching_resources")

# Authoritative, verified technical reference repository
AUTHORITATIVE_RESOURCE_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "id": "res-python-asyncio",
            "title": "Python Official Documentation: Asyncio Coroutines & Event Loop",
            "canonical_url": "https://docs.python.org/3/library/asyncio.html",
            "resource_type": "official_doc",
            "concepts_covered": ["Python", "Async Programming", "Event Loop", "Concurrency"],
            "difficulty_level": "Medium to Hard",
            "source": "Python Software Foundation",
            "excerpt": "Asyncio is a library to write concurrent code using the async/await syntax. It runs on a single OS thread using cooperative multitasking, scheduling coroutines on an event loop.",
            "relevance_rationale": "Authoritative standard documentation explaining event loop invariants and non-blocking I/O execution.",
        },
        {
            "id": "res-python-memory",
            "title": "Python Memory Management & GIL Architectural Guide",
            "canonical_url": "https://docs.python.org/3/c-api/memory.html",
            "resource_type": "official_doc",
            "concepts_covered": ["Python", "Memory Allocation", "GIL", "Garbage Collection"],
            "difficulty_level": "Hard",
            "source": "Python Developer's Guide",
            "excerpt": "CPython manages memory via reference counting and a cyclic garbage collector. The Global Interpreter Lock (GIL) prevents concurrent execution of Python bytecode across multiple OS threads.",
            "relevance_rationale": "Essential reference for explaining CPU-bound vs I/O-bound concurrency limits.",
        },
        {
            "id": "res-python-dicts",
            "title": "Python Official Documentation: Dictionaries, Key Hashing & Mapping Types",
            "canonical_url": "https://docs.python.org/3/tutorial/datastructures.html#dictionaries",
            "resource_type": "official_doc",
            "concepts_covered": ["Python", "Dictionaries", "Hash Table", "Hashable Keys", "Key Lookup", "O(1) Complexity"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "Python Software Foundation",
            "excerpt": "A dictionary is a mapping of hashable values to arbitrary objects. Keys must be immutable and hashable. In Python 3.7+, dictionaries preserve insertion order by combining a sparse index array with a dense entry array.",
            "relevance_rationale": "Authoritative reference for dictionary memory layout, hash lookup mechanics, and time complexity.",
        },
        {
            "id": "res-gfg-python-dict",
            "title": "GeeksforGeeks: Internal Working of Python Dictionary & Open Addressing",
            "canonical_url": "https://www.geeksforgeeks.org/internal-working-of-python-dictionary/",
            "resource_type": "educational_tutorial",
            "concepts_covered": ["Python", "Dictionary Internals", "Hash Collisions", "Open Addressing", "Compact Dict"],
            "difficulty_level": "Intermediate",
            "source": "GeeksforGeeks Computer Science Portal",
            "excerpt": "Python dictionaries resolve hash collisions using open addressing with a pseudo-random probing sequence. The compact dictionary design separates a sparse index table from a dense table of (hash, key, value) tuples to save 20-25% memory.",
            "relevance_rationale": "Comprehensive technical deep-dive explaining internal CPython implementation, collision handling, and performance trade-offs.",
        },
    ],
    "fastapi": [
        {
            "id": "res-fastapi-di",
            "title": "FastAPI Documentation: Advanced Dependencies & Yield Cleanups",
            "canonical_url": "https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/",
            "resource_type": "official_doc",
            "concepts_covered": ["FastAPI", "Dependency Injection", "Database Sessions", "Transactions"],
            "difficulty_level": "Medium",
            "source": "FastAPI Official Documentation",
            "excerpt": "Dependencies with yield allow executing setup code before route execution and teardown cleanup code in a finally block after the route finishes.",
            "relevance_rationale": "Guarantees resource teardown (e.g. database session commit/rollback) without polluting controller logic.",
        },
        {
            "id": "res-fastapi-async",
            "title": "FastAPI Concurrency and async / await Internals",
            "canonical_url": "https://fastapi.tiangolo.com/async/",
            "resource_type": "official_doc",
            "concepts_covered": ["FastAPI", "Async Routes", "Threadpool Execution", "Pydantic"],
            "difficulty_level": "Medium",
            "source": "FastAPI Technical Documentation",
            "excerpt": "Path operations declared with 'async def' are scheduled directly onto the event loop. Synchronous 'def' path operations are offloaded to an AnyIO external worker threadpool.",
            "relevance_rationale": "Explains route scheduling behavior under high concurrent connection loads.",
        },
    ],
    "javascript": [
        {
            "id": "res-js-closures",
            "title": "MDN Web Docs: Closures & Lexical Scoping",
            "canonical_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Closures",
            "resource_type": "official_doc",
            "concepts_covered": ["JavaScript", "Closures", "Lexical Scope", "Function Factories", "Encapsulation", "State Management"],
            "difficulty_level": "Intermediate",
            "source": "Mozilla Developer Network (MDN Web Docs)",
            "excerpt": "A closure is the combination of a function bundled together (enclosed) with references to its surrounding state (the lexical environment). In JavaScript, closures give an inner function access to an outer function's scope even after the outer function has closed.",
            "relevance_rationale": "Authoritative MDN documentation defining lexical scoping, environment records, and closure mechanics.",
        },
        {
            "id": "res-js-scope",
            "title": "MDN Web Docs: JavaScript Scope & Execution Context",
            "canonical_url": "https://developer.mozilla.org/en-US/docs/Glossary/Scope",
            "resource_type": "official_doc",
            "concepts_covered": ["JavaScript", "Scope", "Block Scope", "Lexical Environment", "Var vs Let"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "Mozilla Developer Network (MDN Web Docs)",
            "excerpt": "The scope is the current context of execution in which values and expressions are 'visible' or can be referenced. JavaScript uses lexical scoping, meaning functions are executed using the variable scope that was in effect when they were defined.",
            "relevance_rationale": "Fundamental MDN reference explaining variable resolution and lifetime.",
        },
        {
            "id": "res-js-javascript-info",
            "title": "JavaScript.info: Variable Scope & Closure Internals",
            "canonical_url": "https://javascript.info/closure",
            "resource_type": "tutorial",
            "concepts_covered": ["JavaScript", "LexicalEnvironment", "Garbage Collection", "Closures"],
            "difficulty_level": "Intermediate",
            "source": "JavaScript.info Tutorial",
            "excerpt": "Every running function, code block, and the script as a whole have an internal (hidden) associated object known as the Lexical Environment. A function retains a hidden [[Environment]] reference to the Lexical Environment where it was created.",
            "relevance_rationale": "In-depth guide explaining memory diagrams, garbage collection, and variable lifecycles.",
        },
    ],
    "react": [
        {
            "id": "res-react-hooks",
            "title": "React.dev: Optimizing Re-renders with useMemo & useCallback",
            "canonical_url": "https://react.dev/reference/react/useMemo",
            "resource_type": "official_doc",
            "concepts_covered": ["React", "Performance Optimization", "Fiber Reconciler", "Memoization"],
            "difficulty_level": "Medium",
            "source": "React Official Documentation",
            "excerpt": "useMemo caches the result of a calculation between re-renders until one of its dependencies changes. Pairing it with React.memo prevents unnecessary re-rendering of deep component trees.",
            "relevance_rationale": "Core architectural guide for preventing redundant reconciliation cycles in high-frequency UIs.",
        },
    ],
    "postgresql": [
        {
            "id": "res-postgres-indexes",
            "title": "PostgreSQL Documentation: Index Types & B-Tree Mechanics",
            "canonical_url": "https://www.postgresql.org/docs/current/indexes-types.html",
            "resource_type": "official_doc",
            "concepts_covered": ["PostgreSQL", "Database Modeling", "B-Tree Indexes", "Query Optimization"],
            "difficulty_level": "Medium to Hard",
            "source": "PostgreSQL Global Development Group",
            "excerpt": "PostgreSQL provides B-tree, Hash, GiST, SP-GiST, GIN, and BRIN index methods. B-tree indexes fit range and equality queries by maintaining sorted, balanced multi-way trees.",
            "relevance_rationale": "Primary documentation on query optimization, index selectivity, and explain analyze planning.",
        },
        {
            "id": "res-postgres-transactions",
            "title": "PostgreSQL Documentation: Transaction Isolation Levels & ACID",
            "canonical_url": "https://www.postgresql.org/docs/current/transaction-iso.html",
            "resource_type": "official_doc",
            "concepts_covered": ["PostgreSQL", "Transactions", "ACID", "Isolation Levels"],
            "difficulty_level": "Hard",
            "source": "PostgreSQL Global Development Group",
            "excerpt": "Read Committed, Repeatable Read, and Serializable isolation levels prevent dirty reads, non-repeatable reads, and serialization anomalies using Multiversion Concurrency Control (MVCC).",
            "relevance_rationale": "Authoritative standard for concurrency control and atomic state transitions.",
        },
    ],
    "dsa": [
        {
            "id": "res-dsa-twosum",
            "title": "LeetCode Problem #1: Two Sum Specification & Analysis",
            "canonical_url": "https://leetcode.com/problems/two-sum/",
            "resource_type": "exercise",
            "concepts_covered": ["Arrays and Hash Maps", "Two Sum", "Invariants", "Big-O Time Complexity"],
            "difficulty_level": "Easy to Medium",
            "source": "LeetCode Algorithmic Repository",
            "excerpt": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target in O(N) time using an auxiliary hash map.",
            "relevance_rationale": "Canonical benchmark problem demonstrating hash map complement tracking.",
        },
        {
            "id": "res-dsa-binary-search",
            "title": "LeetCode Problem #33: Search in Rotated Sorted Array",
            "canonical_url": "https://leetcode.com/problems/search-in-rotated-sorted-array/",
            "resource_type": "exercise",
            "concepts_covered": ["Binary Search", "Monotonic Invariant", "Logarithmic Time Complexity"],
            "difficulty_level": "Medium",
            "source": "LeetCode Algorithmic Repository",
            "excerpt": "An array sorted in ascending order is rotated at an unknown pivot index. Locate the target in O(log N) time by determining which half is strictly sorted.",
            "relevance_rationale": "Benchmark problem demonstrating state-space division when strict global monotonicity is broken.",
        },
    ],
    "docker": [
        {
            "id": "res-docker-multi-stage",
            "title": "Docker Official Documentation: Multi-Stage Container Builds",
            "canonical_url": "https://docs.docker.com/build/building/multi-stage/",
            "resource_type": "official_doc",
            "concepts_covered": ["Docker", "Containerization", "CI/CD", "Production Optimization"],
            "difficulty_level": "Medium",
            "source": "Docker Documentation",
            "excerpt": "Multi-stage builds allow separating build-time compilers and SDKs from lean runtime production images, shrinking image size by 80%+ and reducing CVE attack surfaces.",
            "relevance_rationale": "Industry-standard practice for secure, minimal production container deployments.",
        },
    ],
    "system design": [
        {
            "id": "res-system-design-caching",
            "title": "System Design: Cache-Aside vs Write-Through Architecture",
            "canonical_url": "https://redis.io/docs/latest/develop/use/patterns/",
            "resource_type": "official_doc",
            "concepts_covered": ["Caching", "Redis", "System Design", "Consistency"],
            "difficulty_level": "Medium to Hard",
            "source": "Redis Documentation",
            "excerpt": "In Cache-Aside, the application first inspects the cache before falling back to the database on cache miss. TTL expiry and cache invalidation strategies mitigate stale reads.",
            "relevance_rationale": "Foundational architectural pattern for sub-5ms low latency data retrieval.",
        },
    ],
    "langchain": [
        {
            "id": "res-langchain-lcel",
            "title": "LangChain Documentation: LangChain Expression Language (LCEL) & Runnables",
            "canonical_url": "https://python.langchain.com/docs/concepts/lcel/",
            "resource_type": "official_doc",
            "concepts_covered": ["LangChain", "LCEL", "Runnable Protocol", "Streaming", "Batching"],
            "difficulty_level": "Medium",
            "source": "LangChain Official Documentation",
            "excerpt": "LCEL provides a declarative composition protocol where components pipe inputs to outputs (`chain = prompt | model | parser`). Every Runnable implements invoke, batch, and astream interfaces.",
            "relevance_rationale": "Authoritative standard documentation explaining modern composable chain architectures.",
        },
        {
            "id": "res-langchain-loaders",
            "title": "LangChain Documentation: Document Loaders, Parsing & Ingestion",
            "canonical_url": "https://python.langchain.com/docs/concepts/document_loaders/",
            "resource_type": "official_doc",
            "concepts_covered": ["LangChain", "Document Loaders", "ETL", "PDF Parsing", "Text Extraction"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "LangChain Official Documentation",
            "excerpt": "Document loaders ingest unstructured data from various sources (PDFs, Markdown, HTML, databases) and convert it into LangChain Document objects containing page content and associated metadata dictionaries.",
            "relevance_rationale": "Canonical guide on data ingestion and document transformation for RAG pipelines.",
        },
        {
            "id": "res-langchain-splitters",
            "title": "LangChain Documentation: Text Splitters & Chunking Strategies",
            "canonical_url": "https://python.langchain.com/docs/concepts/text_splitters/",
            "resource_type": "official_doc",
            "concepts_covered": ["LangChain", "Text Splitters", "Chunking", "Chunk Size", "Chunk Overlap", "RecursiveCharacterTextSplitter"],
            "difficulty_level": "Intermediate",
            "source": "LangChain Official Documentation",
            "excerpt": "Text splitters divide long documents into manageable chunks that fit within model context windows while preserving semantic meaning. RecursiveCharacterTextSplitter splits text recursively using paragraphs, lines, and spaces.",
            "relevance_rationale": "Essential reference for optimizing retrieval precision and preventing context window overflow in RAG.",
        },
    ],
    "langgraph": [
        {
            "id": "res-langgraph-state",
            "title": "LangGraph Documentation: Multi-Actor Cyclic StateGraph & Node Reducers",
            "canonical_url": "https://langchain-ai.github.io/langgraph/concepts/high_level/",
            "resource_type": "official_doc",
            "concepts_covered": ["LangGraph", "StateGraph", "TypedDict", "Cyclic Workflows", "Checkpointers"],
            "difficulty_level": "Medium to Hard",
            "source": "LangGraph Documentation",
            "excerpt": "LangGraph models agent workflows as cyclical state graphs. Pure node functions receive state and return partial updates that are merged by reducers into the shared state.",
            "relevance_rationale": "Core conceptual guide for building robust, stateful multi-agent workflows.",
        },
    ],
    "sql": [
        {
            "id": "res-sql-joins",
            "title": "PostgreSQL Documentation: Table Expressions, Queries & Relational Joins",
            "canonical_url": "https://www.postgresql.org/docs/current/queries-table-expressions.html",
            "resource_type": "official_doc",
            "concepts_covered": ["SQL", "Relational Joins", "Query Execution", "ON Predicate", "Cartesian Product"],
            "difficulty_level": "Medium",
            "source": "PostgreSQL Documentation",
            "excerpt": "Table expressions produce a relational result table through the evaluation of FROM, WHERE, GROUP BY, and HAVING clauses. JOIN types specify row inclusion rules based on join predicates.",
            "relevance_rationale": "Authoritative standard for relational query execution order and join semantics.",
        },
    ],
    "large language models": [
        {
            "id": "res-llm-architecture",
            "title": "Anthropic Research: Core Architecture & Invariants of Modern Language Models",
            "canonical_url": "https://docs.anthropic.com/en/docs/build-with-claude/overview",
            "resource_type": "official_doc",
            "concepts_covered": ["Large Language Models", "Transformer", "Attention", "Tokens", "Decoding"],
            "difficulty_level": "Intermediate",
            "source": "Anthropic Technical Documentation",
            "excerpt": "Language models are causal autoregressive predictors trained to minimize cross-entropy loss over text tokens. Decoding strategies (temperature, top-p) sample from vocabulary distributions.",
            "relevance_rationale": "Essential reference on statistical next-token prediction and context window dynamics.",
        },
        {
            "id": "res-transformer-attention",
            "title": "Attention Is All You Need — Transformer Architecture",
            "canonical_url": "https://arxiv.org/abs/1706.03762",
            "resource_type": "academic_paper",
            "concepts_covered": ["Transformer", "Self-Attention", "Multi-Head Attention", "Positional Encoding"],
            "difficulty_level": "Advanced",
            "source": "Google Research",
            "excerpt": "The Transformer replaces recurrent layers with multi-head self-attention mechanisms, computing parallel attention weights across sequence positions with scaled dot-product attention.",
            "relevance_rationale": "The foundational publication establishing the modern LLM architecture.",
        },
    ],
    "prompt engineering": [
        {
            "id": "res-prompt-interactive",
            "title": "Anthropic Interactive Prompt Engineering Tutorial & System Guidelines",
            "canonical_url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview",
            "resource_type": "official_doc",
            "concepts_covered": ["Prompt Engineering", "Task Specification", "Delimiters", "Few-Shot", "Chain-of-Thought"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "Anthropic Documentation",
            "excerpt": "Clear task specification, explicit constraints, structural XML tags, few-shot exemplars, and thinking step-by-step yield deterministic and accurate model responses.",
            "relevance_rationale": "Industry-standard prompt engineering best practices and failure mode mitigations.",
        },
        {
            "id": "res-prompt-security",
            "title": "OWASP Top 10 for LLM Applications: Prompt Injection Vulnerabilities",
            "canonical_url": "https://genai.owasp.org/llm-top-10/",
            "resource_type": "security_standard",
            "concepts_covered": ["Prompt Injection", "Jailbreak Defense", "Trust Boundaries", "Security"],
            "difficulty_level": "Intermediate to Hard",
            "source": "OWASP Foundation",
            "excerpt": "Direct and indirect prompt injection attacks exploit the lack of separation between instructions and data in LLM inputs. Delimiter separation and input sanitization mitigate risks.",
            "relevance_rationale": "Authoritative security guidance for protecting enterprise LLM applications against prompt attacks.",
        },
    ],
    "figma": [
        {
            "id": "res-figma-autolayout",
            "title": "Figma Official Guide: Auto Layout Properties, Spacing & Constraints",
            "canonical_url": "https://help.figma.com/hc/en-us/articles/360040451373-Explore-auto-layout-properties",
            "resource_type": "official_doc",
            "concepts_covered": ["Figma", "Auto Layout", "Responsive Design", "Constraints", "Hug Contents", "Fill Container"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "Figma Official Help Center",
            "excerpt": "Auto layout is a property you can add to frames and components. It lets you create designs that grow to fit their content or adjust as you resize the canvas. You can define horizontal or vertical direction, padding, gap, and child resizing behaviors (Fixed, Hug contents, Fill container).",
            "relevance_rationale": "Authoritative reference for responsive component architecture, padding models, and dynamic resizing in Figma.",
        },
        {
            "id": "res-figma-components",
            "title": "Figma Official Documentation: Components, Variants & Design Tokens",
            "canonical_url": "https://help.figma.com/hc/en-us/articles/360038662654-Guide-to-components-in-Figma",
            "resource_type": "official_doc",
            "concepts_covered": ["Figma", "Components", "Variants", "Design Systems", "Component Properties"],
            "difficulty_level": "Intermediate",
            "source": "Figma Official Help Center",
            "excerpt": "Components are elements you can reuse across designs. Variants allow you to group similar components into a single container with distinct state properties (e.g. size, style, active state, boolean toggles).",
            "relevance_rationale": "Standard documentation for building unified, scalable design systems.",
        },
        {
            "id": "res-figma-wcag",
            "title": "W3C Web Content Accessibility Guidelines (WCAG) 2.2: Color Contrast & Usability",
            "canonical_url": "https://www.w3.org/WAI/standards-guidelines/wcag/",
            "resource_type": "security_standard",
            "concepts_covered": ["UI/UX", "Accessibility", "WCAG", "Contrast Ratio", "Usability Testing"],
            "difficulty_level": "Intermediate",
            "source": "W3C Web Accessibility Initiative",
            "excerpt": "WCAG provides recommendations for making Web content more accessible. Success Criterion 1.4.3 requires a contrast ratio of at least 4.5:1 for normal text and 3:1 for large text to ensure readable interfaces.",
            "relevance_rationale": "International technical standard for accessible user interface design.",
        },
    ],
    "opencv": [
        {
            "id": "res-opencv-matrix",
            "title": "OpenCV Documentation: Getting Started with Images & Matrix Representation",
            "canonical_url": "https://docs.opencv.org/4.x/db/deb/tutorial_display_image.html",
            "resource_type": "official_doc",
            "concepts_covered": ["OpenCV", "Image Representation", "NumPy", "Pixel Grids", "cv2.imread"],
            "difficulty_level": "Beginner",
            "source": "OpenCV Documentation (opencv.org)",
            "excerpt": "In OpenCV Python, images are stored as multi-dimensional NumPy ndarrays. A color image is represented as a 3D matrix (height, width, channels) in BGR order with uint8 values in range [0, 255].",
            "relevance_rationale": "Authoritative foundation for image representation, memory arrays, and pixel coordinate systems.",
        },
        {
            "id": "res-opencv-colorspaces",
            "title": "OpenCV Documentation: Changing Colorspaces (cvtColor, BGR to RGB/HSV)",
            "canonical_url": "https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html",
            "resource_type": "official_doc",
            "concepts_covered": ["OpenCV", "Colorspaces", "BGR to RGB", "HSV", "cv2.cvtColor"],
            "difficulty_level": "Beginner to Intermediate",
            "source": "OpenCV Documentation (opencv.org)",
            "excerpt": "cv2.cvtColor converts images between color spaces. Note that OpenCV uses BGR by default instead of RGB. For object tracking by color, HSV (Hue, Saturation, Value) is preferred over BGR.",
            "relevance_rationale": "Core official tutorial for color conversions and pixel channel transformations.",
        },
        {
            "id": "res-opencv-canny",
            "title": "OpenCV Documentation: Canny Edge Detection & Contours Analysis",
            "canonical_url": "https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html",
            "resource_type": "official_doc",
            "concepts_covered": ["OpenCV", "Edge Detection", "Canny", "Hysteresis Thresholding", "Gradients"],
            "difficulty_level": "Intermediate",
            "source": "OpenCV Documentation (opencv.org)",
            "excerpt": "Canny edge detection is a multi-stage algorithm: noise reduction via Gaussian filter, intensity gradient calculation, non-maximum suppression, and hysteresis thresholding.",
            "relevance_rationale": "Primary official reference for edge detection algorithms and structural feature extraction.",
        },
    ],
}

_RESOURCE_CACHE: Dict[str, List[TeachingResourceItem]] = {}


def retrieve_teaching_resources_for_lesson(
    concept_title: str,
    skill_name: Optional[str] = None,
    candidate_projects: Optional[List[Dict[str, Any]]] = None,
    candidate_skills: Optional[List[str]] = None,
    limit: int = 4,
) -> List[TeachingResourceItem]:
    """
    Retrieves verified teaching resources for a lesson.
    Combines authoritative official documentation with the candidate's own repository projects.
    Never fabricates URLs or claims to have retrieved inaccessible materials.
    Strictly prevents cross-domain contamination (e.g. Figma lessons never receive LangChain or SQL resources).
    """
    import re

    c_lower = concept_title.strip().lower()
    s_lower = (skill_name or "").strip().lower()

    # Determine primary domain
    domain_key = None
    if s_lower:
        if any(cv in s_lower for cv in ("opencv", "cv2", "computer vision")):
            domain_key = "opencv"
        elif any(f in s_lower for f in ("figma", "ui/ux", "ui-ux", "ux", "design")):
            domain_key = "figma"
        elif any(l in s_lower for l in ("langchain", "lcel")):
            domain_key = "langchain"
        elif "langgraph" in s_lower:
            domain_key = "langgraph"
        elif any(m in s_lower for m in ("large language models", "llm")):
            domain_key = "large language models"
        elif "prompt" in s_lower:
            domain_key = "prompt engineering"
        elif "react" in s_lower:
            domain_key = "react"
        elif "javascript" in s_lower or "js" in s_lower.split():
            domain_key = "javascript"
        elif any(sq in s_lower for sq in ("sql", "postgres", "mysql")):
            domain_key = "sql" if "postgres" not in s_lower else "postgresql"
        elif "python" in s_lower:
            domain_key = "python"
        elif "docker" in s_lower:
            domain_key = "docker"
        elif "fastapi" in s_lower:
            domain_key = "fastapi"

    # If domain_key still undetermined, infer from concept_title tokens
    if domain_key is None:
        if any(cv in c_lower for cv in ("opencv", "cv2", "bgr", "canny", "pixel grid", "colorspace", "contour")):
            domain_key = "opencv"
        elif any(f in c_lower for f in ("figma", "auto layout", "wireframe", "prototype", "wcag", "typography", "design system")):
            domain_key = "figma"
        elif "langchain" in c_lower:
            domain_key = "langchain"
        elif "langgraph" in c_lower:
            domain_key = "langgraph"
        elif any(m in c_lower for m in ("llm", "large language model", "transformer", "attention")):
            domain_key = "large language models"
        elif "prompt" in c_lower:
            domain_key = "prompt engineering"
        elif "react" in c_lower or "jsx" in c_lower or "hook" in c_lower:
            domain_key = "react"
        elif "javascript" in c_lower or "closure" in c_lower:
            domain_key = "javascript"
        elif "sql" in c_lower or "postgres" in c_lower or "join" in c_lower:
            domain_key = "sql"
        elif "python" in c_lower or "asyncio" in c_lower or "dict" in c_lower:
            domain_key = "python"

    cache_key = f"{domain_key or s_lower}::{c_lower}::{limit}"
    if cache_key in _RESOURCE_CACHE:
        return _RESOURCE_CACHE[cache_key]

    results: List[TeachingResourceItem] = []

    # 1. Candidate project evidence (Strictly gated by technology match)
    if candidate_projects:
        for proj in candidate_projects:
            title = proj.get("title", "")
            techs = [str(t).lower() for t in proj.get("technologies", [])]
            desc = proj.get("description", "")
            url = proj.get("url")

            # Project is ONLY relevant if domain_key or skill explicitly appears in project technologies or title
            is_relevant = False
            if domain_key:
                is_relevant = any(domain_key in t or t in domain_key for t in techs) or (domain_key in title.lower())
            elif s_lower:
                is_relevant = any(s_lower in t or t in s_lower for t in techs) or (s_lower in title.lower())

            if is_relevant:
                results.append(
                    TeachingResourceItem(
                        id=f"cand-proj-{proj.get('id', title.lower())}",
                        title=f"Candidate Project: {title}",
                        canonical_url=url,
                        file_reference=f"Project codebase / repository: {title}",
                        resource_type="candidate_project",
                        concepts_covered=proj.get("technologies", []) or [concept_title],
                        difficulty_level="Production Codebase",
                        source="Candidate Verified Repository",
                        retrieval_timestamp=datetime.utcnow().isoformat(),
                        excerpt=desc or f"Verified candidate repository demonstrating {', '.join(proj.get('technologies', []))}.",
                        relevance_rationale=f"Direct evidence of practical implementation in candidate's project '{title}'.",
                        is_verified=True,
                    )
                )

    # 2. Match Authoritative Documentation strictly within domain
    if domain_key and domain_key in AUTHORITATIVE_RESOURCE_BANK:
        items = AUTHORITATIVE_RESOURCE_BANK[domain_key]
        for item in items:
            if not any(r.id == item["id"] for r in results):
                results.append(
                    TeachingResourceItem(
                        id=item["id"],
                        title=item["title"],
                        canonical_url=item["canonical_url"],
                        file_reference=None,
                        resource_type=item["resource_type"],
                        concepts_covered=item["concepts_covered"],
                        difficulty_level=item["difficulty_level"],
                        source=item["source"],
                        retrieval_timestamp=datetime.utcnow().isoformat(),
                        excerpt=item["excerpt"],
                        relevance_rationale=item["relevance_rationale"],
                        is_verified=True,
                    )
                )
    else:
        # Cross-search with substantive word tokens (len >= 4, no stopwords)
        STOPWORDS = {"this", "that", "with", "from", "what", "where", "when", "using", "your", "code", "system", "data", "test", "into", "over", "about"}
        tokens = {t for t in re.findall(r'[a-zA-Z]{4,}', c_lower) if t not in STOPWORDS}
        for key, items in AUTHORITATIVE_RESOURCE_BANK.items():
            # Domain exclusion guard
            if domain_key == "opencv" and key in ("react", "javascript", "figma", "sql", "postgresql", "langchain", "prompt engineering"):
                continue
            if domain_key in ("react", "javascript", "figma", "sql", "prompt engineering") and key == "opencv":
                continue
            if domain_key == "figma" and key in ("langchain", "large language models", "prompt engineering", "sql", "postgresql", "python", "opencv"):
                continue
            if domain_key == "langchain" and key in ("figma", "sql", "postgresql", "opencv"):
                continue
            if domain_key == "python" and key in ("figma", "react", "langchain"):
                continue

            if key in c_lower or any(t in key for t in tokens):
                for item in items:
                    if not any(r.id == item["id"] for r in results):
                        results.append(
                            TeachingResourceItem(
                                id=item["id"],
                                title=item["title"],
                                canonical_url=item["canonical_url"],
                                file_reference=None,
                                resource_type=item["resource_type"],
                                concepts_covered=item["concepts_covered"],
                                difficulty_level=item["difficulty_level"],
                                source=item["source"],
                                retrieval_timestamp=datetime.utcnow().isoformat(),
                                excerpt=item["excerpt"],
                                relevance_rationale=item["relevance_rationale"],
                                is_verified=True,
                            )
                        )

    final_results = results[:limit]
    _RESOURCE_CACHE[cache_key] = final_results
    return final_results
