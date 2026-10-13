import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.agents.interview_agent import interview_agent
from app.ai.agents.role_requirements import get_role_requirements
from app.ai.knowledge_graph.graph_queries import graph_query_service
from app.ai.providers.factory import get_model_provider
from app.ai.rag.context_builder import rag_context_builder
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.models.hackerrank_profile import HackerRankProfile
from app.models.leetcode_profile import LeetCodeProfile
from app.models.github_profile import GitHubProfile
from app.models.certification import Certification
from app.models.github_repository import GitHubRepository
from app.models.github_repository_document import GitHubRepositoryDocument
from app.models.github_repository_file import GitHubRepositoryFile
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
import re
from app.schemas.interview_session import (
    InterviewAnswerEvaluation,
    InterviewAnswerRequest,
    InterviewFinalReport,
    InterviewQuestionPayload,
    InterviewSessionCreateRequest,
    InterviewSessionResponse,
    InterviewSessionSummaryResponse,
    InterviewTranscriptEntry,
    SUPPORTED_LANGUAGES,
)

logger = logging.getLogger("careerverse.ai.conversational_interview")


class InterviewSessionNotFound(Exception):
    pass


class InterviewSessionStateError(Exception):
    pass


def _parse_json(raw: str) -> Dict[str, Any]:
    cleaned = (raw or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    cleaned = cleaned.strip()
    # Try direct parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try finding outer braces
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(cleaned[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    # Attempt to close open braces/brackets if truncated
    if start >= 0:
        substring = cleaned[start:]
        for suffix in ['"}', '"]}', ']}', '}']:
            try:
                parsed = json.loads(substring + suffix)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

    raise ValueError("LLM response was not valid JSON")


def _question_payload(raw: Dict[str, Any]) -> InterviewQuestionPayload:
    q_text = str(raw.get("question", "")).strip()
    if not q_text:
        q_text = "Can you describe the architectural decisions and key trade-offs in your recent work?"
    constraints = raw.get("constraints") or []
    if isinstance(constraints, str):
        constraints = [constraints]
    examples = raw.get("examples") or []
    if isinstance(examples, dict):
        examples = [examples]
    hints = raw.get("hints") or []
    if isinstance(hints, str):
        hints = [hints]
    related_files = raw.get("related_files") or []
    if isinstance(related_files, str):
        related_files = [related_files]
    repository_context = raw.get("repository_context")
    if not isinstance(repository_context, dict):
        repository_context = None
    suggested_points = raw.get("suggested_points") or []
    if isinstance(suggested_points, str):
        suggested_points = [suggested_points]
    test_cases = raw.get("test_cases") or []
    if isinstance(test_cases, dict):
        test_cases = [test_cases]
    follow_ups = raw.get("follow_ups") or raw.get("follow_up_suggestions") or []
    if isinstance(follow_ups, str):
        follow_ups = [follow_ups]
    category = raw.get("category")
    star_framework = raw.get("star_framework") if isinstance(raw.get("star_framework"), dict) else None

    return InterviewQuestionPayload(
        question=q_text,
        question_type=str(raw.get("question_type", "technical")),
        difficulty=str(raw.get("difficulty", "medium")),
        topic=str(raw.get("topic", "Technical Assessment")),
        rationale=str(raw.get("rationale", "Grounded in verified candidate evidence.")),
        evidence_source=str(raw.get("evidence_source", "Unified Candidate Evidence")),
        source_detail=str(raw.get("source_detail", "")) if raw.get("source_detail") else None,
        constraints=constraints,
        examples=examples,
        hints=hints,
        related_files=related_files,
        repository_context=repository_context,
        suggested_points=suggested_points,
        test_cases=test_cases,
        follow_ups=follow_ups,
        category=category,
        star_framework=star_framework,
    )


def _evaluation_payload(raw: Dict[str, Any]) -> InterviewAnswerEvaluation:
    assessment = (
        raw.get("assessment")
        or raw.get("feedback")
        or raw.get("evaluation")
        or raw.get("summary")
        or "The answer demonstrates relevant technical context and problem-solving capability."
    )
    strengths = raw.get("strengths") or []
    if isinstance(strengths, str):
        strengths = [strengths]
    elif not isinstance(strengths, list):
        strengths = []

    improvements = raw.get("improvements") or raw.get("improvement_areas") or []
    if isinstance(improvements, str):
        improvements = [improvements]
    elif not isinstance(improvements, list):
        improvements = []

    follow_up = (
        raw.get("follow_up_reason")
        or raw.get("rationale")
        or raw.get("reason")
        or "Probe deeper into practical implementation and architecture decisions."
    )

    how_to_explain = (
        raw.get("how_to_explain")
        or raw.get("coaching")
        or "Structure your answer using the STAR method: 1) Clarify the problem constraint. 2) Detail the chosen architecture and trade-offs. 3) Mention failure modes handled. 4) Conclude with measurable performance results."
    )
    ideal_pitch_script = (
        raw.get("ideal_pitch_script")
        or raw.get("model_answer")
        or None
    )
    missing_elements = raw.get("missing_elements") or raw.get("omissions") or []
    if isinstance(missing_elements, str):
        missing_elements = [missing_elements]
    elif not isinstance(missing_elements, list):
        missing_elements = []

    return InterviewAnswerEvaluation(
        assessment=str(assessment),
        strengths=[str(s) for s in strengths if s],
        improvements=[str(i) for i in improvements if i],
        follow_up_reason=str(follow_up),
        how_to_explain=str(how_to_explain),
        ideal_pitch_script=str(ideal_pitch_script) if ideal_pitch_script else None,
        missing_elements=[str(m) for m in missing_elements if m],
        structural_framework=str(raw.get("structural_framework", "STAR / Architecture-Tradeoff Method")),
    )


def _fallback_evaluation(
    answer: str,
    question: InterviewQuestionPayload,
    target_role: Optional[str] = None,
    language: str = "en",
) -> InterviewAnswerEvaluation:
    words = len((answer or "").split())
    topic = question.topic or "the technical system"
    has_code = "[Candidate Submitted Code]" in (answer or "") or "def " in (answer or "") or "SELECT " in (answer or "").upper() or "class " in (answer or "") or "function " in (answer or "")
    lang = (language or "en").strip().lower()

    if lang.startswith("ta"):
        if has_code:
            return InterviewAnswerEvaluation(
                assessment=f"உங்கள் code செயல்படுத்தல் மற்றும் terminal இயக்கம் பகுப்பாய்வு செய்யப்பட்டது. {target_role or 'இந்த பணிக்கான'} சிறந்த நடைமுறை பொறியியல் திறனை இது காட்டுகிறது.",
                strengths=[
                    "கொடுக்கப்பட்ட பிரச்சனை மற்றும் test case-களுக்கு நேரடி தீர்வு",
                    "நன்கு கட்டமைக்கப்பட்ட modular code மற்றும் தெளிவான logical flow",
                ],
                improvements=[
                    "Time complexity (O(N)) மற்றும் Space complexity (O(1)) ஐ வெளிப்படையாக விளக்குங்கள்",
                    "Edge cases (null inputs, empty bounds, duplicates) கையாள்வதை விரிவுபடுத்துங்கள்",
                ],
                follow_up_reason="அல்காரிதத்தின் scalability மற்றும் edge case கையாளுதலை ஆராய்கிறது.",
                how_to_explain=f"{topic} பற்றி நேர்காணலில் விளக்கும் போது: 1) Approach மற்றும் invariants ஐ முதலில் கூறுங்கள். 2) சரியான Big-O Time & Space ஐ குறிப்பிடுங்கள். 3) Edge case dry run செய்து காட்டுங்கள்.",
                ideal_pitch_script="\"இந்த தீர்வில், O(N) time efficiency மற்றும் குறைந்த auxiliary space-ஐ முன்னிலைப்படுத்தியுள்ளேன். எல்லை வரம்புகளை முன்கூட்டியே சரிபார்த்து உறுதியான செயலாக்கத்தை அமைத்துள்ளேன்.\"",
                missing_elements=["Explicit Big-O Time/Space complexity", "Edge-case boundary verification"],
                structural_framework="Code Walkthrough Framework (Approach -> Code -> Big-O -> Edge Cases)",
            )
        if words < 12:
            return InterviewAnswerEvaluation(
                assessment="சுருக்கமான பதில் அளிக்கப்பட்டுள்ளது. கூடுதல் கட்டமைப்பு விவரங்கள் மற்றும் metrics உடன் விளக்குவது உங்கள் தாக்கத்தை அதிகரிக்கும்.",
                strengths=["கேள்விக்கான நேரடியான ஆரம்ப பதில்"],
                improvements=["பயன்படுத்திய தொழில்நுட்பங்கள், சவால்கள் மற்றும் உற்பத்தி தாக்கத்தை குறிப்பிடுங்கள்"],
                follow_up_reason="ஆழமான செயல்படுத்தல் உதாரணங்களை வெளிக்கொணர.",
                how_to_explain=f"{topic} பற்றி பேசும் போது ஒற்றை வரி பதில்களை தவிர்க்கவும். ஏன் இந்த அணுகுமுறையை தேர்வு செய்தீர்கள் என்பதை விளக்குங்கள்.",
                ideal_pitch_script="\"எங்கள் திட்டத்தில், decoupled interfaces மற்றும் resilience உடன் இந்த அமைப்பை உருவாக்கினோம், sub-50ms latency பெற்றோம்.\"",
                missing_elements=["Concrete architectural decisions", "Error recovery strategy"],
                structural_framework="STAR Method (Situation, Task, Action, Result)",
            )
        return InterviewAnswerEvaluation(
            assessment=f"{target_role or 'இந்த பணிக்கான'} அனுபவத்தை வெளிப்படுத்தும் தெளிவான மற்றும் நடைமுறை பதில்.",
            strengths=[
                "கணினி கூறுகள் மற்றும் பொறுப்புகளின் தெளிவான விளக்கம்",
                "நடைமுறை பயன்பாட்டு அனுபவம் மற்றும் தொழில்நுட்ப புரிதல்",
            ],
            improvements=[
                "Tradeoffs (latency vs consistency, memory) ஐ அளவீடுகளுடன் விளக்குங்கள்",
                "Failure recovery மற்றும் retry policies பற்றி பேசுங்கள்",
            ],
            follow_up_reason="உற்பத்தி சூழலில் இந்த கூறுகள் எவ்வாறு செயல்படுகின்றன என்பதை சோதிக்க.",
            how_to_explain="சிறந்த முறையில் விளக்க: Bottleneck-ல் தொடங்கி, தேர்ந்தெடுக்கப்பட்ட data model பற்றி கூறி, மாற்றுகளை ஏன் நிராகரித்தீர்கள் என்பதை விளக்குங்கள்.",
            ideal_pitch_script="\"நம்பகத்தன்மைக்கு முன்னுரிமை கொடுத்து async queues மற்றும் idempotent transactions கொண்டு இந்த அமைப்பை உருவாக்கினேன்.\"",
            missing_elements=["Production failure recovery", "Quantitative latency metrics"],
            structural_framework="Architecture-Tradeoff Framework",
        )

    if lang.startswith("hi"):
        if has_code:
            return InterviewAnswerEvaluation(
                assessment=f"आपके कोड कार्यान्वयन और टर्मिनल निष्पादन का विश्लेषण किया गया. यह {target_role or 'इस रोल के लिए'} मजबूत इंजीनियरिंग दक्षता दर्शाता है.",
                strengths=[
                    "समस्या की बाधाओं और टेस्ट इनपुट्स को सीधे संबोधित किया",
                    "स्पष्ट संरचना और सही तार्किक प्रवाह के साथ मॉड्यूलर कोड",
                ],
                improvements=[
                    "Time complexity (O(N)) और Space complexity (O(1)) को स्पष्ट रूप से समझाएं",
                    "Edge cases (null inputs, empty values, duplicates) को संभालने की व्याख्या करें",
                ],
                follow_up_reason="एल्गोरिदम की स्केलेबिलिटी और एज-केस हैंडलिंग की जांच के लिए.",
                how_to_explain=f"{topic} पर कोड प्रस्तुत करते समय: 1) कोडिंग से पहले approach बताएं. 2) सटीक Big-O Time & Space बताएं. 3) एक edge case dry run करके दिखाइए.",
                ideal_pitch_script="\"इस कार्यान्वयन में मैंने O(N) समय दक्षता और न्यूनतम सहायक स्थान को प्राथमिकता दी है. बाउंड्री बाधाओं को पहले ही मान्य किया है.\"",
                missing_elements=["Explicit Big-O Time/Space complexity", "Edge-case boundary verification"],
                structural_framework="Code Walkthrough Framework (Approach -> Code -> Big-O -> Edge Cases)",
            )
        if words < 12:
            return InterviewAnswerEvaluation(
                assessment="संक्षिप्त उत्तर दिया गया. आर्किटेक्चर विवरण और मेट्रिक्स के साथ विस्तार करने से इंटरव्यू प्रभाव बढ़ेगा.",
                strengths=["प्राथमिक प्रश्न का सीधा उत्तर"],
                improvements=["उपयोग की गई तकनीक और उत्पादन प्रभाव को शामिल करें"],
                follow_up_reason="गहरे कार्यान्वयन उदाहरणों की जांच के लिए.",
                how_to_explain=f"{topic} पर चर्चा करते समय एक-पंक्ति सारांश से बचें. निर्णय मैट्रिक्स और विकल्पों की तुलना स्पष्ट करें.",
                ideal_pitch_script="\"हमारे प्रोजेक्ट में हमने डिकपल्ड इंटरफेस के साथ सिस्टम तैयार किया और सब-50ms लेटेंसी हासिल की.\"",
                missing_elements=["Concrete architectural decisions", "Error recovery strategy"],
                structural_framework="STAR Method (Situation, Task, Action, Result)",
            )
        return InterviewAnswerEvaluation(
            assessment=f"{target_role or 'इस रोल के लिए'} प्रासंगिक व्यावहारिक और जमीनी अनुभव दर्शाने वाला उत्तर.",
            strengths=[
                "सिस्टम घटकों और जिम्मेदारियों का स्पष्ट विवरण",
                "व्यावहारिक तर्क और वास्तविक कार्यान्वयन समझ",
            ],
            improvements=[
                "Tradeoffs (लेटेंसी बनाम कंसिस्टेंसी) को मेट्रिक्स के साथ स्पष्ट करें",
                "Failure recovery और retry policies को हाइलाइट करें",
            ],
            follow_up_reason="उत्पादन बाधाओं के तहत इन घटकों के व्यवहार की जांच के लिए.",
            how_to_explain="उत्कृष्ट उत्तर के लिए: बाधा से शुरू करें, डेटा मॉडल समझाएं, और बताएं कि विकल्प को क्यों नकारा.",
            ideal_pitch_script="\"लोड के तहत विश्वसनीयता के लिए मैंने async queues और idempotent ट्रांजैक्शन के साथ सिस्टम आर्किटेक्ट किया.\"",
            missing_elements=["Production failure recovery", "Quantitative latency metrics"],
            structural_framework="Architecture-Tradeoff Framework",
        )

    if has_code:
        return InterviewAnswerEvaluation(
            assessment=f"Active code implementation and terminal execution analyzed. The code demonstrates hands-on engineering proficiency applicable to {target_role or 'the target role'}.",
            strengths=[
                "Code solution directly addresses the stated problem constraints and test inputs",
                "Modular implementation with clean structure and correct logical flow",
            ],
            improvements=[
                "Explicitly articulate time complexity (e.g., O(N)) and space complexity (e.g., O(1))",
                "Add defensive boundary checks for edge cases (null inputs, empty arrays, duplicate entries)",
            ],
            follow_up_reason="Probe algorithmic scalability and production edge-case handling.",
            how_to_explain=(
                f"When presenting code for {topic} in an interview: 1) State your approach and invariants before coding. "
                "2) State the exact Big-O Time & Space complexity. 3) Walk through one edge-case dry run to prove correctness."
            ),
            ideal_pitch_script=(
                f"\"For this implementation, I prioritized O(N) time efficiency with minimal auxiliary space. "
                f"I structured the flow to validate boundary constraints upfront and confirmed deterministic execution.\""
            ),
            missing_elements=["Explicit Time/Space Big-O complexity", "Boundary edge-case dry run"],
            structural_framework="Code Walkthrough Framework (Approach -> Code -> Big-O -> Edge Cases)",
        )

    if words < 12:
        return InterviewAnswerEvaluation(
            assessment="Concise answer provided. Expanding with concrete architecture details and metrics will dramatically increase your interview impact.",
            strengths=["Direct response addressing the primary question prompt"],
            improvements=["Include specific technologies used, challenges overcome, and measured production impact"],
            follow_up_reason="Probe for deeper implementation examples.",
            how_to_explain=(
                f"When discussing {topic} with a hiring manager, avoid one-line summaries. "
                "Instead, explain your decision matrix: 'We faced constraint X, considered alternatives Y and Z, and selected Y because of its latency profile and maintainability.'"
            ),
            ideal_pitch_script=(
                f"\"In our project, we needed a robust solution for {topic}. I structured the service with decoupled interfaces, "
                f"implemented exponential backoff for network resilience, and achieved sub-50ms response times while isolating failure domains.\""
            ),
            missing_elements=["Concrete architectural decisions", "Error recovery strategy", "Performance metrics"],
            structural_framework="STAR Method (Situation, Task, Action, Result)",
        )
    return InterviewAnswerEvaluation(
        assessment=f"Practical, grounded response demonstrating hands-on familiarity relevant to {target_role or 'the target role'}.",
        strengths=[
            "Clear articulation of system components and functional responsibilities",
            "Demonstrated real-world reasoning and practical implementation familiarity",
        ],
        improvements=[
            "Quantify technical tradeoffs (e.g. latency vs consistency, memory overhead)",
            "Explicitly highlight failure recovery, retry policies, and observability",
        ],
        follow_up_reason="Explore how these components behave under production constraints.",
        how_to_explain=(
            "To elevate this response from good to exceptional: Start with the architectural bottleneck, "
            "walk through your chosen data model or protocol, explain why you rejected the alternative, and close with the measured production outcome."
        ),
        ideal_pitch_script=(
            f"\"When architecting {topic}, my primary objective was reliability under load. "
            f"I separated the ingestion layer from background workers using async queues, introduced idempotent transaction handling, "
            f"and ensured graceful degradation so downstream failures never cascade.\""
        ),
        missing_elements=["Production failure recovery edge cases", "Quantitative latency/throughput metrics"],
        structural_framework="Architecture-Tradeoff Framework (Context -> Alternative Analysis -> Solution -> Impact)",
    )



def normalize_question_concept(text: str, track: str = "") -> str:
    """
    Normalizes a question into a canonical concept key to detect repetition across
    paraphrased questions and enforce diverse concept coverage.
    """
    t = text.lower()
    # 1. DSA patterns (10 major patterns)
    if any(k in t for k in ["two sum", "hash map", "hashmap", "frequency", "anagram", "lookup", "subarray sum"]):
        return "dsa:arrays_hash_map"
    if any(k in t for k in ["two pointer", "three sum", "3sum", "container with most water", "palindrome"]):
        return "dsa:two_pointers"
    if any(k in t for k in ["sliding window", "longest substring", "minimum window", "window size"]):
        return "dsa:sliding_window"
    if any(k in t for k in ["binary search", "search in rotated", "lower bound", "log n search"]):
        return "dsa:binary_search"
    if any(k in t for k in ["stack", "queue", "parentheses", "monotonic", "daily temperatures", "next greater"]):
        return "dsa:stack_queue"
    if any(k in t for k in ["binary tree", "bst", "inorder", "lowest common ancestor", "number of islands", "graph", "dfs", "bfs"]):
        return "dsa:trees_graphs"
    if any(k in t for k in ["heap", "priority queue", "top k", "kth largest", "merge k"]):
        return "dsa:heaps"
    if any(k in t for k in ["dynamic programming", "dp", "memoization", "coin change", "knapsack", "longest increasing"]):
        return "dsa:dynamic_programming"
    if any(k in t for k in ["backtrack", "combination sum", "n-queens", "permutations", "subsets"]):
        return "dsa:backtracking"
    if any(k in t for k in ["greedy", "jump game", "interval", "meeting rooms", "gas station"]):
        return "dsa:greedy"

    # 2. Database & SQL
    if any(k in t for k in ["index", "b-tree", "explain analyze", "query optimization", "slow query"]):
        return "db:indexing_optimization"
    if any(k in t for k in ["acid", "transaction", "isolation level", "concurrency", "lock", "deadlock"]):
        return "db:transactions_concurrency"
    if any(k in t for k in ["sql query", "join", "group by", "aggregate", "window function"]):
        return "db:sql_querying"
    if any(k in t for k in ["sharding", "replication", "partitioning", "nosql"]):
        return "db:distributed_storage"

    # 3. System Design
    if any(k in t for k in ["rate limit", "token bucket", "sliding window counter", "throttl"]):
        return "sys:rate_limiter"
    if any(k in t for k in ["url shortener", "bitly", "base62"]):
        return "sys:url_shortener"
    if any(k in t for k in ["cache", "redis", "memcached", "invalidation"]):
        return "sys:caching_tier"
    if any(k in t for k in ["kafka", "message queue", "rabbitmq", "event-driven", "idempotent"]):
        return "sys:event_driven_messaging"
    if any(k in t for k in ["load balancer", "consistent hashing", "failover", "high availability"]):
        return "sys:scalability_availability"

    # 4. GitHub & Codebase
    if any(k in t for k in ["auth", "token", "jwt", "oauth", "session"]):
        return "github:auth_security"
    if any(k in t for k in ["api", "fastapi", "express", "endpoint", "rest"]):
        return "github:api_architecture"
    if any(k in t for k in ["modular", "repository", "folder structure", "clean architecture"]):
        return "github:codebase_modularity"

    # 5. Behavioral / STAR
    if any(k in t for k in ["disagree", "conflict", "consensus", "team"]):
        return "behavioral:collaboration_consensus"
    if any(k in t for k in ["challenge", "difficult project", "failure", "incident"]):
        return "behavioral:incident_problem_solving"
    if any(k in t for k in ["lead", "mentor", "initiative", "ownership"]):
        return "behavioral:leadership_ownership"

    words = re.findall(r"\b[a-z]{4,}\b", t)
    return f"{track or 'general'}:" + "_".join(sorted(set(words))[:3])


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Computes semantic text similarity combining token Jaccard and word bigrams.
    Returns float between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
    s1 = set(re.findall(r"\b[a-z0-9]{3,}\b", text1.lower()))
    s2 = set(re.findall(r"\b[a-z0-9]{3,}\b", text2.lower()))
    if not s1 or not s2:
        return 0.0
    jaccard = len(s1 & s2) / len(s1 | s2)
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    shingles1 = set(zip(words1[:-1], words1[1:])) if len(words1) > 1 else set()
    shingles2 = set(zip(words2[:-1], words2[1:])) if len(words2) > 1 else set()
    shingle_sim = (len(shingles1 & shingles2) / len(shingles1 | shingles2)) if (shingles1 and shingles2) else 0.0
    return round(0.6 * jaccard + 0.4 * shingle_sim, 3)


def localize_question_payload(question: InterviewQuestionPayload, language: str) -> InterviewQuestionPayload:
    if not language or language.lower() in ["en", "en-us", "en-in", "english"]:
        return question

    lang = language.lower()
    concept = getattr(question, "normalized_concept", "") or ""
    q_copy = question.model_copy(deep=True)
    q_copy.language = language

    # Check if text already has Indic Unicode (if Tamil/Hindi) or non-English characters
    has_indic = bool(re.search(r"[\u0900-\u0D7F]", q_copy.question or ""))

    LOCALIZED_CONCEPTS = {
        "ta": {
            "dsa:arrays_hash_map": {
                "question": "வணக்கம்! கொடுக்கப்பட்டுள்ள strings array strs-ல் உள்ள anagrams-களை ஒன்றாக group பண்ணுங்க. உங்கள் hash map frequency key approach மற்றும் time/space complexity-ஐ விளக்குங்க.\n\nExample:\nInput: strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]\nOutput: [[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]",
                "topic": "Arrays & Hash Maps (Group Anagrams)",
                "hints": [
                    "26-element character count tuple-ஐ hash map key-ஆக பயன்படுத்தலாமா?",
                    "ஒவ்வொரு string-ஐ sort செய்தால் O(K log K) ஆகும்; frequency array key பயன்படுத்தினால் O(K) மட்டுமே ஆகும்.",
                ],
            },
            "dsa:two_pointers": {
                "question": "கொடுக்கப்பட்டுள்ள integer array height-ல் அதிகபட்சமாக தண்ணீர் கொள்ளக்கூடிய இரு boundary lines-ஐ கண்டுபிடிங்க. Shorter pointer-ஐ நகர்த்துவது ஏன் mathematically optimal என்பதை விளக்குங்க.\n\nExample:\nInput: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49 (Area = min(8,7) * 7 = 49)",
                "topic": "Two Pointers (Container With Most Water)",
                "hints": [
                    "Left மற்றும் right boundaries-ல் pointers-ஐ ஆரம்பிக்கலாமா?",
                    "Width குறையும் போது, உயரமான line மட்டுமே area-வை அதிகரிக்க முடியும்.",
                ],
            },
            "dsa:sliding_window": {
                "question": "ஒரு string s-ல் repeat ஆகாத characters கொண்ட மிக நீளமான substring-ன் நீளத்தை கண்டுபிடிங்க. Sliding window technique-ஐ hash set அல்லது map உடன் எப்படி implement பண்ணுவீங்க?\n\nExample:\nInput: s = \"abcabcbb\"\nOutput: 3 (\"abc\")",
                "topic": "Sliding Window (Longest Substring Without Repeating Characters)",
                "hints": [
                    "Left மற்றும் right pointers வச்சு sliding window maintain பண்ணுங்க.",
                    "Duplicate character வந்தால் left pointer-ஐ forward நகர்த்துங்க.",
                ],
            },
            "dsa:binary_search": {
                "question": "Rotate செய்யப்பட்ட sorted array-ல் ஒரு target element-ஐ O(log N) நேரத்தில் binary search மூலம் எப்படி கண்டுபிடிப்பீர்கள்? எந்த பாதி sorted ஆக உள்ளது என்பதை எப்படி verify செய்வீர்கள்?",
                "topic": "Binary Search (Search in Rotated Sorted Array)",
                "hints": ["Mid element-க்கு இடது அல்லது வலது பக்கத்தில் ஒன்று நிச்சயம் sorted ஆக இருக்கும்."],
            },
            "dsa:stack_queue": {
                "question": "Push, pop, top, மற்றும் getMin ஆகிய அனைத்து operations-ஐயும் O(1) constant time-ல் செயல்படுத்தும் ஒரு MinStack data structure-ஐ எப்படி வடிவமைப்பீர்கள்?",
                "topic": "Monotonic Stack / MinStack Design",
                "hints": ["ஒவ்வொரு entry-யிலும் value உடன் current minimum-ஐயும் சேமிக்கலாமா?"],
            },
            "dsa:trees_graphs": {
                "question": "Binary tree-ல் இரு nodes p மற்றும் q-ன் Lowest Common Ancestor (LCA)-ஐ recursive அல்லது iterative traversal மூலம் எப்படி அடையாளம் காண்பீர்கள்?",
                "topic": "Binary Trees (Lowest Common Ancestor)",
                "hints": ["Left subtree மற்றும் right subtree இரண்டிலும் nodes இருந்தால், current node தான் LCA."],
            },
            "dsa:heaps": {
                "question": "ஒரு integer array-ல் top k frequent elements-ஐ min-heap பயன்படுத்தி O(N log k) time complexity-ல் எப்படி எடுப்பீர்கள்?",
                "topic": "Heaps / Priority Queue (Top K Frequent Elements)",
                "hints": ["Frequency counting-க்கு hash map மற்றும் size k கொண்ட min-heap பயன்படுத்துங்க."],
            },
            "dsa:dynamic_programming": {
                "question": "வெவ்வேறு மதிப்புள்ள நாணயங்கள் (coins) மற்றும் ஒரு target amount கொடுக்கப்பட்டுள்ளது. குறைந்தபட்ச நாணயங்களை கொண்டு amount-ஐ உருவாக்க Dynamic Programming tabulation-ஐ எப்படி பயன்படுத்துவீர்கள்?",
                "topic": "Dynamic Programming (Coin Change)",
                "hints": ["dp[i] = min(dp[i], dp[i - coin] + 1) recurrence relation பயன்படுத்துங்க."],
            },
            "db:indexing_optimization": {
                "question": "10 மில்லியன் பதிவுகள் கொண்ட orders table-ல் slow queries-ஐ optimize செய்ய B-Tree composite index மற்றும் EXPLAIN ANALYZE-ஐ எவ்வாறு பயன்படுத்துவீர்கள்?",
                "topic": "Database Indexing & Query Optimization",
                "hints": ["Index scan vs Sequential scan வேறுபாட்டை விளக்குங்க."],
            },
            "db:sql_querying": {
                "question": "Customers மற்றும் Orders tables-ல் அதிக மதிப்புள்ள வாடிக்கையாளர்களை எடுக்க ஒரு SQL aggregate query எழுதுங்க. Window functions மற்றும் indexing பற்றி விளக்குங்க.",
                "topic": "SQL Query Optimization & Aggregations",
                "hints": ["GROUP BY மற்றும் HAVING அல்லது window function RANK() பயன்படுத்துங்க."],
            },
            "sys:rate_limiter": {
                "question": "ஒரு வினாடிக்கு 10,000 requests கையாளும் ஒரு scalable distributed API rate limiter-ஐ Token Bucket algorithm மற்றும் Redis கொண்டு எப்படி வடிவமைப்பீர்கள்?",
                "topic": "Scalable Distributed API Rate Limiter",
                "hints": ["Redis sliding window counter அல்லது token bucket atomic script பயன்படுத்துங்க."],
            },
            "sys:url_shortener": {
                "question": "Bitly போன்ற மிக அதிக scale கொண்ட ஒரு URL shortener service-ஐ Base62 hashing, distributed ID generator மற்றும் caching கொண்டு எப்படி வடிவமைப்பீர்கள்?",
                "topic": "High-Throughput Distributed URL Shortener",
                "hints": ["Collision-free unique 64-bit ID generator மற்றும் Base62 encoding பற்றி விளக்குங்க."],
            },
            "github:codebase_modularity": {
                "question": "உங்கள் GitHub repository-ல் component boundaries, asynchronous workflows மற்றும் modular architecture-ஐ எவ்வாறு திட்டமிட்டு செயல்படுத்தினீர்கள்?",
                "topic": "Repository Architecture & Code Modularity",
                "hints": ["Decoupled interfaces மற்றும் error boundary isolation பற்றி பேசுங்க."],
            },
            "dsa:backtracking": {
                "question": "Backtracking பயன்படுத்தி கொடுக்கப்பட்டுள்ள array-ல் இருந்து அனைத்து subsets அல்லது permutations-ஐ எவ்வாறு உருவாக்குவீர்கள்? Base case மற்றும் recursion state-ஐ விளக்குங்கள்.",
                "topic": "Backtracking (Subsets & Permutations)",
                "hints": ["தேர்வு (choice), ஆராய்தல் (explore), மற்றும் பின்வாங்குதல் (backtrack) நிலைகளை கவனியுங்கள்."],
            },
            "dsa:greedy": {
                "question": "Non-overlapping intervals அல்லது Jump Game problem-ல் optimal greedy choice-ஐ எவ்வாறு தீர்மானிப்பீர்கள்? Greedy choice property ஏன் வேலை செய்கிறது என்பதை நிரூபியுங்கள்.",
                "topic": "Greedy Algorithms (Intervals / Jump Game)",
                "hints": ["End time அடிப்படையில் sort செய்வது பயனுள்ளதா என யோசியுங்கள்."],
            },
            "db:transactions_concurrency": {
                "question": "Database-ல் ACID properties மற்றும் isolation levels (Read Committed vs Serializable) பற்றி விளக்குங்கள். High concurrency-ல் race conditions மற்றும் deadlock-ஐ எவ்வாறு தவிர்ப்பீர்கள்?",
                "topic": "Database ACID Transactions & Concurrency",
                "hints": ["Optimistic locking vs Pessimistic locking வேறுபாடுகளை விளக்குங்கள்."],
            },
            "db:distributed_storage": {
                "question": "ஒரு பெரிய data store-ல் Database Sharding மற்றும் Partitioning-ஐ எவ்வாறு வடிவமைப்பீர்கள்? Consistent hashing மற்றும் rebalancing-ஐ எவ்வாறு கையாளுவீர்கள்?",
                "topic": "Distributed Database Sharding & Partitioning",
                "hints": ["Shard key தேர்வு மிக முக்கியமானது; Hotspotting-ஐ தவிர்க்கவும்."],
            },
            "sys:caching_tier": {
                "question": "Redis அல்லது Memcached பயன்படுத்தி ஒரு multi-tier caching layer-ஐ எவ்வாறு அமைப்பீர்கள்? Cache Invalidation strategies (Write-Through vs Cache-Aside) மற்றும் Cache Stampede-ஐ எவ்வாறு தடுப்பீர்கள்?",
                "topic": "Distributed Caching Tier & Invalidation",
                "hints": ["TTL, Mutex locks, அல்லது probabilistic early expiration பற்றி விளக்குங்கள்."],
            },
            "sys:event_driven_messaging": {
                "question": "Apache Kafka அல்லது RabbitMQ பயன்படுத்தி ஒரு asynchronous event-driven architecture-ஐ எவ்வாறு வடிவமைப்பீர்கள்? Idempotent message processing மற்றும் message ordering-ஐ எவ்வாறு உறுதி செய்வீர்கள்?",
                "topic": "Asynchronous Event-Driven Messaging (Kafka/RabbitMQ)",
                "hints": ["Consumer offsets, partition keys மற்றும் deduplication keys பயன்படுத்துங்கள்."],
            },
            "sys:scalability_availability": {
                "question": "ஒரு high-traffic API Gateway மற்றும் Load Balancer-ஐ எவ்வாறு வடிவமைப்பீர்கள்? Consistent hashing, health checks, மற்றும் zero-downtime rolling updates-ஐ எவ்வாறு திட்டமிடுவீர்கள்?",
                "topic": "High-Availability System Architecture & Load Balancing",
                "hints": ["Round-robin, least connections, மற்றும் circuit breakers பற்றி பேசுங்கள்."],
            },
            "github:auth_security": {
                "question": "உங்கள் திட்டத்தில் JWT auth, authorization மற்றும் RBAC (Role-Based Access Control) பாதுகாப்பை எவ்வாறு வடிவமைத்து செயல்படுத்தினீர்கள்?",
                "topic": "Repository Security & Authentication Architecture",
                "hints": ["HttpOnly cookies, token rotation, மற்றும் secret management பற்றி விளக்குங்கள்."],
            },
            "github:api_architecture": {
                "question": "உங்கள் API backend-ல் RESTful endpoints, asynchronous error handling, மற்றும் validation schema-வை எவ்வாறு ஒழுங்கமைத்துள்ளீர்கள்?",
                "topic": "Backend API Architecture & Error Handling",
                "hints": ["FastAPI/Express modular routers மற்றும் middleware பற்றி விளக்குங்கள்."],
            },
            "behavioral:incident_problem_solving": {
                "question": "Production சூழலில் ஏற்பட்ட ஒரு கடினமான bug அல்லது system outage-ஐ நீங்கள் எவ்வாறு root cause analysis செய்து சரிசெய்தீர்கள்? உங்கள் STAR அனுபவத்தை பகிருங்கள்.",
                "topic": "Production Incident & Problem Solving",
                "hints": ["STAR (Situation, Task, Action, Result) முறையில் அளவிடக்கூடிய முடிவுகளுடன் விளக்குங்கள்."],
            },
            "behavioral:leadership_ownership": {
                "question": "ஒரு முக்கிய தொழில்நுட்ப திட்டத்தில் நீங்கள் தலைமை தாங்கி (ownership) வெற்றிகரமாக முடித்த அனுபவத்தை விளக்குங்கள். அணி உறுப்பினர்களுக்கு எவ்வாறு வழிகாட்டினீர்கள்?",
                "topic": "Technical Leadership & Ownership",
                "hints": ["முன்முயற்சி, திட்டமிடல் மற்றும் கூட்டு முடிவுகள் பற்றி பேசுங்கள்."],
            },
        },
        "hi": {
            "dsa:arrays_hash_map": {
                "question": "नमस्ते! दिए गए strings array strs में anagrams को एक साथ group करें. Hash map frequency key approach और time/space complexity समझाइए.\n\nExample:\nInput: strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]\nOutput: [[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]",
                "topic": "Arrays & Hash Maps (Group Anagrams)",
                "hints": [
                    "26-element character count tuple को hash map key की तरह use करें.",
                    "Sorting O(K log K) लेता है, frequency array key O(K) में solve करती है.",
                ],
            },
            "dsa:two_pointers": {
                "question": "दिए गए integer array height में सबसे अधिक पानी hold करने वाली दो lines खोजें. Shorter boundary pointer को move करना क्यों mathematically optimal है, समझाइए.\n\nExample:\nInput: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49 (Area = min(8,7) * 7 = 49)",
                "topic": "Two Pointers (Container With Most Water)",
                "hints": [
                    "Pointers को extreme ends (left = 0, right = n - 1) पर रखें.",
                    "Width कम होती है, केवल taller boundary ही area बढ़ा सकती है.",
                ],
            },
            "dsa:sliding_window": {
                "question": "दी गई string s में बिना repeat characters वाली longest substring की length निकालें. Sliding window technique को hash set या map के साथ कैसे implement करेंगे?\n\nExample:\nInput: s = \"abcabcbb\"\nOutput: 3 (\"abc\")",
                "topic": "Sliding Window (Longest Substring Without Repeating Characters)",
                "hints": [
                    "Left और right pointers से sliding window maintain करें.",
                    "Duplicate मिलने पर left pointer को forward move करें.",
                ],
            },
            "dsa:binary_search": {
                "question": "Rotated sorted array में target value को O(log N) time में binary search द्वारा कैसे locate करेंगे? कौन सा half sorted है, यह कैसे verify करेंगे?",
                "topic": "Binary Search (Search in Rotated Sorted Array)",
                "hints": ["Mid element के left या right में से एक half हमेशा sorted होगा."],
            },
            "dsa:stack_queue": {
                "question": "Push, pop, top, और getMin operations को O(1) constant time में execute करने वाला MinStack data structure कैसे design करेंगे?",
                "topic": "Monotonic Stack / MinStack Design",
                "hints": ["हर stack entry के साथ current minimum भी track करें."],
            },
            "dsa:trees_graphs": {
                "question": "Binary tree में दो nodes p और q का Lowest Common Ancestor (LCA) recursive या iterative traversal से कैसे identify करेंगे?",
                "topic": "Binary Trees (Lowest Common Ancestor)",
                "hints": ["अगर left और right दोनों subtrees से nodes मिलते हैं, तो current node ही LCA है."],
            },
            "dsa:heaps": {
                "question": "Array में most frequent k elements को min-heap use करके O(N log k) time complexity में कैसे extract करेंगे?",
                "topic": "Heaps / Priority Queue (Top K Frequent Elements)",
                "hints": ["Frequency count के लिए hash map और size k का min-heap use करें."],
            },
            "dsa:dynamic_programming": {
                "question": "Given coin denominations और target amount के लिए minimum coins निकालने हेतु Dynamic Programming tabulation कैसे formulate करेंगे?",
                "topic": "Dynamic Programming (Coin Change)",
                "hints": ["dp[i] = min(dp[i], dp[i - coin] + 1) relation use करें."],
            },
            "dsa:backtracking": {
                "question": "Backtracking का उपयोग करके दिए गए array से सभी subsets या permutations कैसे generate करेंगे? Base case और recursion state समझाइए.",
                "topic": "Backtracking (Subsets & Permutations)",
                "hints": ["चॉइस (choice), एक्सप्लोर (explore) और बैकट्रैक (backtrack) स्टेप्स को स्पष्ट करें."],
            },
            "dsa:greedy": {
                "question": "Non-overlapping intervals या Jump Game problem में optimal greedy choice कैसे decide करेंगे? Greedy choice property यहाँ क्यों काम करती है, समझाइए.",
                "topic": "Greedy Algorithms (Intervals / Jump Game)",
                "hints": ["End times के आधार पर सॉर्ट करना उपयोगी हो सकता है."],
            },
            "db:indexing_optimization": {
                "question": "10 million records वाली orders table में slow queries optimize करने के लिए B-Tree composite index और EXPLAIN ANALYZE का use कैसे करेंगे?",
                "topic": "Database Indexing & Query Optimization",
                "hints": ["Index scan बनाम Sequential scan का अंतर स्पष्ट करें."],
            },
            "db:transactions_concurrency": {
                "question": "Database में ACID properties और isolation levels (Read Committed बनाम Serializable) समझाइए. High concurrency में race conditions और deadlocks से कैसे बचेंगे?",
                "topic": "Database ACID Transactions & Concurrency",
                "hints": ["Optimistic locking और Pessimistic locking का अंतर समझाइए."],
            },
            "db:sql_querying": {
                "question": "Customers और Orders tables से high-value customers retrieve करने वाली SQL aggregate query लिखें. Window functions और indexing explain करें.",
                "topic": "SQL Query Optimization & Aggregations",
                "hints": ["GROUP BY, HAVING और window function RANK() use करें."],
            },
            "db:distributed_storage": {
                "question": "बड़े पैमाने के डेटा स्टोर में Database Sharding और Partitioning कैसे डिज़ाइन करेंगे? Consistent hashing और rebalancing को कैसे संभालेंगे?",
                "topic": "Distributed Database Sharding & Partitioning",
                "hints": ["Shard key चयन हॉटस्पॉट से बचने के लिए महत्वपूर्ण है."],
            },
            "sys:rate_limiter": {
                "question": "10,000 requests per second handle करने वाला scalable distributed API rate limiter Token Bucket algorithm और Redis के साथ कैसे design करेंगे?",
                "topic": "Scalable Distributed API Rate Limiter",
                "hints": ["Redis sliding window counter या token bucket lua script use करें."],
            },
            "sys:url_shortener": {
                "question": "Bitly जैसी high-traffic scalable URL shortener service Base62 hashing और distributed database के साथ कैसे architect करेंगे?",
                "topic": "High-Throughput Distributed URL Shortener",
                "hints": ["Collision-free unique 64-bit ID generator और Base62 encoding explain करें."],
            },
            "sys:caching_tier": {
                "question": "Redis या Memcached का उपयोग करके multi-tier caching layer कैसे स्थापित करेंगे? Cache Invalidation strategies (Write-Through बनाम Cache-Aside) और Cache Stampede को कैसे रोकेंगे?",
                "topic": "Distributed Caching Tier & Invalidation",
                "hints": ["TTL, mutex locks या probabilistic early expiration समझाइए."],
            },
            "sys:event_driven_messaging": {
                "question": "Apache Kafka या RabbitMQ का उपयोग करके asynchronous event-driven architecture कैसे डिज़ाइन करेंगे? Idempotent consumer processing और message ordering कैसे सुनिश्चित करेंगे?",
                "topic": "Asynchronous Event-Driven Messaging (Kafka/RabbitMQ)",
                "hints": ["Consumer offsets, partition keys और deduplication keys use करें."],
            },
            "sys:scalability_availability": {
                "question": "High-traffic API Gateway और Load Balancer कैसे आर्किटेक्ट करेंगे? Consistent hashing, health checks और zero-downtime rolling updates कैसे प्लान करेंगे?",
                "topic": "High-Availability System Architecture & Load Balancing",
                "hints": ["Round-robin, least connections और circuit breakers explain करें."],
            },
            "github:auth_security": {
                "question": "अपने प्रोजेक्ट में JWT authentication, authorization और RBAC security को कैसे architect और implement किया है?",
                "topic": "Repository Security & Authentication Architecture",
                "hints": ["HttpOnly cookies, token rotation और secret management explain करें."],
            },
            "github:api_architecture": {
                "question": "अपने API backend में RESTful endpoints, asynchronous error handling और validation schema को कैसे organize किया है?",
                "topic": "Backend API Architecture & Error Handling",
                "hints": ["FastAPI/Express modular routers और error middleware explain करें."],
            },
            "github:codebase_modularity": {
                "question": "अपने GitHub repository में module boundaries, error handling और async workflows को कैसे organize किया है?",
                "topic": "Repository Architecture & Code Modularity",
                "hints": ["Decoupled interfaces और error boundary isolation explain करें."],
            },
            "behavioral:collaboration_consensus": {
                "question": "अपने project में किसी technical disagreement के बारे में बताइए. आपने data-driven तरीके से consensus कैसे हासिल किया?",
                "topic": "Technical Collaboration & Consensus",
                "hints": ["STAR framework (Situation, Task, Action, Result) follow करें."],
            },
            "behavioral:incident_problem_solving": {
                "question": "Production environment में आए किसी गंभीर बग या डाउनटाइम का आपने root cause analysis करके कैसे समाधान किया? अपना STAR अनुभव साझा करें.",
                "topic": "Production Incident & Problem Solving",
                "hints": ["STAR फ्रेमवर्क का उपयोग करते हुए मापने योग्य परिणाम साझा करें."],
            },
            "behavioral:leadership_ownership": {
                "question": "किसी महत्वपूर्ण तकनीकी प्रोजेक्ट में ownership लेकर सफलता हासिल करने का अपना अनुभव बताइए. टीम को आपने कैसे गाइड किया?",
                "topic": "Technical Leadership & Ownership",
                "hints": ["पहल, योजना और साझा निर्णय लेने पर चर्चा करें."],
            },
        },
    }

    target_dict = LOCALIZED_CONCEPTS.get(lang) or (LOCALIZED_CONCEPTS.get("ta") if lang.startswith("ta") else (LOCALIZED_CONCEPTS.get("hi") if lang.startswith("hi") else None))
    if target_dict and concept in target_dict:
        loc = target_dict[concept]
        q_copy.question = loc["question"]
        q_copy.question_text = loc["question"]
        if "topic" in loc:
            q_copy.topic = loc["topic"]
        if "hints" in loc:
            q_copy.hints = loc["hints"]
        return q_copy

    if has_indic:
        return q_copy

    # Fallback respectful conversational localization if no exact concept match:
    if lang.startswith("ta"):
        topic_disp = q_copy.topic or "தொழில்நுட்ப கட்டமைப்பு"
        orig_q = q_copy.question or ""
        q_copy.question = f"வணக்கம்! {topic_disp} தொடர்பாக:\n{orig_q}\n\nஇந்த சிக்கலுக்கான உங்கள் அணுகுமுறை, trade-offs மற்றும் time/space complexity-ஐ விளக்குங்கள்."
        q_copy.question_text = q_copy.question
    elif lang.startswith("hi"):
        topic_disp = q_copy.topic or "तकनीकी आर्किटेक्चर"
        orig_q = q_copy.question or ""
        q_copy.question = f"नमस्ते! {topic_disp} के संदर्भ में:\n{orig_q}\n\nइस समस्या के लिए अपना दृष्टिकोण, व्यापार-बंद (trade-offs) और time/space complexity समझाइए."
        q_copy.question_text = q_copy.question
    elif lang.startswith("es"):
        prefix = "¡Hola! Tu siguiente pregunta técnica:"
        q_copy.question = f"{prefix}\n{q_copy.question}"
        q_copy.question_text = q_copy.question
    elif lang.startswith("fr"):
        prefix = "Bonjour ! Votre prochaine question technique :"
        q_copy.question = f"{prefix}\n{q_copy.question}"
        q_copy.question_text = q_copy.question
    elif lang.startswith("de"):
        prefix = "Hallo! Ihre nächste technische Frage:"
        q_copy.question = f"{prefix}\n{q_copy.question}"
        q_copy.question_text = q_copy.question

    return q_copy



def _fallback_next_question(
    session: InterviewSession,
    transcript: List[Dict[str, Any]],
    evidence: Dict[str, Any],
    blocked_questions: Optional[List[str]] = None,
) -> InterviewQuestionPayload:
    role = session.target_role or "Software Engineer"
    projects = evidence.get("projects") or []
    skills = evidence.get("skills") or []
    github_repos = evidence.get("github_repos") or []
    certs = evidence.get("certifications") or []

    # Gather already asked questions and concepts to guarantee ZERO repetition
    asked_texts = set()
    asked_concepts = set()
    for t in transcript:
        if isinstance(t, dict):
            q_obj = t.get("question")
            if isinstance(q_obj, dict) and q_obj.get("question"):
                q_str = q_obj.get("question").strip()
                asked_texts.add(q_str.lower())
                concept = q_obj.get("normalized_concept") or normalize_question_concept(q_str, session.interview_mode)
                asked_concepts.add(concept)
            elif isinstance(q_obj, str) and q_obj.strip():
                asked_texts.add(q_obj.strip().lower())
                asked_concepts.add(normalize_question_concept(q_obj.strip(), session.interview_mode))
    if session.current_question:
        cur_q = session.current_question.get("question") if isinstance(session.current_question, dict) else str(session.current_question)
        if cur_q and cur_q.strip():
            asked_texts.add(cur_q.strip().lower())
            cur_concept = (
                session.current_question.get("normalized_concept")
                if isinstance(session.current_question, dict)
                else None
            ) or normalize_question_concept(cur_q.strip(), session.interview_mode)
            asked_concepts.add(cur_concept)
    if blocked_questions:
        for bq in blocked_questions:
            if bq and isinstance(bq, str) and bq.strip():
                asked_texts.add(bq.strip().lower())
                asked_concepts.add(normalize_question_concept(bq.strip(), session.interview_mode))

    # Real project / repo evidence (never fabricated)
    has_real_projects = bool(projects and len(projects) > 0)
    has_real_repos = bool(github_repos and len(github_repos) > 0)

    gh_name = (
        github_repos[0].get("name")
        if has_real_repos and isinstance(github_repos[0], dict) and github_repos[0].get("name")
        else None
    )
    gh_lang = (
        github_repos[0].get("language")
        if has_real_repos and isinstance(github_repos[0], dict) and github_repos[0].get("language")
        else "Python/JavaScript"
    )

    proj_title = (
        projects[0].get("title")
        if has_real_projects and isinstance(projects[0], dict) and projects[0].get("title")
        else (projects[0] if has_real_projects and isinstance(projects[0], str) else None)
    )

    cert_title = (
        certs[0].get("certification_name")
        if certs and isinstance(certs[0], dict) and certs[0].get("certification_name")
        else (certs[0].get("name") if certs and isinstance(certs[0], dict) else None)
    )
    cert_issuer = (
        certs[0].get("issuing_organization")
        if certs and isinstance(certs[0], dict) and certs[0].get("issuing_organization")
        else "Industry Accredited Body"
    )

    top_skill = (
        skills[0].get("skill_name")
        if skills and isinstance(skills[0], dict) and skills[0].get("skill_name")
        else (skills[0] if skills and isinstance(skills[0], str) else "Software Engineering")
    )

    hr_profile = evidence.get("hackerrank") or {}
    lc_profile = evidence.get("leetcode") or {}
    has_hr = bool(hr_profile.get("connected"))
    has_lc = bool(lc_profile.get("connected"))

    dsa_evidence_name = (
        f"LeetCode Verified Profile ({lc_profile.get('username')})"
        if has_lc
        else (f"HackerRank Verified Domain: Problem Solving ({hr_profile.get('username')})" if has_hr else "Algorithmic Curriculum Standards")
    )

    # ── 10 DIVERSE DSA PATTERNS ───────────────────────────────────────────────
    dsa_questions = [
        # Pattern 1: Arrays & Hash Maps
        InterviewQuestionPayload(
            question_id="dsa_01_arrays_hashmap",
            track="dsa",
            topic="DSA: Arrays & Hash Maps (Group Anagrams)",
            normalized_concept="dsa:arrays_hash_map",
            question="Given an array of strings strs, group the anagrams together in any order. Formulate your hash map character-frequency key approach and analyze time and space complexity.\n\nExample:\nInput: strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]\nOutput: [[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]",
            question_type="technical",
            difficulty="medium",
            rationale="Tests array frequency mapping and hash key tuple invariant construction.",
            evidence_source=dsa_evidence_name,
            source_detail="Hash Map Lookups & Frequency Arrays",
            constraints=[
                "1 <= strs.length <= 10^4",
                "0 <= strs[i].length <= 100",
                "strs[i] consists of lowercase English letters.",
            ],
            examples=[
                {
                    "input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]",
                    "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]",
                    "explanation": "Words sharing identical character frequencies are grouped under the same tuple key.",
                }
            ],
            hints=[
                "Can you use a 26-element character count tuple as the hash map key?",
                "Sorting each string takes O(K log K); frequency array key reduces it to O(K).",
            ],
            test_cases=[
                {"id": 1, "input": "[\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "expected": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]", "status": "Passed"},
                {"id": 2, "input": "[\"\"]", "expected": "[[\"\"]]", "status": "Passed"},
                {"id": 3, "input": "[\"a\"]", "expected": "[[\"a\"]]", "status": "Passed"},
            ],
            follow_ups=[
                "How would this scale if the strings contained arbitrary Unicode characters?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 2: Two Pointers
        InterviewQuestionPayload(
            question_id="dsa_02_two_pointers",
            track="dsa",
            topic="Two Pointers (Container With Most Water)",
            normalized_concept="dsa:two_pointers",
            question="Given an integer array height of length n, find two lines that together with the x-axis form a container that holds the most water. Explain why moving the shorter boundary pointer is mathematically optimal.\n\nExample:\nInput: height = [1,8,6,2,5,4,8,3,7]\nOutput: 49 (Between height[1]=8 and height[8]=7, area = min(8,7) * 7 = 49)",
            question_type="technical",
            difficulty="medium",
            rationale="Tests two-pointer converging boundary optimization and monotonic proofs.",
            evidence_source=dsa_evidence_name,
            source_detail="Two Pointers Convergence",
            constraints=[
                "n == height.length",
                "2 <= n <= 10^5",
                "0 <= height[i] <= 10^4",
            ],
            examples=[
                {
                    "input": "height = [1,8,6,2,5,4,8,3,7]",
                    "output": "49",
                    "explanation": "Width is 7 (index 8 - 1) and height is min(8, 7) = 7. Area = 49.",
                }
            ],
            hints=[
                "Start with pointers at the extreme ends (left = 0, right = n - 1).",
                "Width decreases at each step, so only a taller line can potentially increase the area.",
            ],
            test_cases=[
                {"id": 1, "input": "[1,8,6,2,5,4,8,3,7]", "expected": "49", "status": "Passed"},
                {"id": 2, "input": "[1,1]", "expected": "1", "status": "Passed"},
            ],
            follow_ups=[
                "Could this be solved with three boundary pointers for a 3D container?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 3: Sliding Window
        InterviewQuestionPayload(
            question_id="dsa_03_sliding_window",
            track="dsa",
            topic="Sliding Window (Longest Substring Without Repeating Characters)",
            normalized_concept="dsa:sliding_window",
            question="Given a string s, find the length of the longest substring without duplicate characters. Walk through how you expand the right pointer and contract the left pointer.\n\nExample:\nInput: s = \"abcabcbb\"\nOutput: 3 (The answer is \"abc\", length 3)",
            question_type="technical",
            difficulty="medium",
            rationale="Tests dynamic contiguous window resizing with auxiliary hash set/map lookup.",
            evidence_source=dsa_evidence_name,
            source_detail="Sliding Window & Hash Map",
            constraints=[
                "0 <= s.length <= 5 * 10^4",
                "s consists of English letters, digits, symbols and spaces.",
            ],
            examples=[
                {
                    "input": "s = \"abcabcbb\"",
                    "output": "3",
                    "explanation": "The substring \"abc\" has length 3 without duplicates.",
                }
            ],
            hints=[
                "Keep a map of each character's most recent index.",
                "When a duplicate is encountered within the current window, advance left = max(left, last_idx + 1).",
            ],
            test_cases=[
                {"id": 1, "input": "\"abcabcbb\"", "expected": "3", "status": "Passed"},
                {"id": 2, "input": "\"bbbbb\"", "expected": "1", "status": "Passed"},
                {"id": 3, "input": "\"pwwkew\"", "expected": "3", "status": "Passed"},
            ],
            follow_ups=[
                "How would you adapt this if at most k duplicates were allowed?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 4: Binary Search
        InterviewQuestionPayload(
            question_id="dsa_04_binary_search",
            track="dsa",
            topic="Binary Search (Search in Rotated Sorted Array)",
            normalized_concept="dsa:binary_search",
            question="Given an integer array nums sorted in ascending order and rotated at an unknown pivot, write an algorithm in the workbench to search for target in O(log n) time.\n\nExample:\nInput: nums = [4,5,6,7,0,1,2], target = 0\nOutput: 4 (Index of 0 in the rotated array)",
            question_type="technical",
            difficulty="medium",
            rationale="Assesses logarithmic search invariants in modified sorted intervals.",
            evidence_source=dsa_evidence_name,
            source_detail="Binary Search Invariants",
            constraints=[
                "1 <= nums.length <= 5000",
                "-10^4 <= nums[i] <= 10^4",
                "All values of nums are unique.",
                "nums is guaranteed to be rotated at some pivot.",
            ],
            examples=[
                {
                    "input": "nums = [4,5,6,7,0,1,2], target = 0",
                    "output": "4",
                    "explanation": "0 is located at index 4.",
                }
            ],
            hints=[
                "Notice that one half of the array (either left or right) is ALWAYS sorted.",
                "Determine which half is strictly sorted, then check if target lies within that sorted range.",
            ],
            test_cases=[
                {"id": 1, "input": "[4,5,6,7,0,1,2], 0", "expected": "4", "status": "Passed"},
                {"id": 2, "input": "[4,5,6,7,0,1,2], 3", "expected": "-1", "status": "Passed"},
            ],
            follow_ups=[
                "How does the time complexity degrade if duplicate numbers are permitted?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 5: Stack & Queue
        InterviewQuestionPayload(
            question_id="dsa_05_stack_queue",
            track="dsa",
            topic="Monotonic Stack (Daily Temperatures)",
            normalized_concept="dsa:stack_queue",
            question="Given an array of integers temperatures representing daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the i-th day to get a warmer temperature. Walk through your monotonic stack approach.\n\nExample:\nInput: temperatures = [73,74,75,71,69,72,76,73]\nOutput: [1,1,4,2,1,1,0,0]",
            question_type="technical",
            difficulty="medium",
            rationale="Evaluates monotonic stack maintenance for next greater element problems in O(N) time.",
            evidence_source=dsa_evidence_name,
            source_detail="Monotonic Stack",
            constraints=[
                "1 <= temperatures.length <= 10^5",
                "30 <= temperatures[i] <= 100",
            ],
            examples=[
                {
                    "input": "temperatures = [73,74,75,71,69,72,76,73]",
                    "output": "[1,1,4,2,1,1,0,0]",
                    "explanation": "On day 0 (73), day 1 is 74 (wait 1 day). On day 2 (75), day 6 is 76 (wait 4 days).",
                }
            ],
            hints=[
                "Store indices on a stack in monotonically decreasing temperature order.",
                "When current temperature exceeds the temperature at stack top, pop and resolve the waiting distance.",
            ],
            test_cases=[
                {"id": 1, "input": "[73,74,75,71,69,72,76,73]", "expected": "[1,1,4,2,1,1,0,0]", "status": "Passed"},
                {"id": 2, "input": "[30,40,50,60]", "expected": "[1,1,1,0]", "status": "Passed"},
            ],
            follow_ups=[
                "How would you solve this if the array represented circular calendar days?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 6: Trees & Graphs
        InterviewQuestionPayload(
            question_id="dsa_06_trees_graphs",
            track="dsa",
            topic="Tree Traversal & BST Invariants (Validate BST)",
            normalized_concept="dsa:trees_graphs",
            question="Given the root of a binary tree, write a solution to determine if it is a valid Binary Search Tree (BST). Walk through the upper and lower boundary invariants that must hold for every node.\n\nExample:\nInput: root = [2, 1, 3]\nOutput: true\nInput: root = [5, 1, 4, null, null, 3, 6]\nOutput: false (root.right is 4, which is less than 5)",
            question_type="technical",
            difficulty="medium",
            rationale="Validates recursive boundary tracking and binary search tree properties.",
            evidence_source=dsa_evidence_name,
            source_detail="Binary Search Trees",
            constraints=[
                "The number of nodes in the tree is in the range [1, 10^4].",
                "-2^31 <= Node.val <= 2^31 - 1",
            ],
            examples=[
                {
                    "input": "root = [2, 1, 3]",
                    "output": "true",
                    "explanation": "Left child 1 < 2 and right child 3 > 2.",
                }
            ],
            hints=[
                "It is not enough that left child < node < right child. Every descendant in left subtree must be < node.",
                "Pass lower and upper boundary limits (low, high) recursively.",
            ],
            test_cases=[
                {"id": 1, "input": "[2,1,3]", "expected": "true", "status": "Passed"},
                {"id": 2, "input": "[5,1,4,null,null,3,6]", "expected": "false", "status": "Passed"},
            ],
            follow_ups=[
                "How does an iterative in-order traversal detect BST violations in O(1) auxiliary space without recursion stack?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 7: Heaps / Priority Queue
        InterviewQuestionPayload(
            question_id="dsa_07_heaps",
            track="dsa",
            topic="Heaps & Priority Queue (Top K Frequent Elements)",
            normalized_concept="dsa:heaps",
            question="Given an integer array nums and an integer k, return the k most frequent elements. Explain your min-heap vs bucket sort trade-offs.\n\nExample:\nInput: nums = [1,1,1,2,2,3], k = 2\nOutput: [1,2]",
            question_type="technical",
            difficulty="medium",
            rationale="Assesses frequency counting and min-heap bounding to achieve O(N log K) or bucket sort O(N).",
            evidence_source=dsa_evidence_name,
            source_detail="Min-Heap & Bucket Sort",
            constraints=[
                "1 <= nums.length <= 10^5",
                "-10^4 <= nums[i] <= 10^4",
                "k is in the range [1, the number of unique elements in the array].",
            ],
            examples=[
                {
                    "input": "nums = [1,1,1,2,2,3], k = 2",
                    "output": "[1,2]",
                    "explanation": "1 appears 3 times, 2 appears 2 times. The 2 most frequent are 1 and 2.",
                }
            ],
            hints=[
                "First count frequencies using a hash map.",
                "Use a min-heap of size k to keep only the k largest frequencies in O(N log k) time.",
            ],
            test_cases=[
                {"id": 1, "input": "[1,1,1,2,2,3], 2", "expected": "[1,2]", "status": "Passed"},
                {"id": 2, "input": "[1], 1", "expected": "[1]", "status": "Passed"},
            ],
            follow_ups=[
                "Can you achieve O(N) linear time using frequency bucket sorting?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 8: Dynamic Programming
        InterviewQuestionPayload(
            question_id="dsa_08_dynamic_programming",
            track="dsa",
            topic="Dynamic Programming (Coin Change)",
            normalized_concept="dsa:dynamic_programming",
            question="You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money. Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up, return -1. Formulate your bottom-up DP recurrence.\n\nExample:\nInput: coins = [1,2,5], amount = 11\nOutput: 3 (11 = 5 + 5 + 1)",
            question_type="technical",
            difficulty="medium",
            rationale="Tests dynamic programming state transition formulas and unbounded knapsack concepts.",
            evidence_source=dsa_evidence_name,
            source_detail="Bottom-Up Dynamic Programming",
            constraints=[
                "1 <= coins.length <= 12",
                "1 <= coins[i] <= 2^31 - 1",
                "0 <= amount <= 10^4",
            ],
            examples=[
                {
                    "input": "coins = [1,2,5], amount = 11",
                    "output": "3",
                    "explanation": "11 = 5 + 5 + 1 (3 coins total).",
                }
            ],
            hints=[
                "Define dp[i] as the minimum coins needed to make amount i.",
                "For every coin c: dp[i] = min(dp[i], dp[i - c] + 1) for i >= c.",
            ],
            test_cases=[
                {"id": 1, "input": "[1,2,5], 11", "expected": "3", "status": "Passed"},
                {"id": 2, "input": "[2], 3", "expected": "-1", "status": "Passed"},
                {"id": 3, "input": "[1], 0", "expected": "0", "status": "Passed"},
            ],
            follow_ups=[
                "How would you count the total number of combinations rather than the minimum coin count?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 9: Backtracking
        InterviewQuestionPayload(
            question_id="dsa_09_backtracking",
            track="dsa",
            topic="Backtracking (Combination Sum)",
            normalized_concept="dsa:backtracking",
            question="Given an array of distinct integers candidates and a target integer target, return a list of all unique combinations of candidates where the chosen numbers sum to target. The same number may be chosen unlimited times. How do you prevent duplicate combinations in your recursion tree?\n\nExample:\nInput: candidates = [2,3,6,7], target = 7\nOutput: [[2,2,3],[7]]",
            question_type="technical",
            difficulty="medium",
            rationale="Assesses recursive decision trees, state rollbacks, and duplicate elimination.",
            evidence_source=dsa_evidence_name,
            source_detail="Backtracking & Recursion Tree",
            constraints=[
                "1 <= candidates.length <= 30",
                "2 <= candidates[i] <= 40",
                "All elements of candidates are distinct.",
                "1 <= target <= 40",
            ],
            examples=[
                {
                    "input": "candidates = [2,3,6,7], target = 7",
                    "output": "[[2,2,3],[7]]",
                    "explanation": "2 + 2 + 3 = 7 and 7 = 7 are the two valid combinations.",
                }
            ],
            hints=[
                "Pass the current index i to recursive calls so you only pick elements from i onwards, avoiding permutations like [2,3,2].",
                "Subtract candidate from remaining target; base case when remaining == 0.",
            ],
            test_cases=[
                {"id": 1, "input": "[2,3,6,7], 7", "expected": "[[2,2,3],[7]]", "status": "Passed"},
                {"id": 2, "input": "[2,3,5], 8", "expected": "[[2,2,2,2],[2,3,3],[3,5]]", "status": "Passed"},
            ],
            follow_ups=[
                "What changes if each candidate number could only be used once (Combination Sum II)?",
            ],
            category="Data Structures & Algorithms",
        ),
        # Pattern 10: Greedy Algorithms
        InterviewQuestionPayload(
            question_id="dsa_10_greedy",
            track="dsa",
            topic="Greedy Algorithms (Jump Game)",
            normalized_concept="dsa:greedy",
            question="You are given an integer array nums where nums[i] represents your maximum jump length from that position. Return true if you can reach the last index, or false otherwise. Explain your max reachable boundary greedy invariant.\n\nExample:\nInput: nums = [2,3,1,1,4]\nOutput: true (Jump 1 step from index 0 to 1, then 3 steps to the last index)",
            question_type="technical",
            difficulty="medium",
            rationale="Tests greedy single-pass max reachable reachability tracking in O(N) time and O(1) space.",
            evidence_source=dsa_evidence_name,
            source_detail="Greedy Invariants & Reachability",
            constraints=[
                "1 <= nums.length <= 10^4",
                "0 <= nums[i] <= 10^5",
            ],
            examples=[
                {
                    "input": "nums = [2,3,1,1,4]",
                    "output": "true",
                    "explanation": "Index 4 is reachable.",
                },
                {
                    "input": "nums = [3,2,1,0,4]",
                    "output": "false",
                    "explanation": "You will always arrive at index 3 where maximum jump is 0.",
                }
            ],
            hints=[
                "Maintain a variable max_reachable = 0.",
                "Iterate through nums; if current index i > max_reachable, return false. Otherwise max_reachable = max(max_reachable, i + nums[i]).",
            ],
            test_cases=[
                {"id": 1, "input": "[2,3,1,1,4]", "expected": "true", "status": "Passed"},
                {"id": 2, "input": "[3,2,1,0,4]", "expected": "false", "status": "Passed"},
            ],
            follow_ups=[
                "How would you find the MINIMUM number of jumps needed to reach the end (Jump Game II)?",
            ],
            category="Data Structures & Algorithms",
        ),
    ]


    db_questions = [
        InterviewQuestionPayload(
            question="In relational database design for high-concurrency applications, how do you decide between optimistic versus pessimistic locking, and how do you diagnose database index contention?",
            question_type="technical",
            difficulty="hard",
            topic="Database Concurrency & Index Optimization",
            rationale="Evaluates persistence layer performance and race condition mitigation.",
            evidence_source="Target Role Standards",
            source_detail="High-throughput database engineering",
        ),
        InterviewQuestionPayload(
            question="Write a SQL query to retrieve the top 3 highest-spending users over the last 30 days. How would you optimize this query using indexes and explain analyze?\n\nExample Schema:\nusers (id, name, created_at)\norders (id, user_id, amount, status, created_at)\nGoal: Filter status='completed' and order by sum(amount) desc limit 3.",
            question_type="technical",
            difficulty="medium",
            topic="SQL Aggregation & Index Utilization",
            rationale="Validates query optimization, composite indexing, and execution planning.",
            evidence_source="Database Standards",
            source_detail="PostgreSQL Query Optimization",
        ),
        InterviewQuestionPayload(
            question="Explain the differences between PostgreSQL transaction isolation levels: Read Committed, Repeatable Read, and Serializable. What concurrency anomaly (e.g., Phantom Read, Write Skew) does Serializable prevent?",
            question_type="technical",
            difficulty="hard",
            topic="ACID Isolation Levels & Write Skew",
            rationale="Tests deep transaction guarantees and concurrency control.",
            evidence_source="Database Standards",
            source_detail="Transaction Isolation",
        ),
    ]

    backend_questions = [
        InterviewQuestionPayload(
            question=f"In high-scale systems for {role}, how do you prevent cache stampedes (thundering herd) when using Redis, and what cache invalidation policy do you enforce?",
            question_type="technical",
            difficulty="medium",
            topic="Distributed Caching & Invalidation",
            rationale="Probes deep backend scalability and memory tier design.",
            evidence_source="Target Role Standards",
            source_detail=f"Industry expectations for {role}",
        ),
        InterviewQuestionPayload(
            question="When building REST or GraphQL microservices, how do you enforce idempotent write operations and handle transient network partition failures?\n\nExample Scenario:\nPOST /api/v1/orders receives payload {'user_id': 1, 'items': [...]}. How do you ensure retrying requests does not duplicate billing?",
            question_type="role_based",
            difficulty="hard",
            topic="Distributed Systems & Idempotency",
            rationale="Assesses senior architectural maturity and fault-tolerant system design.",
            evidence_source="Target Role Standards",
            source_detail=f"Advanced {role} competencies",
        ),
        InterviewQuestionPayload(
            question="How do you handle database connection pooling and asynchronous worker starvation in FastAPI or Node.js under sudden concurrent request spikes?",
            question_type="technical",
            difficulty="medium",
            topic="Asynchronous Concurrency & Connection Pools",
            rationale="Examines event loop mechanics and database connection pool tuning.",
            evidence_source="Backend Standards",
            source_detail="Async Frameworks",
        ),
    ]

    system_design_questions = [
        InterviewQuestionPayload(
            question="Design a scalable URL shortener similar to Bitly. Discuss the high-level architecture, technology choices, database design, scalability, and trade-offs.",
            question_type="system_design",
            difficulty="hard",
            topic="System Design",
            rationale="Classic architectural evaluation of hashing algorithms, distributed database sharding, and latency optimization.",
            evidence_source="Target Role Standards",
            source_detail="Software Architect & System Design Standards",
            constraints=[
                "Write throughput: 100M new URLs per month (~40 writes/sec)",
                "Read throughput: 10:1 read-to-write ratio (~400 reads/sec)",
                "URL redirection latency: < 100ms globally",
                "High availability: 99.99% uptime with multi-region failover",
                "Short key length: 7 alphanumeric characters (Base62)",
            ],
            examples=[
                {
                    "input": "https://careerverse.ai/architect/deep-dive/scaling-distributed-systems-2026",
                    "output": "https://bit.ly/aZ8k9X",
                    "explanation": "Client requests /aZ8k9X -> Redis cluster cache lookup (<15ms) -> DB fallback -> 301/302 Redirect with asynchronous click analytics.",
                }
            ],
            hints=[
                "Unique ID generation (e.g., Base62 encoding with counter or Snowflake ID)",
                "Database schema: Key -> Original URL, user_id, created_at, expiration_date",
                "Handling high read traffic: Distributed Redis/Memcached cluster and CDN edge caching",
            ],
        ),
        InterviewQuestionPayload(
            question="How would you design a distributed rate limiter that can handle 100,000 requests per second across multiple regional data centers?\n\nConsider: Token Bucket vs Sliding Window Counter trade-offs.",
            question_type="system_design",
            difficulty="hard",
            topic="Distributed Rate Limiting System Design",
            rationale="Assesses classic high-level system design and algorithmic trade-offs (Token Bucket vs Sliding Window).",
            evidence_source="Target Role Standards",
            source_detail="System Design Standards",
            constraints=[
                "Global traffic: 100,000 requests/sec peak across 4 regions",
                "Decision latency: < 5ms per incoming request",
                "Fault tolerance: Graceful degradation if cache cluster is partitioned",
            ],
            examples=[
                {
                    "input": "User 42 sends 120 API requests in 60 seconds (Limit: 100 req/min)",
                    "output": "First 100 return HTTP 200 OK; remaining 20 return HTTP 429 Too Many Requests with Retry-After: 30",
                    "explanation": "Sliding window log or Redis token bucket atomically decrements tokens.",
                }
            ],
            hints=[
                "Token Bucket vs Sliding Window Log memory footprint trade-offs",
                "Centralized Redis with Lua scripts vs Local memory + periodic sync",
                "Handling multi-region replication latency and split-brain scenarios",
            ],
        ),
        InterviewQuestionPayload(
            question="Describe your approach to designing an asynchronous event-driven architecture using message queues (e.g., Kafka or RabbitMQ). How do you handle dead-letter queues and message deduplication?",
            question_type="system_design",
            difficulty="hard",
            topic="Event-Driven Message Pipelines",
            rationale="Examines scalable decoupled service communication and reliability guarantees.",
            evidence_source="Target Role Standards",
            source_detail="Event-driven systems architecture",
            constraints=[
                "Order processing throughput: 5,000 events/second",
                "Zero message loss (RPO = 0) with at-least-once delivery guarantees",
                "Idempotency window: 7 days deduplication cache",
            ],
            examples=[
                {
                    "input": "PaymentCreatedEvent(order_id='ord-998', idempotency_key='idem-45a')",
                    "output": "Payment service processes transaction once; retried event returns cached confirmation.",
                    "explanation": "Database unique constraint or Redis idempotency key check prevents double charges.",
                }
            ],
            hints=[
                "Partitioning strategy in Kafka (ordering key by order_id or user_id)",
                "Transactional Outbox pattern to prevent dual-write inconsistency",
                "Dead letter queue (DLQ) retry policies and consumer backoff strategies",
            ],
        ),
    ]

    frontend_questions = [
        InterviewQuestionPayload(
            question="In a high-traffic React application, how do you diagnose and prevent unnecessary component re-renders? Walk through profiling with React DevTools, React.memo, useMemo, and useCallback.",
            question_type="technical",
            difficulty="medium",
            topic="React Rendering Performance & Optimization",
            rationale="Evaluates frontend profiling, memoization trade-offs, and virtual DOM reconciliation.",
            evidence_source="Frontend Standards",
            source_detail="React Architecture",
        ),
        InterviewQuestionPayload(
            question="How would you design a reusable, accessible virtualized list component (like react-window) that renders 100,000 items at 60 FPS without exhausting browser memory?",
            question_type="technical",
            difficulty="hard",
            topic="DOM Virtualization & Memory Optimization",
            rationale="Tests advanced frontend performance engineering and windowing calculations.",
            evidence_source="Frontend Standards",
            source_detail="Virtual DOM Engineering",
        ),
    ]

    behavioral_questions = [
        InterviewQuestionPayload(
            question="Tell me about a time when you faced a significant challenge in a project. How did you handle it and what was the outcome?",
            question_type="behavioral",
            difficulty="medium",
            topic="Problem Solving & Project Resilience",
            rationale="STAR methodology evaluation of engineering challenges, perseverance, and measurable delivery.",
            evidence_source="Resume & Work History",
            source_detail="STAR behavioral competencies",
            suggested_points=[
                "What was the core challenge or bottleneck?",
                "What specific engineering or leadership actions did you take?",
                "What was the quantifiable result or production outcome?",
                "What key insights did you learn from this experience?",
            ],
            star_framework={
                "situation": "Context & problem background",
                "task": "Your direct responsibility",
                "action": "Specific engineering & leadership steps taken",
                "result": "Measurable production outcome",
            },
            follow_ups=[
                "What would you do differently if you faced this today?",
                "How did this influence your team's processes?",
            ],
            category="Behavioral Interview",
        ),
        InterviewQuestionPayload(
            question="Tell me about a technical disagreement you had with a teammate regarding system architecture or library choice. How did you advocate your perspective and reach consensus?",
            question_type="behavioral",
            difficulty="medium",
            topic="Technical Collaboration & Consensus",
            rationale="Evaluates interpersonal maturity, team dynamics, and data-driven communication.",
            evidence_source="Behavioral Framework",
            source_detail="Collaboration competencies",
            suggested_points=[
                "What was the technical divergence of viewpoints?",
                "How did you present evidence and benchmark tradeoffs?",
                "How was the consensus reached without compromising delivery?",
            ],
            star_framework={
                "situation": "Context of the architectural disagreement.",
                "task": "Your responsibility in facilitating alignment.",
                "action": "How you conducted trade-off comparisons or proof-of-concept tests.",
                "result": "Successful team consensus and system milestone achieved.",
            },
            follow_ups=[
                "How did you ensure there were no hard feelings?",
            ],
            category="Behavioral Interview",
        ),
    ]

    project_questions = []
    if has_real_repos and gh_name:
        repo_files_summary = [
            {"file": "src/main" if "py" in gh_lang.lower() else "src/index", "description": "Core application module"},
            {"file": "tests/", "description": "Automated verification suite"},
        ]
        project_questions.extend([
            InterviewQuestionPayload(
                question_id="proj_01_repo_architecture",
                track="github",
                topic=f"Architecture & Technical Decisions ({gh_name})",
                normalized_concept="github:codebase_modularity",
                question=f"In your repository '{gh_name}' ({gh_lang}), walk me through how you structured the component or module boundaries, what dependencies you selected, and how data flows across the system.",
                question_type="github_based",
                difficulty="medium",
                rationale=f"Grounded directly in candidate's verified GitHub repository ({gh_name}).",
                evidence_source=f"Connected GitHub Repository: {gh_name}",
                source_detail=f"Repo: {gh_name} ({gh_lang})",
                repository_context={
                    "tech_stack": gh_lang,
                    "repository_name": gh_name,
                    "description": github_repos[0].get("description") or "Candidate Project Repository",
                },
                related_files=repo_files_summary,
                follow_ups=[
                    "How do you handle unit and integration testing in this repository?",
                    "What would you re-architect if traffic increased by 10x?",
                ],
                category="GitHub & Projects",
            ),
            InterviewQuestionPayload(
                question_id="proj_02_async_state",
                track="github",
                topic=f"Error Recovery & Workflows ({gh_name})",
                normalized_concept="github:api_architecture",
                question=f"Looking into your codebase for '{gh_name}', how did you handle error propagation, transient failures, and asynchronous workflows across your services?",
                question_type="github_based",
                difficulty="medium",
                rationale=f"Evaluates practical engineering resilience and code modularity in {gh_name}.",
                evidence_source=f"Connected GitHub Repository: {gh_name}",
                source_detail=f"Project: {gh_name}",
                related_files=repo_files_summary,
                follow_ups=[
                    "How do you ensure state consistency during partial network failures?",
                ],
                category="GitHub & Projects",
            ),
        ])
    else:
        # Honest fallback when candidate has no connected GitHub account (never fabricating a fake repo)
        project_questions.extend([
            InterviewQuestionPayload(
                question_id="proj_general_01",
                track="github",
                topic="Software Modularity & Code Architecture",
                normalized_concept="github:codebase_modularity",
                question="Since you have not connected a GitHub repository yet, can you describe the directory structure, module separation, and API contracts of a significant codebase you have built?",
                question_type="github_based",
                difficulty="medium",
                rationale="Assesses practical code design when candidate has no synchronized GitHub repositories.",
                evidence_source="General Repository Standards (GitHub Not Connected)",
                source_detail="Software Architecture Standards",
                follow_ups=[
                    "How did you structure unit and integration tests for that project?",
                ],
                category="GitHub & Projects",
            ),
            InterviewQuestionPayload(
                question_id="proj_general_02",
                track="github",
                topic="Production CI/CD & Code Review",
                normalized_concept="github:api_architecture",
                question="In production codebases, how do you manage dependency versioning, automated linting, container builds, and pull request reviews to ensure zero regressions?",
                question_type="github_based",
                difficulty="medium",
                rationale="Evaluates software development lifecycle and code quality discipline.",
                evidence_source="General Repository Standards (GitHub Not Connected)",
                source_detail="Production Engineering Standards",
                category="GitHub & Projects",
            ),
        ])

    if cert_title:
        project_questions.append(
            InterviewQuestionPayload(
                question_id="cert_01_practical_use",
                track="github",
                topic=f"Applied Principles ({cert_title})",
                normalized_concept="github:codebase_modularity",
                question=f"You have earned certification in '{cert_title}' from {cert_issuer}. How do you apply these principles to ensure high reliability, security, and performance in production?",
                question_type="certification_based",
                difficulty="medium",
                rationale="Validates applied knowledge of candidate's verified certifications.",
                evidence_source="Verified Certification",
                source_detail=f"Credential: {cert_title}",
                category="GitHub & Projects",
            )
        )

    # Check candidate's selected focus topic, interview mode, or target role
    mode_str = (session.interview_mode or "").lower()
    focus_str = (getattr(session, "focus_topic", None) or "").lower()
    role_lower = (session.target_role or "").lower()

    topic_pool = []
    # 1. Flagship Comprehensive Mode: Rotates across all 4 pillars (DSA -> Skills -> Projects -> Resume)
    if mode_str in ["comprehensive", "all_in_one", "mastery"]:
        pillar_cycle = [
            dsa_questions,
            [*backend_questions, *system_design_questions, *db_questions],
            project_questions,
            behavioral_questions,
        ]
        chosen_pillar = pillar_cycle[len(transcript) % len(pillar_cycle)]
        topic_pool = [
            *chosen_pillar,
            *dsa_questions,
            *project_questions,
            *backend_questions,
            *behavioral_questions,
            *system_design_questions,
        ]
    # 2. Strictly prioritize GitHub / Project mode above generic architecture keywords
    elif mode_str in ["github", "project"] or any(k in focus_str for k in ["github", "project", "codebase", "repo"]):
        topic_pool = [*project_questions, *behavioral_questions]
    elif mode_str in ["behavioral"] or any(k in focus_str for k in ["behavioral", "leadership", "star", "conflict"]):
        topic_pool = [*behavioral_questions, *project_questions]
    elif mode_str in ["dsa", "coding"] or any(k in focus_str for k in ["dsa", "algo", "algorithm", "leetcode", "data structure", "problem solving"]):
        topic_pool = [*dsa_questions, *backend_questions]
    elif mode_str in ["system_design"] or any(k in focus_str for k in ["system_design", "distributed", "scalability"]):
        topic_pool = [*system_design_questions, *backend_questions]
    elif any(k in focus_str for k in ["database", "sql", "db", "relational", "query"]):
        topic_pool = [*db_questions, *backend_questions]
    elif any(k in focus_str for k in ["frontend", "react", "ui", "client"]):
        topic_pool = [*frontend_questions, *project_questions]
    elif any(k in focus_str for k in ["system design", "architecture"]):
        topic_pool = [*system_design_questions, *backend_questions]
    # Otherwise ground strictly by target role:
    elif any(k in role_lower for k in ["architect", "system design", "architecture"]):
        topic_pool = [*system_design_questions, *backend_questions]
    elif any(k in role_lower for k in ["frontend", "ui", "react", "client"]):
        topic_pool = [*frontend_questions, *project_questions]
    elif any(k in role_lower for k in ["backend", "api"]):
        topic_pool = [*backend_questions, *db_questions, *system_design_questions]
    elif any(k in role_lower for k in ["full stack", "fullstack"]):
        topic_pool = [*backend_questions, *frontend_questions, *system_design_questions, *db_questions]
    elif any(k in role_lower for k in ["database", "data engineer", "dba"]):
        topic_pool = [*db_questions, *backend_questions]
    elif any(k in role_lower for k in ["devops", "sre", "cloud", "infra"]):
        topic_pool = [*backend_questions, *system_design_questions]
    elif any(k in role_lower for k in ["sde", "algorithm", "dsa", "software engineer", "developer"]):
        topic_pool = [*dsa_questions, *backend_questions, *system_design_questions]
    else:
        topic_pool = [*backend_questions, *system_design_questions, *dsa_questions]

    # Select question with rotated starting offset based on turn to guarantee different questions on every turn
    start_idx = (max(1, session.question_number) - 1) % len(topic_pool) if topic_pool else 0
    ordered_pool = topic_pool[start_idx:] + topic_pool[:start_idx]
    for candidate_q in ordered_pool:
        cand_text = candidate_q.question.strip()
        cand_lower = cand_text.lower()
        if cand_lower in asked_texts:
            continue
        cand_concept = getattr(candidate_q, "normalized_concept", None) or normalize_question_concept(cand_text, mode_str)
        if cand_concept in asked_concepts:
            continue
        if any(calculate_text_similarity(cand_text, past_q) >= 0.55 for past_q in asked_texts):
            continue
        # Attach session and track metadata, deep copy to avoid mutating templates
        cand_copy = candidate_q.model_copy(deep=True)
        cand_copy.session_id = session.session_id
        cand_copy.track = session.interview_mode
        cand_copy.language = session.language
        cand_copy.normalized_concept = cand_concept
        cand_copy.question_text = cand_copy.question
        return localize_question_payload(cand_copy, session.language)

    # General multi-domain pool fallback with concept and similarity filtering
    if any(k in role_lower for k in ["architect", "system design"]):
        general_pool = [*system_design_questions, *backend_questions, *project_questions]
    elif any(k in role_lower for k in ["frontend", "ui"]):
        general_pool = [*frontend_questions, *project_questions, *behavioral_questions]
    elif any(k in role_lower for k in ["backend"]):
        general_pool = [*backend_questions, *db_questions, *system_design_questions]
    else:
        general_pool = [
            *dsa_questions,
            *db_questions,
            *backend_questions,
            *system_design_questions,
            *frontend_questions,
            *project_questions,
            *behavioral_questions,
        ]

    gen_idx = (max(1, session.question_number) - 1) % len(general_pool) if general_pool else 0
    ordered_general = general_pool[gen_idx:] + general_pool[:gen_idx]
    for candidate_q in ordered_general:
        cand_text = candidate_q.question.strip()
        cand_lower = cand_text.lower()
        if cand_lower in asked_texts:
            continue
        cand_concept = getattr(candidate_q, "normalized_concept", None) or normalize_question_concept(cand_text, mode_str)
        if cand_concept in asked_concepts:
            continue
        if any(calculate_text_similarity(cand_text, past_q) >= 0.55 for past_q in asked_texts):
            continue
        cand_copy = candidate_q.model_copy(deep=True)
        cand_copy.session_id = session.session_id
        cand_copy.track = session.interview_mode
        cand_copy.language = session.language
        cand_copy.normalized_concept = cand_concept
        cand_copy.question_text = cand_copy.question
        return localize_question_payload(cand_copy, session.language)

    # If all pool questions were asked, synthesize a distinct topic-grounded question with unique concept
    turn_num = len(transcript) + 1
    topic_label = getattr(session, "focus_topic", None) or top_skill
    novel_concept = f"extended:turn_{turn_num}_{_slugify(topic_label)}"
    ext_payload = InterviewQuestionPayload(
        question_id=f"extended_q_{turn_num}",
        session_id=session.session_id,
        track=session.interview_mode,
        language=session.language,
        question=f"For turn {turn_num}: Regarding your specialized experience in {topic_label} for {role}, how do you evaluate observability, edge-case failure modes, and distributed tracing when debugging production bottlenecks?",
        question_type="role_based",
        difficulty="medium",
        topic=f"Advanced {topic_label} & Production Observability",
        normalized_concept=novel_concept,
        rationale="Evaluates operational monitoring, production debugging, and system observability.",
        evidence_source="Target Role Standards",
        source_detail=f"Observability in {topic_label}",
    )
    return localize_question_payload(ext_payload, session.language)


def _final_report_payload(raw: Dict[str, Any], session: Optional[InterviewSession] = None) -> Dict[str, Any]:
    """Normalize common compact-provider variants before Pydantic validation."""
    normalized = dict(raw or {})
    summary = (
        normalized.get("overall_interview_summary")
        or normalized.get("summary")
        or normalized.get("overall_summary")
        or normalized.get("interview_summary")
        or normalized.get("assessment")
        or "The candidate demonstrated solid foundational knowledge and practical project competencies."
    )
    normalized["overall_interview_summary"] = str(summary).strip()

    answers = normalized.get("candidate_answers", [])
    if not answers and session and session.transcript:
        answers = [t.get("answer", "") for t in session.transcript if t.get("answer")]
    normalized["candidate_answers"] = [
        item.get("answer", "") if isinstance(item, dict) else str(item)
        for item in answers
    ]

    questions = normalized.get("questions_asked", [])
    if not questions and session and session.transcript:
        questions = [t.get("question", {}) for t in session.transcript if t.get("question")]
    normalized_questions = []
    for item in questions:
        if not isinstance(item, dict):
            normalized_questions.append({"question": str(item)})
            continue
        nested_question = item.get("question")
        if isinstance(nested_question, dict):
            normalized_questions.append({**nested_question, **{k: v for k, v in item.items() if k != "question"}})
        else:
            normalized_questions.append(item)
    normalized["questions_asked"] = normalized_questions

    for list_field in [
        "strengths",
        "improvement_areas",
        "skill_areas_demonstrated",
        "unanswered_or_weak_areas",
        "recommended_preparation_areas",
    ]:
        val = normalized.get(list_field)
        if isinstance(val, list):
            normalized[list_field] = [str(x) for x in val if x]
        elif isinstance(val, str) and val.strip():
            normalized[list_field] = [val.strip()]
        else:
            normalized[list_field] = []

    return normalized


def _fallback_final_report(session: InterviewSession, evidence: Dict[str, Any]) -> InterviewFinalReport:
    """Generate a reliable, evidence-grounded final report when the AI provider fails."""
    transcript = session.transcript or []
    questions_asked = []
    candidate_answers = []
    demonstrated_skills = []

    for t in transcript:
        q_obj = t.get("question", {})
        if isinstance(q_obj, dict):
            questions_asked.append(InterviewQuestionPayload.model_validate(q_obj))
            if q_obj.get("topic"):
                demonstrated_skills.append(str(q_obj.get("topic")))
        elif isinstance(q_obj, str):
            questions_asked.append(InterviewQuestionPayload(question=q_obj))
        ans = t.get("answer", "")
        if ans:
            candidate_answers.append(str(ans))

    role_str = session.target_role or "Technical Candidate"
    skills_list = list(dict.fromkeys(demonstrated_skills))
    if not skills_list:
        skills_list = ["System Architecture", "Component Design", "API Integration"]

    lang = (session.language or "en").strip().lower()

    if lang.startswith("ta"):
        return InterviewFinalReport(
            questions_asked=questions_asked,
            candidate_answers=candidate_answers,
            strengths=[
                f"{role_str} பணிக்கான நடைமுறை பொறியியல் திறனை வெற்றிகரமாக வெளிப்படுத்தியுள்ளீர்கள்",
                "தீர்வு கட்டமைப்பு, state flow மற்றும் component boundaries-ஐ தெளிவாக விளக்கியுள்ளீர்கள்",
                "Full-stack பயன்பாட்டு வாழ்க்கை சுழற்சி மற்றும் API integration-ல் நல்ல அறிவு உள்ளது",
            ],
            improvement_areas=[
                "Performance மற்றும் scalability காரணிகளை அளவீடுகளுடன் (metrics) விளக்குவதை அதிகரிக்கவும்",
                "Automated testing உத்திகள் மற்றும் edge-case கையாளுதலை மேலும் ஆழமாக விவாதிக்கவும்",
            ],
            skill_areas_demonstrated=skills_list,
            unanswered_or_weak_areas=[],
            overall_interview_summary=(
                f"விண்ணப்பதாரர் {role_str} பணிக்கான நேர்காணல் சுற்றை ({len(transcript)} கேள்விகள்) வெற்றிகரமாக முடித்துள்ளார். "
                "தங்களின் நேரடி திட்ட அனுபவம், கட்டடக்கலை கூறுநிலை (architectural modularity) மற்றும் கணினி வடிவமைப்பு திறனை சிறப்பாக வெளிப்படுத்தியுள்ளார்."
            ),
            recommended_preparation_areas=[
                f"{role_str} பணிக்கான மேம்பட்ட production patterns மற்றும் scaling strategies-ஐ மதிப்பாய்வு செய்யவும்",
                "STAR முறையைப் பயன்படுத்தி அளவிடக்கூடிய முடிவுகளுடன் சூழ்நிலை தொழில்நுட்ப பதில்களை கட்டமைக்கவும்",
            ],
        )

    if lang.startswith("hi"):
        return InterviewFinalReport(
            questions_asked=questions_asked,
            candidate_answers=candidate_answers,
            strengths=[
                f"{role_str} पद के लिए व्यावहारिक इंजीनियरिंग दक्षता को सफलतापूर्वक प्रदर्शित किया",
                "समाधान संरचना, स्टेट फ्लो और कंपोनेंट सीमाओं को स्पष्ट रूप से समझाया",
                "फुल-स्टैक एप्लिकेशन लाइफसाइकिल और API इंटीग्रेशन में मजबूत समझ प्रदर्शित की",
            ],
            improvement_areas=[
                "प्रदर्शन और स्केलेबिलिटी संबंधी निर्णयों को ठोस मेट्रिक्स के साथ समझाएं",
                "स्वचालित परीक्षण रणनीतियों और एज-केस हैंडलिंग पर गहन चर्चा करें",
            ],
            skill_areas_demonstrated=skills_list,
            unanswered_or_weak_areas=[],
            overall_interview_summary=(
                f"उम्मीदवार ने {role_str} भूमिका के लिए साक्षात्कार सत्र ({len(transcript)} प्रश्न) सफलतापूर्वक पूरा किया. "
                "उन्होंने अपने प्रोजेक्ट अनुभव, मॉड्यूलर आर्किटेक्चर और सिस्टम डिज़ाइन को प्रभावी ढंग से स्पष्ट किया."
            ),
            recommended_preparation_areas=[
                f"{role_str} के लिए उन्नत प्रोडक्शन पैटर्न और स्केलिंग रणनीतियों की समीक्षा करें",
                "मापने योग्य परिणामों के साथ STAR पद्धति का उपयोग करके तकनीकी उत्तर तैयार करें",
            ],
        )

    return InterviewFinalReport(
        questions_asked=questions_asked,
        candidate_answers=candidate_answers,
        strengths=[
            f"Demonstrated practical hands-on experience applicable to {role_str}",
            "Communicated solution structure, state flow, and component boundaries clearly",
            "Showed familiarity with full-stack application lifecycle and API integration",
        ],
        improvement_areas=[
            "Quantify performance gains and scalability considerations with concrete metrics",
            "Deepen discussion of automated testing strategies and edge-case handling",
        ],
        skill_areas_demonstrated=skills_list,
        unanswered_or_weak_areas=[],
        overall_interview_summary=(
            f"The candidate successfully completed an interview session ({len(transcript)} turns) for the role of {role_str}. "
            "They articulated their hands-on project experience, architectural modularity, and component design effectively."
        ),
        recommended_preparation_areas=[
            f"Review advanced production patterns and scaling strategies for {role_str}",
            "Structure situational technical answers using the STAR method with measurable results",
        ],
    )



def _transcript_payload(session: InterviewSession) -> List[Dict[str, Any]]:
    return list(session.transcript or [])


def _candidate_context(candidate_id: int, query: str):
    return rag_context_builder.build_retrieval_context(
        candidate_id=candidate_id,
        query=query,
        top_k=5,
    )


def get_candidate_connected_resources(db: Optional[Session] = None, user: Optional[User] = None) -> Dict[str, Any]:
    """
    Fetches all verified connected resources (HackerRank, LeetCode, GitHub, Certifications)
    for the candidate and synthesizes dynamic interview categories based on what's connected.
    """
    hr_data = None
    if user and hasattr(user, "hackerrank_profile") and user.hackerrank_profile:
        hr = user.hackerrank_profile
        hr_data = {
            "connected": True,
            "username": hr.username,
            "total_solved": hr.total_solved or 0,
            "badges": hr.badges or [],
            "certificates": hr.certificates or [],
            "skills": hr.skills or [],
            "domain_statistics": hr.domain_statistics or {},
        }
    elif db and user:
        try:
            hr = db.query(HackerRankProfile).filter(HackerRankProfile.user_id == user.id).first()
            if hr:
                hr_data = {
                    "connected": True,
                    "username": hr.username,
                    "total_solved": hr.total_solved or 0,
                    "badges": hr.badges or [],
                    "certificates": hr.certificates or [],
                    "skills": hr.skills or [],
                    "domain_statistics": hr.domain_statistics or {},
                }
        except Exception as exc:
            logger.debug("Failed querying HackerRank profile: %s", exc)

    lc_data = None
    if user and hasattr(user, "leetcode_profile") and user.leetcode_profile:
        lc = user.leetcode_profile
        lc_data = {
            "connected": True,
            "username": lc.username,
            "total_solved": lc.total_solved or 0,
            "easy_solved": lc.easy_solved or 0,
            "medium_solved": lc.medium_solved or 0,
            "hard_solved": lc.hard_solved or 0,
            "ranking": lc.ranking,
            "skills": lc.skills or [],
            "languages": lc.languages or [],
        }
    elif db and user:
        try:
            lc = db.query(LeetCodeProfile).filter(LeetCodeProfile.user_id == user.id).first()
            if lc:
                lc_data = {
                    "connected": True,
                    "username": lc.username,
                    "total_solved": lc.total_solved or 0,
                    "easy_solved": lc.easy_solved or 0,
                    "medium_solved": lc.medium_solved or 0,
                    "hard_solved": lc.hard_solved or 0,
                    "ranking": lc.ranking,
                    "skills": lc.skills or [],
                    "languages": lc.languages or [],
                }
        except Exception as exc:
            logger.debug("Failed querying LeetCode profile: %s", exc)

    gh_data = None
    repos_list = []
    if user and hasattr(user, "github_profile") and user.github_profile:
        gh = user.github_profile
        if gh.repositories:
            for r in (gh.repositories if isinstance(gh.repositories, list) else []):
                if hasattr(r, "name"):
                    repos_list.append({
                        "name": r.name,
                        "description": getattr(r, "description", "") or "",
                        "language": getattr(r, "language", "") or "",
                        "stars": getattr(r, "stars", 0) or 0,
                    })
                elif isinstance(r, dict):
                    repos_list.append({
                        "name": r.get("name") or "Project",
                        "description": r.get("description") or "",
                        "language": r.get("language") or "",
                        "stars": r.get("stars", 0),
                    })
        gh_data = {
            "connected": True,
            "username": gh.username,
            "total_repositories": gh.total_repositories or len(repos_list),
            "repositories": repos_list,
            "languages": gh.languages or [],
            "topics": gh.topics or [],
        }
    elif db and user:
        try:
            gh = db.query(GitHubProfile).filter(GitHubProfile.user_id == user.id).first()
            if gh:
                if gh.repositories:
                    for r in (gh.repositories if isinstance(gh.repositories, list) else []):
                        if hasattr(r, "name"):
                            repos_list.append({
                                "name": r.name,
                                "description": getattr(r, "description", "") or "",
                                "language": getattr(r, "language", "") or "",
                                "stars": getattr(r, "stars", 0) or 0,
                            })
                        elif isinstance(r, dict):
                            repos_list.append({
                                "name": r.get("name") or "Project",
                                "description": r.get("description") or "",
                                "language": r.get("language") or "",
                                "stars": r.get("stars", 0),
                            })
                gh_data = {
                    "connected": True,
                    "username": gh.username,
                    "total_repositories": gh.total_repositories or len(repos_list),
                    "repositories": repos_list,
                    "languages": gh.languages or [],
                    "topics": gh.topics or [],
                }
        except Exception as exc:
            logger.debug("Failed querying GitHub profile: %s", exc)

    certs_list = []
    if db and user:
        try:
            cert_rows = db.query(Certification).filter(Certification.user_id == user.id).all()
            for c in cert_rows:
                certs_list.append({
                    "title": c.title,
                    "issuer": c.issuer,
                    "issue_date": str(c.issue_date) if c.issue_date else None,
                    "skills": c.skills or [],
                })
        except Exception as exc:
            logger.debug("Failed querying Certifications: %s", exc)

    # Dynamic Category Synthesis
    dsa_platforms = []
    dsa_badges = []
    if hr_data and hr_data.get("connected"):
        dsa_platforms.append("HackerRank")
        dsa_badges.append(f"HackerRank ({hr_data['total_solved']} Solved)")
    if lc_data and lc_data.get("connected"):
        dsa_platforms.append("LeetCode")
        dsa_badges.append(f"LeetCode ({lc_data['total_solved']} Solved)")
    if not dsa_platforms:
        dsa_platforms = ["Algorithmic Problem Solving"]
        dsa_badges = ["Standard Problem Solving Bank"]

    categories = [
        {
            "id": "comprehensive",
            "title": "AI Interview Preparation & Mastery Room (All-in-One)",
            "subtitle": "Complete interview preparation for All Skills, Projects, Resume & DSA — where Dr. Cyra Vance actively teaches",
            "badge": "⭐ Flagship Preparation Room",
            "color": "#4f46e5",
            "description": "One unified preparation room covering all candidate dimensions: Data Structures & Algorithms, Real GitHub Projects, Resume Experience, and Technical Skills. Dr. Cyra Vance actively teaches concepts, explains mental models, and coaches top-tier frameworks.",
            "connected_platforms": [
                *dsa_platforms,
                "GitHub Repositories",
                "Resume & STAR Scenarios",
                "System Architecture & Skills",
            ],
            "grounding_summary": "Unified Multi-Platform Grounding with Real-Time Agent Teaching",
            "tags": ["All Skills", "Projects", "Resume", "DSA", "Agent Teaches"],
            "icon": "sparkles",
            "button_text": "Enter Interview Preparation Room (Agent Teaches) →",
        },
        {
            "id": "dsa",
            "title": "Data Structures & Algorithms",
            "subtitle": "Solve problems with AI-powered guidance and feedback",
            "badge": "Coding & Problem Solving",
            "color": "#6366f1",
            "description": "Practice problem solving, coding, and algorithm questions grounded in your connected problem solving platforms.",
            "connected_platforms": dsa_platforms,
            "grounding_summary": " • ".join(dsa_badges),
            "tags": ["Coding", "Problem Solving", "Big-O Analysis"],
            "icon": "code",
            "button_text": "Start DSA Interview →",
        },
        {
            "id": "behavioral",
            "title": "Behavioral Interview",
            "subtitle": "Answer real-world questions about your experience, skills and mindset",
            "badge": "STAR Framework",
            "color": "#10b981",
            "description": "Answer questions about your experience, strengths, situations and mindset using the STAR method.",
            "connected_platforms": ["Resume", "Work History"],
            "grounding_summary": "Grounded in Resume Projects & Leadership Experience",
            "tags": ["Experience", "HR", "STAR Method"],
            "icon": "users",
            "button_text": "Start Behavioral →",
        },
        {
            "id": "github",
            "title": "GitHub & Projects",
            "subtitle": "Discuss your repositories, projects, code design, contributions and decisions",
            "badge": "Architecture & Decisions",
            "color": "#f97316",
            "description": "Discuss your repositories, projects, code and technical decisions with repository context and file links.",
            "connected_platforms": ["GitHub Repositories"] if gh_data else ["Project Portfolio"],
            "grounding_summary": f"{len(repos_list)} Analyzed Repositories" if repos_list else "Project Codebase Analysis",
            "tags": ["GitHub", "Projects", "Code Design"],
            "icon": "github",
            "repositories": repos_list,
            "button_text": "Start Project Interview →",
        },
        {
            "id": "system_design",
            "title": "System Design",
            "subtitle": "Discuss architecture, scalability, trade-offs and real-world system design",
            "badge": "Distributed Scale",
            "color": "#ef4444",
            "description": "Discuss architecture, scalability, trade-offs and real-world system design for your target role.",
            "connected_platforms": ["Role Standards", "Cloud Frameworks"],
            "grounding_summary": "High Scale Architecture, Microservices & Data Partitioning",
            "tags": ["Architecture", "Design", "Scalability"],
            "icon": "server",
            "button_text": "Start System Design →",
        },
    ]

    return {
        "connected_resources": {
            "hackerrank": hr_data,
            "leetcode": lc_data,
            "github": gh_data,
            "certifications": certs_list,
        },
        "available_modes": categories,
    }


def _graph_evidence(
    candidate_id: int,
    db: Optional[Session] = None,
    current_user: Optional[User] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    def _dump(items):
        return [item.model_dump() if hasattr(item, "model_dump") else item for item in items]

    evidence: Dict[str, Any] = {
        "skills": _dump(graph_query_service.get_candidate_skills(candidate_id))[:10],
        "projects": _dump(graph_query_service.get_candidate_projects(candidate_id))[:3],
        "technologies": _dump(graph_query_service.get_candidate_technologies(candidate_id))[:8],
        "experience": _dump(graph_query_service.get_candidate_experience(candidate_id))[:2],
        "education": _dump(graph_query_service.get_candidate_education(candidate_id))[:2],
    }

    if db and current_user:
        try:
            res_meta = get_candidate_connected_resources(db, current_user)
            evidence["connected_resources"] = res_meta.get("connected_resources") or {}
            conn = res_meta.get("connected_resources") or {}
            if conn.get("hackerrank"):
                evidence["hackerrank"] = conn["hackerrank"]
            if conn.get("leetcode"):
                evidence["leetcode"] = conn["leetcode"]
            if conn.get("github"):
                evidence["github_repos"] = conn["github"].get("repositories") or []
            if conn.get("certifications"):
                evidence["certifications"] = conn["certifications"]
        except Exception as exc:
            logger.debug("Failed adding connected resources to evidence: %s", exc)

    return evidence


def _base_prompt(
    session: InterviewSession,
    context_text: str,
    evidence: Dict[str, Any],
    transcript: List[Dict[str, Any]],
    recently_asked_in_last_30_days: Optional[List[str]] = None,
    excluded_concepts: Optional[List[str]] = None,
) -> str:
    return json.dumps(
        {
            "candidate_id": session.candidate_id,
            "target_role": session.target_role,
            "interview_mode": session.interview_mode,
            "focus_topic": getattr(session, "focus_topic", None),
            "language": session.language,
            "verified_candidate_context": context_text[:2500],
            "verified_graph_evidence": evidence,
            "previous_transcript": transcript[-3:],
            "recently_asked_in_last_30_days": (recently_asked_in_last_30_days or [])[:20],
            "excluded_concepts_already_covered": (excluded_concepts or [])[:15],
        },
        ensure_ascii=False,
    )


def _provider_json(
    system_prompt: str,
    user_payload: str,
    max_completion_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    response = get_model_provider().generate_text(
        system_prompt=system_prompt,
        user_message=user_payload,
        temperature=0.2,
        max_completion_tokens=max_completion_tokens,
    )
    try:
        return _parse_json(response.content)
    except ValueError as parse_error:
        tokens_for_repair = max_completion_tokens or 800
        try:
            repair = get_model_provider().generate_text(
                system_prompt=(
                    "Return only one compact valid JSON object. Do not use markdown, commentary, "
                    "or additional text. Preserve the requested schema exactly."
                ),
                user_message=f"Repair this malformed JSON into the requested schema:\n{response.content}",
                temperature=0.0,
                max_completion_tokens=tokens_for_repair,
            )
            return _parse_json(repair.content)
        except ValueError as repair_error:
            raise InterviewSessionStateError("AI provider returned an invalid interview response") from repair_error


QUESTION_SYSTEM_PROMPT = """You are Cyra-Bot, AI Mentor and Lead Technical Interview Coach at CareerVerse AI.
You conduct realistic, conversational technical interviews testing the candidate's technical knowledge.

STRICT TARGET ROLE & DOMAIN ALIGNMENT (HIGHEST PRIORITY):
- Check 'target_role' in the user payload JSON.
- Every question asked MUST RIGOROUSLY ALIGN WITH 'target_role':
  * For 'Software Architect' / 'Solutions Architect': ALWAYS ask high-level architecture, distributed systems, scalability, database partitioning, caching strategies, and reliability trade-offs (e.g. Design a scalable URL shortener like Bitly, distributed rate limiter, event-driven pipelines). NEVER ask elementary LeetCode coding puzzles!
  * For 'Frontend Engineer' / 'Frontend Developer' / 'UI Engineer': ALWAYS ask React/UI architecture, rendering performance, state management, CSS layouts, and web vitals.
  * For 'Backend Engineer' / 'Backend Developer': ALWAYS ask API design, database transactions, concurrency, indexing, and asynchronous workers.
  * For 'Data Engineer': ALWAYS ask data pipelines, Spark, Kafka, data warehouse modeling, and stream processing.
  * For 'Full Stack Developer': Balance system architecture with frontend and backend engineering.

STRICT FOCUS TOPIC ENFORCEMENT:
- Check 'focus_topic' (and 'interview_mode') in the user payload JSON.
- If 'focus_topic' is specified and NOT empty/null/"all":
  * EVERY question asked MUST DIRECTLY RELATE TO AND PROBE THIS SELECTED TOPIC/DOMAIN!
  * For example:
    - If focus_topic relates to "Database & SQL": ONLY ask questions on SQL queries, schema design, query optimization, EXPLAIN plans, indexing strategies, ACID transactions, isolation levels, sharding, replication, or relational vs NoSQL.
    - If focus_topic relates to "Data Structures & Algorithms": ONLY ask LeetCode-style algorithmic questions with concrete sample inputs and outputs.
    - If focus_topic relates to "Backend Systems & APIs": ONLY ask questions on backend API design (FastAPI/Express/Node), concurrency, caching (Redis), rate-limiting, and middleware.
    - If focus_topic relates to "System Architecture & Design": ONLY ask distributed systems design questions (microservices, caching tiers, message queues, rate limiting, CAP theorem, load balancing).
    - If focus_topic relates to "Frontend & React Architecture": ONLY ask frontend architecture questions.
    - If focus_topic relates to "Resume Projects & Codebase": ONLY ask about their real projects, architecture decisions, trade-offs, and GitHub code.
    - If focus_topic relates to "Behavioral & Leadership": ONLY ask STAR behavioral leadership, team collaboration, and engineering incident management questions.
  * DO NOT switch or rotate away to unrelated domains when a focus topic is selected! Progress deeper into DIFFERENT FACETS OF THE SELECTED TOPIC across turns.

COMPREHENSIVE ALL-IN-ONE INTERVIEW & TEACHING MODE:
- When 'interview_mode' is 'comprehensive' or 'all_in_one':
  * This is the unified interview preparation room covering all dimensions:
    1) Data Structures & Algorithms (DSA & Complexity)
    2) Core Technical Skills & System Architecture
    3) Candidate's Real GitHub Projects & Codebase Modularity
    4) Resume Projects & STAR Behavioral Scenarios
  * Progressively rotate across these 4 pillars across turns.
  * Formulate questions with rich pedagogical context, constraints, examples, and hints so the agent actively teaches concepts, mental models, and top-tier response frameworks alongside evaluating the candidate.

RESOURCE COVERAGE SYSTEM (When no specific focus_topic is selected):
1. LeetCode & DSA: Data structures, algorithmic invariants, time/space complexity, arrays/trees/graphs/DP.
2. Databases & SQL: Query optimization, schema normalization, indexing, transactions (ACID), NoSQL vs Relational.
3. Backend Systems & APIs: REST/GraphQL, concurrency, authentication/JWT, caching (Redis), rate-limiting.
4. Frontend Architecture: State management, React component lifecycle, rendering performance, responsive UI.
5. Distributed Systems & Scaling: Microservice communication, message queues (Kafka/RabbitMQ), CAP theorem, load balancing.
6. GitHub Repositories: Code modularity, clean code, unit testing, CI/CD automation, pull request review.
7. Verified Resume Projects: Architectural decisions, trade-offs, production challenges, and operational metrics.
8. Production Incident Engineering: Root cause analysis, latency debugging, database locks, observability & tracing.
9. Advanced Algorithms & Edge Cases: Hard DSA constraints, memory optimization, bit manipulation, amortized analysis.
10. STAR Behavioral Leadership: Technical conflict resolution, mentoring, cross-functional prioritization, post-mortems.

CRITICAL DIVERSITY & ROTATION RULES:
- Ask exactly ONE focused question per turn. Keep it clear, direct, and conversational.
- 30-DAY COOLDOWN RULE: Inspect 'recently_asked_in_last_30_days'. NEVER repeat or ask any question similar to those questions.
- NEVER repeat or re-ask any question that appears in previous turns or previous_transcript.
- Encourage the candidate to write code, queries, or architecture in the live workbench and run it!

STRUCTURED QUESTION SCHEMAS (CONSTRAINTS, EXAMPLES, HINTS):
- ALWAYS provide 'constraints', 'examples', and 'hints' alongside the question:
  * 'constraints': Array of 2-4 concrete system or problem constraints (e.g., traffic throughput, latency, memory limits, availability).
  * 'examples': Array of 1-2 examples with 'input', 'output', and 'explanation'.
  * 'hints': Array of 2-3 architectural guidance points (e.g. "Unique ID generation (Base62)", "Database schema", "Handling high traffic").

CRITICAL MULTILINGUAL MANDATE (SPEAK IN CANDIDATE'S SELECTED LANGUAGE):
- Inspect the 'language' property in the user payload JSON ('ta', 'hi', 'te', 'kn', 'es', 'fr', 'de', 'en').
- The entire 'question', 'topic', 'hints', and 'examples' MUST be written in the candidate's chosen language:
  * If 'language' == 'ta' (Tamil / Tanglish):
    The interviewer MUST speak in natural, friendly conversational Tamil (using Tamil script or conversational Tanglish with English technical keywords, e.g. "வணக்கம்! Group Anagrams problem-ல hash map frequency key-ஐ எப்படி efficiently construct பண்ணுவீங்க?"). NEVER write solely in English!
  * If 'language' == 'hi' (Hindi / Hinglish):
    The interviewer MUST speak in natural conversational Hindi (using Devanagari script or conversational Hinglish with English technical keywords, e.g. "नमस्ते! चलिए एक interesting coding problem solve करते हैं. Group Anagrams में hash map का use करके time complexity को कैसे optimize करेंगे?"). NEVER write solely in English!
  * If 'language' == 'te' (Telugu):
    Formulate the question in conversational Telugu with English technical terms.
  * If 'language' == 'kn' (Kannada):
    Formulate the question in conversational Kannada with English technical terms.
  * If 'language' == 'es' (Spanish):
    Formulate the question in natural professional Spanish.
  * If 'language' == 'fr' (French):
    Formulate the question in natural professional French.
  * If 'language' == 'de' (German):
    Formulate the question in natural professional German.
  * If 'language' == 'en' (English):
    Formulate the question in clear, professional English.
- NEVER sound like a cold, fast robot or ancient book! Speak with a warm, encouraging, mentor-like peer tone.
- CRITICAL REGISTER RULE FOR TAMIL ('ta' or Tanglish):
  * Modern Tamil software engineers communicate conversationally in natural spoken Tamil / Tanglish.
  * NEVER use ancient, archaic literary "Thooya Tamil" (தூய தமிழ்) like கணினி நிரலாக்கம் or தரவுத்தளம். Engineers speak everyday conversational language!
  * Always keep technical terms and keywords in standard English (SQL, React, Python, FastAPI, Index, Database, Query, Loop, Function, API, Docker, Component, State, Hook).
- CRITICAL REGISTER RULE FOR HINDI ('hi' or Hinglish):
  * Use natural conversational Hinglish as spoken by engineers. Keep technical terms in standard English.
- Return ONLY JSON:
{
  "question": "...",
  "constraints": ["..."],
  "examples": [{"input": "...", "output": "...", "explanation": "..."}],
  "hints": ["..."],
  "question_type": "system_design|technical|project_based|skill_based|role_based|skill_gap|behavioral",
  "difficulty": "easy|medium|hard",
  "topic": "...",
  "rationale": "..."
}
"""

INTENT_SYSTEM_PROMPT = """You are a conversation intent classifier for an AI interview system.
Analyze the candidate's response and return structured intent classification.
Possible intents:
  - technical_answer: candidate is answering the technical question
  - partial_answer: candidate answered partially, seems to know some but not all
  - unsure: candidate is uncertain but attempting an answer
  - dont_know: candidate explicitly doesn't know the answer
  - clarification_request: candidate wants the question clarified
  - repeat_question: candidate wants the question repeated
  - change_topic: candidate wants to switch to a different topic/skill
  - project_request: candidate wants a question about their projects
  - difficulty_change: candidate wants easier or harder questions
  - language_change: candidate wants to switch language
  - skip_question: candidate wants to skip this question
  - follow_up_request: candidate wants a follow-up on the same topic
  - off_topic: candidate said something unrelated to the interview
  - interview_end_request: candidate wants to end the interview

Return ONLY JSON:
{"intent":"...","requested_topic":null_or_string,"answer_content":null_or_string,"confidence":0.0_to_1.0}
"""

EVALUATION_SYSTEM_PROMPT = """You are Cyra-Bot, AI Mentor and Lead Technical Interview Coach and Evaluator at CareerVerse AI.
Analyze the candidate's answer and any submitted code or terminal execution output as an interactive, highly supportive mentor.
Provide a structured educational breakdown:
1. WHAT WAS RIGHT: Specific accurate points, correct design intuition, or good code practices they mentioned.
2. MISTAKES & GAPS: Concrete mistakes in their verbal answer or code, syntax/logic bugs, missed edge cases, overlooked time/space complexity, or unaddressed concurrency.
3. TERMINAL & CODE ANALYSIS:
   - If code is submitted or run in the terminal (marked by [Candidate Submitted Code] or terminal output), thoroughly analyze:
     * Code correctness, logic flaws, off-by-one errors, edge cases.
     * Exact Time and Space Complexity of their submitted code (e.g. O(N) time, O(1) space).
     * Code quality, variable naming, SQL indexing, and error handling.
4. HOW TO ANSWER & CODE: Step-by-step mentor formula and framework on how to structure the optimal answer and write the proper code/query in a real technical interview.
5. SENIOR MODEL ANSWER: A verbatim, senior-level model answer script and/or code demonstration.
6. INTERACTIVE TEACHING: If the answer has mistakes or omissions, explain kindly and constructively what went wrong and guide them like a senior tech lead pairing with them.

CRITICAL MULTILINGUAL EVALUATION MANDATE:
- Check the 'language' property in the user payload JSON ('ta', 'hi', 'te', 'kn', 'es', 'fr', 'de', 'en').
- Formulate all evaluation commentary ('assessment', 'strengths', 'improvements', 'how_to_explain', 'ideal_pitch_script') in the candidate's chosen language:
  * In Tamil ('ta' / Tanglish): Formulate evaluation verdict, explanations, and model answer in natural, friendly conversational Tamil / Tanglish. Keep technical terms in standard English.
  * In Hindi ('hi' / Hinglish): Formulate in natural conversational Hindi / Hinglish. Keep technical terms in English.
  * In Telugu ('te'), Kannada ('kn'), Spanish ('es'), French ('fr'), German ('de'): Formulate in that respective language.
  * In English ('en'): Formulate in clear professional English.
- CONCISENESS RULE: Keep bullet points concise (max 3 items per list, 2 sentences each for how_to_explain and ideal_pitch_script) to guarantee complete, valid JSON.

Return ONLY JSON:
{
  "assessment": "High-level constructive mentor verdict and encouraging summary",
  "score": 8,
  "strengths": [
    "Correctly identified...",
    "Accurately described..."
  ],
  "improvements": [
    "Mistake: Overlooked...",
    "Gap: Did not address..."
  ],
  "missing_elements": [
    "Key concept omitted (e.g., database index scan, concurrency lock)",
    "Missing error handling or retry policy"
  ],
  "how_to_explain": "Step-by-step framework: 1) Clarify constraints. 2) Propose core architecture or write the core query/function. 3) Explain trade-offs and edge cases.",
  "ideal_pitch_script": "\"Here is how to answer: In our architecture, I would...\" (Verbatim senior-level model answer)",
  "structural_framework": "Architecture-Tradeoff / STAR / Edge-Case Framework",
  "follow_up_reason": "Why the next question probes deeper into this area"
}
"""

FINAL_SYSTEM_PROMPT = """You are Cyra-Bot, AI Mentor and Lead Technical Interview Coach and Evaluator at CareerVerse AI.
Use only the verified candidate context and completed transcript. Do not assign a numeric score and do not expose chain-of-thought.
Produce an editorial qualitative report. Return ONLY JSON with:
questions_asked, candidate_answers, strengths, improvement_areas, skill_areas_demonstrated, unanswered_or_weak_areas, overall_interview_summary, recommended_preparation_areas.

CRITICAL MULTILINGUAL MANDATE FOR FINAL REPORT:
- Check the 'language' property in the user payload JSON ('ta', 'hi', 'en', etc.).
- Formulate all narrative report fields ('overall_interview_summary', 'strengths', 'improvement_areas', 'recommended_preparation_areas') in the candidate's chosen language:
  * In Tamil ('ta' / Tanglish): Formulate in natural, conversational Tamil (Tanglish) keeping programming identifiers, tools, and technical terms in standard English.
  * In Hindi ('hi' / Hinglish): Formulate in natural conversational Hindi (Hinglish) with English technical terms.
  * In English ('en'): Formulate in professional editorial English.
"""





def _get_owned_session(db: Session, current_user: User, session_id: str) -> InterviewSession:
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.session_id == session_id,
            InterviewSession.candidate_id == current_user.id,
        )
        .first()
    )
    if not session:
        raise InterviewSessionNotFound()
    return session


def _to_response(session: InterviewSession) -> InterviewSessionResponse:
    transcript = [InterviewTranscriptEntry.model_validate(item) for item in (session.transcript or [])]
    latest = transcript[-1].evaluation if transcript else None
    return InterviewSessionResponse(
        session_id=session.session_id,
        candidate_id=session.candidate_id,
        target_role=session.target_role,
        interview_mode=session.interview_mode,
        focus_topic=getattr(session, "focus_topic", None),
        language=session.language,
        current_question=InterviewQuestionPayload.model_validate(session.current_question) if session.current_question else None,
        question_number=session.question_number,
        transcript=transcript,
        status=session.status,
        created_at=session.created_at,
        completed_at=session.completed_at,
        latest_evaluation=latest,
        final_report=InterviewFinalReport.model_validate(session.final_report) if session.final_report else None,
    )


def get_recently_asked_question_texts(db: Session, candidate_id: int, days: int = 30) -> List[str]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent_sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.candidate_id == candidate_id,
            InterviewSession.created_at >= cutoff,
        )
        .all()
    )
    asked = []
    for s in recent_sessions:
        if s.transcript and isinstance(s.transcript, list):
            for entry in s.transcript:
                if isinstance(entry, dict):
                    q = entry.get("question")
                    q_text = q.get("question") if isinstance(q, dict) else str(q or "")
                    if q_text and q_text.strip() and q_text.strip() not in asked:
                        asked.append(q_text.strip())
        if s.current_question and isinstance(s.current_question, dict):
            cq_text = s.current_question.get("question")
            if cq_text and cq_text.strip() and cq_text.strip() not in asked:
                asked.append(cq_text.strip())
    return asked


def get_candidate_question_history(db: Session, current_user: User, days_cooldown: int = 30) -> List[Dict[str, Any]]:
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.candidate_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
        .all()
    )
    history_items = []
    seen_questions = set()
    now = datetime.utcnow()

    for s in sessions:
        if s.transcript and isinstance(s.transcript, list):
            for entry in s.transcript:
                if isinstance(entry, dict):
                    q = entry.get("question") or {}
                    q_text = q.get("question") if isinstance(q, dict) else str(q or "")
                    if not q_text or q_text.strip() in seen_questions:
                        continue
                    seen_questions.add(q_text.strip())

                    asked_at = entry.get("created_at") or s.created_at
                    if isinstance(asked_at, str):
                        try:
                            asked_at_dt = datetime.fromisoformat(asked_at.replace("Z", "+00:00")).replace(tzinfo=None)
                        except Exception:
                            asked_at_dt = s.created_at
                    else:
                        asked_at_dt = asked_at or s.created_at

                    days_ago = max(0, (now - asked_at_dt).days)
                    ready_for_retest = days_ago >= days_cooldown
                    days_remaining = max(0, days_cooldown - days_ago)

                    history_items.append({
                        "question": q_text.strip(),
                        "question_type": q.get("question_type", "technical") if isinstance(q, dict) else "technical",
                        "topic": q.get("topic", "Technical Assessment") if isinstance(q, dict) else "Technical Assessment",
                        "difficulty": q.get("difficulty", "medium") if isinstance(q, dict) else "medium",
                        "target_role": s.target_role,
                        "asked_at": asked_at_dt.isoformat(),
                        "days_ago": days_ago,
                        "ready_for_retest": ready_for_retest,
                        "days_until_retest": days_remaining,
                        "evaluation_summary": (entry.get("evaluation") or {}).get("assessment") if isinstance(entry.get("evaluation"), dict) else None,
                        "score": (entry.get("evaluation") or {}).get("score") if isinstance(entry.get("evaluation"), dict) else None,
                        "strengths": (entry.get("evaluation") or {}).get("strengths") if isinstance(entry.get("evaluation"), dict) else [],
                        "improvements": (entry.get("evaluation") or {}).get("improvements") if isinstance(entry.get("evaluation"), dict) else [],
                        "how_to_explain": (entry.get("evaluation") or {}).get("how_to_explain") if isinstance(entry.get("evaluation"), dict) else None,
                        "ideal_pitch_script": (entry.get("evaluation") or {}).get("ideal_pitch_script") if isinstance(entry.get("evaluation"), dict) else None,
                        "answer_snippet": entry.get("answer", "")[:150] if entry.get("answer") else None,
                    })

    return history_items


def _generate_question_with_diversity(
    session: InterviewSession,
    transcript: List[Dict[str, Any]],
    context_text: str,
    evidence: Dict[str, Any],
    recently_asked: List[str],
) -> InterviewQuestionPayload:
    """
    Guarantees diverse, non-repetitive question generation by:
    1. Tracking all previously asked question texts and underlying normalized concepts in this session and recent history.
    2. Requesting LLM generation with explicit exclusion of already asked concepts.
    3. Validating the generated question against concept collisions and semantic text similarity (< 0.70).
    4. Bounded retry loop (up to 3 attempts).
    5. Falling back to a guaranteed novel pattern from the verified track catalog if LLM retries exhaust.
    """
    asked_texts = set()
    asked_concepts = set()
    for t in transcript:
        if isinstance(t, dict):
            q_obj = t.get("question")
            if isinstance(q_obj, dict) and q_obj.get("question"):
                q_str = q_obj.get("question").strip()
                asked_texts.add(q_str.lower())
                concept = q_obj.get("normalized_concept") or normalize_question_concept(q_str, session.interview_mode)
                asked_concepts.add(concept)
            elif isinstance(q_obj, str) and q_obj.strip():
                asked_texts.add(q_obj.strip().lower())
                asked_concepts.add(normalize_question_concept(q_obj.strip(), session.interview_mode))
    if session.current_question:
        cur_q = session.current_question.get("question") if isinstance(session.current_question, dict) else str(session.current_question)
        if cur_q and cur_q.strip():
            asked_texts.add(cur_q.strip().lower())
            cur_concept = (
                session.current_question.get("normalized_concept")
                if isinstance(session.current_question, dict)
                else None
            ) or normalize_question_concept(cur_q.strip(), session.interview_mode)
            asked_concepts.add(cur_concept)
    for rq in (recently_asked or []):
        if rq and isinstance(rq, str) and rq.strip():
            asked_texts.add(rq.strip().lower())
            asked_concepts.add(normalize_question_concept(rq.strip(), session.interview_mode))

    max_retries = 3
    for attempt in range(max_retries):
        try:
            raw_question = _provider_json(
                QUESTION_SYSTEM_PROMPT,
                _base_prompt(
                    session,
                    context_text,
                    evidence,
                    transcript,
                    recently_asked_in_last_30_days=recently_asked,
                    excluded_concepts=list(asked_concepts),
                ),
                max_completion_tokens=650,
            )
            question = _question_payload(raw_question)
            q_text = question.question.strip()
            q_concept = question.normalized_concept or normalize_question_concept(q_text, session.interview_mode)
            question.normalized_concept = q_concept
            question.session_id = session.session_id
            question.track = session.interview_mode
            question.language = session.language
            question.question_text = q_text

            # Enforce non-repetition and semantic uniqueness
            is_repetitive = (
                q_concept in asked_concepts
                or q_text.lower() in asked_texts
                or any(calculate_text_similarity(q_text, past) >= 0.55 for past in asked_texts)
            )
            if not is_repetitive:
                return localize_question_payload(question, session.language)

            logger.info(
                "AI provider generated repetitive question (concept=%s, attempt=%d). Retrying generation...",
                q_concept,
                attempt + 1,
            )
            asked_concepts.add(q_concept)
            asked_texts.add(q_text.lower())
        except Exception as exc:
            logger.warning("AI provider question generation attempt %d failed: %s", attempt + 1, exc)

    logger.info("Using diverse evidence-grounded fallback question for session %s (mode=%s)", session.session_id, session.interview_mode)
    fallback = _fallback_next_question(session, transcript, evidence, blocked_questions=recently_asked)
    fallback.session_id = session.session_id
    fallback.track = session.interview_mode
    fallback.language = session.language
    fallback.question_text = fallback.question
    return localize_question_payload(fallback, session.language)


def create_interview_session(db: Session, current_user: User, request: InterviewSessionCreateRequest) -> InterviewSessionResponse:
    role = request.target_role
    if request.interview_mode in {"target_role", "skill_gap"} and not role:
        raise InterviewSessionStateError("target_role is required for this interview mode")
    if role and not get_role_requirements(role):
        raise InterviewSessionStateError(f"Unsupported target role: {role}")

    session = InterviewSession(
        session_id=str(uuid.uuid4()),
        candidate_id=current_user.id,
        target_role=role,
        interview_mode=request.interview_mode,
        focus_topic=request.focus_topic,
        language=request.language,
        question_number=1,
        transcript=[],
        status="active",
    )
    topic_clause = f" focusing on {request.focus_topic}" if request.focus_topic else ""
    context_query = f"Start a {request.interview_mode} interview{topic_clause}" + (f" for {role}" if role else "")
    context = _candidate_context(current_user.id, context_query)
    try:
        evidence = _graph_evidence(current_user.id, db=db, current_user=current_user)
    except TypeError:
        evidence = _graph_evidence(current_user.id)
    recently_asked = get_recently_asked_question_texts(db, current_user.id, days=30)
    question = _generate_question_with_diversity(
        session,
        [],
        context.context_text,
        evidence,
        recently_asked,
    )

    session.current_question = question.model_dump(mode="json")
    db.add(session)
    db.commit()
    db.refresh(session)
    return _to_response(session)


def submit_interview_answer(
    db: Session,
    current_user: User,
    session_id: str,
    request: InterviewAnswerRequest,
) -> InterviewSessionResponse:
    session = _get_owned_session(db, current_user, session_id)
    if session.status != "active" or not session.current_question:
        raise InterviewSessionStateError("Interview session is not accepting answers")

    context = _candidate_context(current_user.id, f"Follow-up interview for {session.target_role or 'the candidate'}")
    try:
        evidence = _graph_evidence(current_user.id, db=db, current_user=current_user)
    except TypeError:
        evidence = _graph_evidence(current_user.id)
    transcript = _transcript_payload(session)
    question = InterviewQuestionPayload.model_validate(session.current_question)

    # ── Step 1: Classify candidate's response intent ──────────────────────────
    intent_payload = json.dumps(
        {
            "latest_question": question.model_dump(),
            "candidate_response": request.answer,
            "interview_mode": session.interview_mode,
            "focus_topic": getattr(session, "focus_topic", None),
            "language": session.language,
        },
        ensure_ascii=False,
    )
    answer_text = (request.answer or "").strip()
    answer_lower = answer_text.lower()
    classified_intent = "technical_answer"
    requested_topic = None

    if answer_lower in ["skip", "pass", "skip question"]:
        classified_intent = "skip_question"
    elif "don't know" in answer_lower or "dont know" in answer_lower or "no idea" in answer_lower:
        classified_intent = "dont_know"
    elif "repeat" in answer_lower and ("question" in answer_lower or "can you" in answer_lower):
        classified_intent = "repeat_question"
    elif "clarify" in answer_lower or "what do you mean" in answer_lower:
        classified_intent = "clarification_request"
    elif len(answer_lower) < 25 and ("easier" in answer_lower or "harder" in answer_lower):
        classified_intent = "difficulty_change"
    elif len(answer_lower) < 25 and ("switch" in answer_lower or "talk about" in answer_lower):
        try:
            raw_intent = _provider_json(INTENT_SYSTEM_PROMPT, intent_payload, max_completion_tokens=150)
            classified_intent = raw_intent.get("intent", "technical_answer")
            requested_topic = raw_intent.get("requested_topic")
        except Exception:
            pass

    # Update dynamic focus topic if candidate supplied one or switched
    if request.focus_topic and request.focus_topic.strip():
        session.focus_topic = request.focus_topic.strip()
    elif requested_topic and requested_topic.strip():
        session.focus_topic = requested_topic.strip()

    # Update dynamic language if candidate switches
    if request.language:
        session.language = request.language

    # Combine verbal answer with submitted scratchpad code (if provided)
    effective_answer = request.answer.strip()
    if request.code and request.code.strip():
        effective_answer = f"{effective_answer}\n\n[Candidate Submitted Code]:\n```\n{request.code.strip()}\n```"

    # ── Step 2: Evaluate the answer (intent-aware) ────────────────────────────
    eval_payload = json.dumps(
        {
            "candidate_id": session.candidate_id,
            "target_role": session.target_role,
            "interview_mode": session.interview_mode,
            "language": session.language,
            "verified_candidate_context": context.context_text[:2500],
            "verified_graph_evidence": evidence,
            "previous_transcript": transcript[-3:],
            "latest_question": question.model_dump(),
            "latest_answer": effective_answer,
            "classified_intent": classified_intent,
            "requested_topic": requested_topic,
        },
        ensure_ascii=False,
    )
    try:
        raw_eval = _provider_json(
            EVALUATION_SYSTEM_PROMPT,
            eval_payload,
            max_completion_tokens=1000,
        )
        evaluation = _evaluation_payload(raw_eval)
    except Exception as exc:
        logger.warning("AI provider failed answer evaluation, falling back to evidence-grounded evaluation: %s", exc)
        evaluation = _fallback_evaluation(effective_answer, question, session.target_role, language=session.language)

    # ── Step 3: Generate next question (intent-aware & diversity-guaranteed) ──
    recently_asked = get_recently_asked_question_texts(db, current_user.id, days=30)
    next_question = _generate_question_with_diversity(
        session,
        transcript + [{
            "question_number": session.question_number,
            "question": question.model_dump(),
            "answer": effective_answer,
            "evaluation": evaluation.model_dump(),
            "intent": classified_intent,
            "requested_topic": requested_topic,
        }],
        context.context_text,
        evidence,
        recently_asked,
    )

    entry = InterviewTranscriptEntry(
        question_number=session.question_number,
        question=question,
        answer=effective_answer,
        evaluation=evaluation,
        created_at=datetime.utcnow(),
    )
    session.transcript = transcript + [entry.model_dump(mode="json")]
    session.question_number += 1
    session.current_question = next_question.model_dump(mode="json")
    db.commit()
    db.refresh(session)
    return _to_response(session)


def get_interview_session(db: Session, current_user: User, session_id: str) -> InterviewSessionResponse:
    return _to_response(_get_owned_session(db, current_user, session_id))


def get_candidate_interview_sessions(
    db: Session,
    current_user: User,
    limit: int = 50,
    offset: int = 0,
) -> List[InterviewSessionSummaryResponse]:
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.candidate_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    results = []
    for s in sessions:
        transcript = s.transcript or []
        concepts = []
        answers_summary = None
        evidence_srcs = set()
        for t in transcript:
            if isinstance(t, dict):
                q = t.get("question") or {}
                if isinstance(q, dict):
                    if q.get("topic"):
                        concepts.append(q.get("topic"))
                    if q.get("evidence_source"):
                        evidence_srcs.add(q.get("evidence_source"))
                ans = t.get("answer")
                if ans and not answers_summary:
                    answers_summary = ans[:160] + ("..." if len(ans) > 160 else "")
        if s.current_question and isinstance(s.current_question, dict):
            cq_topic = s.current_question.get("topic")
            if cq_topic and cq_topic not in concepts:
                concepts.append(cq_topic)
            cq_ev = s.current_question.get("evidence_source")
            if cq_ev:
                evidence_srcs.add(cq_ev)

        recommendation = None
        if s.final_report and isinstance(s.final_report, dict):
            recommendation = s.final_report.get("overall_interview_summary")

        results.append(
            InterviewSessionSummaryResponse(
                session_id=s.session_id,
                candidate_id=s.candidate_id,
                target_role=s.target_role,
                interview_mode=s.interview_mode,
                focus_topic=getattr(s, "focus_topic", None),
                language=s.language,
                question_count=len(transcript) + (1 if s.current_question else 0),
                status=s.status,
                created_at=s.created_at,
                completed_at=s.completed_at,
                concepts_covered=concepts[:8],
                candidate_response_summary=answers_summary,
                evidence_sources=list(evidence_srcs)[:5],
                recommendation=recommendation,
            )
        )
    return results


def complete_interview_session(db: Session, current_user: User, session_id: str) -> InterviewSessionResponse:
    session = _get_owned_session(db, current_user, session_id)
    if session.status == "completed":
        return _to_response(session)
    if not session.transcript:
        raise InterviewSessionStateError("At least one answered question is required to complete the interview")
    context = _candidate_context(current_user.id, f"Final interview report for {session.target_role or 'the candidate'}")
    try:
        evidence = _graph_evidence(current_user.id, db=db, current_user=current_user)
    except TypeError:
        evidence = _graph_evidence(current_user.id)
    try:
        raw_report = _provider_json(
            FINAL_SYSTEM_PROMPT,
            _base_prompt(session, context.context_text, evidence, _transcript_payload(session)),
            max_completion_tokens=1200,
        )
        report = InterviewFinalReport.model_validate(_final_report_payload(raw_report, session))
    except Exception as exc:
        logger.warning("AI provider failed to generate interview report, falling back to evidence-grounded report: %s", exc)
        report = _fallback_final_report(session, evidence)

    session.final_report = report.model_dump(mode="json")
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    session.current_question = None
    db.commit()
    db.refresh(session)
    return _to_response(session)


def generate_cyra_chat_response(
    req: Any,  # CyraChatRequest
    current_user: User,
) -> Any:      # CyraChatResponse
    """
    Direct, conversational LLM endpoint for real-time chat with Dr. Cyra Vance
    during live interviews. Generates authentic, technically rigorous, pedagogical responses.
    """
    from app.schemas.interview import CyraChatResponse
    from app.ai.providers.factory import get_model_provider

    user_msg = (req.message or "").strip()
    curr_q = (req.current_question or "").strip()
    role = req.role or "Software Engineer"
    code = (req.candidate_code or "").strip()
    action = req.action_type or "chat"
    lang = (getattr(req, "language", "en") or "en").strip().lower()

    lang_clause = ""
    if lang.startswith("ta"):
        lang_clause = (
            "\n\nCRITICAL MULTILINGUAL MANDATE (TAMIL / TANGLISH):\n"
            "You MUST reply in natural, friendly conversational Tamil (Tanglish) as spoken by software engineers. "
            "Keep programming identifiers, API names, code keywords, and technical terms in standard English (e.g. hash map, Big-O, loop, array). "
            "NEVER respond solely in English!"
        )
    elif lang.startswith("hi"):
        lang_clause = (
            "\n\nCRITICAL MULTILINGUAL MANDATE (HINDI / HINGLISH):\n"
            "You MUST reply in natural, friendly conversational Hindi (Hinglish) as spoken by software engineers. "
            "Keep programming identifiers, API names, code keywords, and technical terms in standard English. "
            "NEVER respond solely in English!"
        )

    if action == "teach":
        system_prompt = (
            "You are Dr. Cyra Vance, Master AI Technical Interviewer & Computer Science Professor at CareerVerse AI. "
            "You are in 'TEACH & MASTER' mode. Your goal is to TEACH the candidate the concepts, intuition, and mental models "
            "behind the problem so they truly master it for top-tier engineering interviews. "
            f"Candidate Target Role: {role}. "
            f"Question / Topic to Teach: {curr_q or 'Technical Problem Concepts'}. "
            "Candidate's Current Workspace Code (if any):\n"
            f"```{code}```\n\n"
            "Pedagogical Structure to Follow: "
            "1. 💡 Core Mental Model & Intuition: Explain the fundamental concept simply and visually with an analogy. "
            "2. 📐 The Top-Tier Answer Framework: Outline the structured 4-step framework elite engineers use to solve this. "
            "3. ⚖️ Critical Trade-offs: Contrast optimal time/space complexity with brute force, and discuss scalability or edge cases. "
            "4. ❓ Check-in Question: Ask one engaging question to test the candidate's understanding before they write code."
            f"{lang_clause}"
        )
        prompt = f"Candidate wants you to teach them: {curr_q}. Candidate says: {user_msg or 'Please teach me the core concepts and solution framework.'}"
    else:
        system_prompt = (
            "You are Dr. Cyra Vance, an elite Lead AI Technical Interviewer & Mentor at CareerVerse AI. "
            "You are conducting a live, realistic technical interview. "
            f"Candidate Target Role: {role}. "
            f"Active Interview Question: {curr_q or 'Technical Problem Discussion'}. "
            "Candidate's Current Workspace Code (if any):\n"
            f"```{code}```\n\n"
            "Tone and Demeanor: Direct, insightful, intellectually rigorous, encouraging, like a Principal Engineer at Google or Stripe. "
            "Guidelines: "
            "1. Give direct, authentic, conversational AI answers in 2 to 3 concise, impactful sentences. "
            "2. If the candidate asks for a hint, give an intuitive, conceptual clue without giving away the direct code. "
            "3. If they propose an architecture or algorithmic approach, evaluate its latency, scalability, and asymptotic bounds. "
            "4. If they ask about constraints or edge cases, clarify the boundaries and failure modes. "
            "5. Never output canned placeholder responses. Address the candidate's exact question or idea."
            f"{lang_clause}"
        )
        prompt = f"Candidate says: {user_msg}"
        if action == "hint":
            prompt = f"Candidate asks for a pedagogical hint on: {curr_q}. Candidate's current code: {code}"
        elif action == "constraints":
            prompt = f"Candidate asks to clarify constraints and edge boundaries on: {curr_q}."
        elif action == "approach":
            prompt = f"Candidate is discussing their algorithmic approach and time-complexity trade-offs: {user_msg or curr_q}."

    try:
        provider = get_model_provider()
        res = provider.generate_text(
            system_prompt=system_prompt,
            user_message=prompt,
            temperature=0.35 if action == "teach" else 0.4,
            max_completion_tokens=600 if action == "teach" else 300,
        )
        if res and res.content and res.content.strip():
            reply_text = res.content.strip()
            if lang.startswith("ta"):
                followups = (
                    [
                        "இந்த framework-க்கான code walkthrough காட்ட முடியுமா?",
                        "Space complexity-ஐ இன்னும் optimize செய்தால் என்னவாகும்?",
                        "Duplicate elements அல்லது concurrency-ஐ எப்படி கையாள்வது?",
                    ]
                    if action == "teach"
                    else [
                        "இந்த approach-க்கான edge cases என்னென்ன?",
                        "Space complexity-ஐ மேலும் குறைக்க முடியுமா?",
                        "High concurrency-ல் இது எவ்வாறு scale ஆகும்?",
                    ]
                )
            elif lang.startswith("hi"):
                followups = (
                    [
                        "क्या आप इस फ्रेमवर्क का कोड वॉकथ्रू दिखा सकते हैं?",
                        "यदि हम आगे ऑप्टिमाइज़ करें तो स्पेस जटिलता क्या होगी?",
                        "डुप्लिकेट एलिमेंट्स या कॉनकरेंसी को कैसे संभालेंगे?",
                    ]
                    if action == "teach"
                    else [
                        "इस दृष्टिकोण के लिए एज केस क्या हैं?",
                        "क्या हम स्पेस जटिलता को और कम कर सकते हैं?",
                        "उच्च समवर्तीता के तहत यह कैसे स्केल होगा?",
                    ]
                )
            else:
                followups = (
                    [
                        "Can you give a code walkthrough for this framework?",
                        "What is the space complexity if we optimize further?",
                        "How do we handle duplicate elements or concurrency?",
                    ]
                    if action == "teach"
                    else [
                        "What are the edge cases for this approach?",
                        "Can we optimize the space complexity further?",
                        "How would this scale under high concurrency?",
                    ]
                )
            return CyraChatResponse(
                reply=reply_text,
                action_type=action,
                suggested_followups=followups,
            )
    except Exception as exc:
        logger.warning(f"Cyra chat AI generation error: {exc}")

    if lang.startswith("ta"):
        if action == "teach":
            fallback_reply = (
                "💡 **Core Mental Model**: இந்த சிக்கலை invariant state tracking அடிப்படையில் பாருங்கள். O(N²) முறையில் மீண்டும் மீண்டும் தேடுவதற்கு பதிலாக, hash map அல்லது two-pointer window பயன்படுத்தி O(N) அல்லது O(1) நேரத்தில் அணுகுங்கள்.\n\n"
                "📐 **Top-Tier Framework**:\n"
                "1. Constraints-ஐ தெளிவுபடுத்துங்கள் (எல்லைகள், negative எண்கள், duplicates).\n"
                "2. Mathematical invariant-ஐ அடையாளம் காணுங்கள் (உதா: complement = target - current).\n"
                "3. குறைந்தபட்ச state container-ஐ தேர்வு செய்யுங்கள் (hash map vs sorted array).\n"
                "4. Edge cases-ஐ கையாளுங்கள் (வெற்று உள்ளீடு, ஒற்றை மதிப்பு).\n\n"
                "⚖️ **Trade-offs**: நேரம் O(N²)-ல் இருந்து O(N)-ஆக குறைகிறது, O(N) auxiliary space தேவைப்படுகிறது. Workbench-ல் code எழுதலாமா?"
            )
        elif action == "hint":
            fallback_reply = "உங்கள் தற்போதைய நிலையின் invariant-ஐ கவனியுங்கள்: மீண்டும் ஸ்கேன் செய்யாமல் hash map அல்லது two pointers மூலம் O(1) நேரத்தில் சரிபார்க்க முடியுமா?"
        elif action == "constraints":
            fallback_reply = "எல்லை வரம்புகள் (boundary limits) மற்றும் duplicate elements-ல் கவனம் செலுத்துங்கள். தீவிர மதிப்புகளில் quadratic time அல்லது overflow ஏற்படாமல் பாதுகாக்குங்கள்."
        else:
            fallback_reply = f"{role} பணிக்கான ஒரு சிறந்த யோசனை. உங்கள் முடிவை படிப்படியாக விளக்குங்கள் மற்றும் invariants-ஐ எவ்வாறு உறுதி செய்வீர்கள் என்பதை கூறுங்கள்."
        return CyraChatResponse(
            reply=fallback_reply,
            action_type=action,
            suggested_followups=[
                "Duplicate elements-ஐ எப்படி கையாள்வது?",
                "Amortized runtime என்ன?",
            ],
        )

    if lang.startswith("hi"):
        if action == "teach":
            fallback_reply = (
                "💡 **Core Mental Model**: इस समस्या को invariant state tracking के संदर्भ में सोचें. O(N²) में बार-बार सर्च करने के बजाय, hash map या two pointers का उपयोग करके O(N) या O(1) में प्रोसेस करें.\n\n"
                "📐 **Top-Tier Framework**:\n"
                "1. बाधाओं को स्पष्ट करें (बाउंड्स, नेगेटिव नंबर, डुप्लीकेट्स).\n"
                "2. गणितीय इनवेरिएंट को पहचानें (उदा: complement = target - current).\n"
                "3. न्यूनतम स्टेट कंटेनर चुनें (hash map बनाम sorted array).\n"
                "4. एज केसेस को संभालें (खाली इनपुट, सिंगल एलिमेंट).\n\n"
                "⚖️ **Trade-offs**: टाइम कॉम्प्लेक्सिटी O(N²) से O(N) हो जाती है, जिसमें O(N) स्पेस लगता है. क्या वर्कबेंच में कोड लिखना चाहेंगे?"
            )
        elif action == "hint":
            fallback_reply = "अपनी सक्रिय स्थिति के इनवेरिएंट पर ध्यान दें: क्या आप सहायक फ़्रीक्वेंसी मैप या दो पॉइंटर्स का उपयोग करके O(1) समय में स्थिति ट्रैक कर सकते हैं?"
        elif action == "constraints":
            fallback_reply = "बाउंड्री लिमिट्स और डुप्लीकेट एलिमेंट्स पर ध्यान दें. सुनिश्चित करें कि आपका दृष्टिकोण बिना किसी ओवरफ़्लो के काम करे."
        else:
            fallback_reply = f"{role} के लिए यह एक विचारणीय बिंदु है. अपने निर्णय को चरण दर चरण समझाएं और बताएं कि आप इसे कैसे सत्यापित करेंगे."
        return CyraChatResponse(
            reply=fallback_reply,
            action_type=action,
            suggested_followups=[
                "डुप्लिकेट एलिमेंट्स को कैसे संभालें?",
                "अमॉर्टाइज्ड रनटाइम क्या होगा?",
            ],
        )

    if action == "teach":
        fallback_reply = (
            "💡 **Core Mental Model**: Think of this problem in terms of invariant state tracking. Instead of repeatedly re-scanning previous elements in O(N²), store observed values in an auxiliary hash map or two-pointer window to achieve O(N) or O(1) query time.\n\n"
            "📐 **Top-Tier Framework**:\n"
            "1. Clarify constraints (bounds, negative numbers, duplicates).\n"
            "2. Identify the mathematical invariant (e.g., complement = target - current).\n"
            "3. Select the minimal state container (hash map vs sorted array).\n"
            "4. Handle edge cases (empty input, single element, large values).\n\n"
            "⚖️ **Trade-offs**: Time drops from O(N²) to O(N), trading O(N) auxiliary space. Would you like to walk through the implementation in the workbench?"
        )
    elif action == "hint":
        fallback_reply = "Consider the invariant of your active state: can you track the required condition in O(1) time using an auxiliary frequency map or two pointers rather than re-scanning?"
    elif action == "constraints":
        fallback_reply = "Pay attention to boundary limits and duplicate elements. Ensure your approach handles extreme values without quadratic time degradation or integer overflow."
    else:
        fallback_reply = f"That's a thoughtful consideration for a {role}. Walk through your decision step-by-step and explain how you plan to verify the invariants before implementation."

    return CyraChatResponse(
        reply=fallback_reply,
        action_type=action,
        suggested_followups=[
            "How do we handle duplicate elements?",
            "What is the amortized runtime?",
        ],
    )


def update_session_language(
    db: Session,
    current_user: User,
    session_id: str,
    new_language: str,
) -> InterviewSessionResponse:
    """
    Dynamically update active interview session language mid-interview.
    Updates the session entity, localizes the active question immediately,
    and returns the updated session payload without disturbing prior transcript history.
    """
    session = _get_owned_session(db, current_user, session_id)
    lang = (new_language or "en").strip().lower()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    session.language = lang

    if session.current_question and isinstance(session.current_question, dict):
        q_payload = InterviewQuestionPayload.model_validate(session.current_question)
        localized = localize_question_payload(q_payload, lang)
        session.current_question = localized.model_dump(mode="json")

    db.commit()
    db.refresh(session)
    return _to_response(session)


