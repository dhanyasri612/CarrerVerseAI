import json
import logging
import re
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.teaching_progress import TeachingProgress
from app.schemas.teaching import (
    SkillCurriculumStage,
    SkillLearningPathResponse,
    TeachingLesson,
)
from app.services.teaching_resource_service import retrieve_teaching_resources_for_lesson
from app.services.learner_knowledge_service import build_learner_knowledge_profile
from app.ai.providers.factory import get_model_provider

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"[-\s]+", "-", s) or "item"


# ── CURATED DOMAIN STAGE ONTOLOGIES ──────────────────────────────────────────
# Curated multi-stage curricula for major skills (with dynamic generation for all others)
CURATED_SKILL_CURRICULA: Dict[str, List[Dict[str, Any]]] = {
    "react": [
        {
            "stage_number": 1,
            "stage_name": "Foundations",
            "description": "What React is, JavaScript prerequisites, JSX syntax, components, rendering composition, props, and fundamental state.",
            "lessons": [
                {
                    "title": "What React Is & Why It Exists",
                    "topic": "Declarative UI, Virtual DOM & React Problem Statement",
                    "summary": "Understand declarative UI vs imperative DOM manipulation and why React was created.",
                    "challenge": "Explain the difference between imperative DOM manipulation (e.g. document.createElement) and React's declarative component model.",
                    "diagnostic": "Why does direct DOM manipulation cause performance bottlenecks in high-frequency applications?",
                    "objective": "Understand declarative UI paradigms and Virtual DOM reconciliation motivation.",
                    "prereqs": ["JavaScript ES6+ fundamentals"],
                    "starter_code": "// Imperative vs Declarative paradigm comparison\n",
                    "resources": ["React Official Docs: Quick Start", "Thinking in React"],
                },
                {
                    "title": "JSX, Components & Component Composition",
                    "topic": "JSX Transformation, Functional Components & Nesting",
                    "summary": "Master JSX transpilation into React.createElement and composing reusable UI component hierarchies.",
                    "challenge": "How does JSX get converted into JavaScript function calls? Why must React components return a single root element (or Fragment)?",
                    "diagnostic": "What does Babel transpile <div><h1>Hello</h1></div> into under the hood?",
                    "objective": "Master functional components, JSX compilation, and component composition patterns.",
                    "prereqs": ["JavaScript functions and arrow syntax"],
                    "starter_code": "function UserCard({ name, role }) {\n  return <div>{name} - {role}</div>;\n}\n",
                    "resources": ["React.dev: Writing Markup with JSX"],
                },
                {
                    "title": "Props & State Fundamentals",
                    "topic": "Unidirectional Data Flow, Props Immutability & useState",
                    "summary": "Learn unidirectional data flow, passing props down component trees, and managing local component state.",
                    "challenge": "Why are props read-only in React? How does useState trigger component re-renders, and why must state mutations be immutable?",
                    "diagnostic": "What happens if you mutate state directly with 'state.count = 5' instead of 'setCount(5)'?",
                    "objective": "Enforce props immutability and understand state-driven re-render triggers.",
                    "prereqs": ["JSX and Component Composition"],
                    "starter_code": "import { useState } from 'react';\n\nfunction Counter() {\n  const [count, setCount] = useState(0);\n  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;\n}\n",
                    "resources": ["React.dev: State: A Component's Memory"],
                },
            ],
        },
        {
            "stage_number": 2,
            "stage_name": "Core React",
            "description": "Event handling, conditional rendering, lists and keys, forms, state updates, and component lifecycles.",
            "lessons": [
                {
                    "title": "Event Handling & Synthetic Events",
                    "topic": "SyntheticEvent Wrapper, Event Pooling & Bubbling",
                    "summary": "Understand React's cross-browser SyntheticEvent system and event handler dispatch.",
                    "challenge": "How does React's SyntheticEvent system differ from native browser events, and how does event delegation work at the root container?",
                    "diagnostic": "Why does passing an inline function onClick={handleClick()} fail compared to onClick={handleClick}?",
                    "objective": "Handle events correctly without premature execution or unwanted re-renders.",
                    "prereqs": ["Props and State Fundamentals"],
                    "starter_code": "function FormSubmit() {\n  const handleSubmit = (e) => {\n    e.preventDefault();\n  };\n  return <form onSubmit={handleSubmit}></form>;\n}\n",
                    "resources": ["React.dev: Responding to Events"],
                },
                {
                    "title": "Conditional Rendering & Lists with Keys",
                    "topic": "Short-Circuit Rendering, List Reconciliation & Key Invariant",
                    "summary": "Master rendering conditional UI and rendering dynamic collections using stable unique keys.",
                    "challenge": "Why is using array index as a 'key' in a dynamic list considered a dangerous anti-pattern during reordering or deletion?",
                    "diagnostic": "Walk through what happens to component internal state when a list item is deleted if keys are array indices.",
                    "objective": "Safely render dynamic collections with stable identity keys.",
                    "prereqs": ["Component rendering"],
                    "starter_code": "const items = [{ id: 'a1', text: 'Task 1' }];\n// Render with stable keys\n",
                    "resources": ["React.dev: Rendering Lists"],
                },
                {
                    "title": "Forms & Controlled vs Uncontrolled Components",
                    "topic": "Controlled Inputs, Form State & Component Lifecycles",
                    "summary": "Manage form state with controlled components and compare with uncontrolled ref inputs.",
                    "challenge": "When should you prefer a controlled component over an uncontrolled component with useRef, and how do you handle complex multi-input forms?",
                    "diagnostic": "What is the single source of truth in a controlled input?",
                    "objective": "Build validated, resilient form inputs adhering to single source of truth.",
                    "prereqs": ["useState fundamentals"],
                    "starter_code": "const [form, setForm] = useState({ email: '', password: '' });\n",
                    "resources": ["React.dev: Sharing State Between Components"],
                },
            ],
        },
        {
            "stage_number": 3,
            "stage_name": "Hooks",
            "description": "useState, useEffect, useRef, useMemo, useCallback, custom hooks, Rules of Hooks, and avoiding effect bugs.",
            "lessons": [
                {
                    "title": "useEffect & Lifecycle Synchronization",
                    "topic": "Dependency Arrays, Cleanup Functions & Race Conditions",
                    "summary": "Master side-effects, dependency array invariants, cleanup handlers, and preventing async race conditions.",
                    "challenge": "Why should useEffect NOT be used for calculating derived state? How do you prevent race conditions when fetching data inside useEffect?",
                    "diagnostic": "What happens if a state variable used inside useEffect is omitted from its dependency array?",
                    "objective": "Master effect synchronization, cleanup lifecycles, and async race-condition guards.",
                    "prereqs": ["Core React state"],
                    "starter_code": "useEffect(() => {\n  let active = true;\n  fetchData().then(data => { if (active) setData(data); });\n  return () => { active = false; };\n}, [query]);\n",
                    "resources": ["React.dev: Synchronizing with Effects", "You Might Not Need an Effect"],
                },
                {
                    "title": "useRef & DOM Access",
                    "topic": "Mutable References, Preserving Values Across Renders",
                    "summary": "Use useRef to store mutable values that do not trigger re-renders and access real DOM nodes.",
                    "challenge": "How does useRef differ from useState in terms of component re-renders? Give two distinct use cases for useRef beyond DOM manipulation.",
                    "diagnostic": "Does mutating ref.current trigger a component re-render?",
                    "objective": "Understand ref lifecycle, non-rendering mutable state, and imperative DOM access.",
                    "prereqs": ["useEffect"],
                    "starter_code": "const timerRef = useRef(null);\nconst inputRef = useRef(null);\n",
                    "resources": ["React.dev: Referencing Values with Refs"],
                },
                {
                    "title": "useMemo & useCallback Performance Hooks",
                    "topic": "Referential Equality, Expensive Computation & Memoization",
                    "summary": "Optimize render performance by memoizing complex calculations and stabilizing callback identities.",
                    "challenge": "When does adding useMemo or useCallback actually HURT performance rather than help? What role does Object.is referential equality play?",
                    "diagnostic": "Why does passing an inline callback to a React.memo child component cause the child to re-render anyway?",
                    "objective": "Apply memoization surgically without cargo-culting or memory overhead.",
                    "prereqs": ["React re-render mechanics"],
                    "starter_code": "const memoizedValue = useMemo(() => computeHeavy(a, b), [a, b]);\nconst memoizedFn = useCallback(() => handleClick(id), [id]);\n",
                    "resources": ["React.dev: useMemo", "React.dev: useCallback"],
                },
                {
                    "title": "Custom Hooks & Rules of Hooks",
                    "topic": "Hook Composition, Reusable Logic & Call Order Invariant",
                    "summary": "Extract reusable stateful logic into custom hooks while adhering to the Rules of Hooks.",
                    "challenge": "Why can Hooks never be placed inside if-statements, loops, or nested functions? Build a custom useDebounce or useLocalStorage hook.",
                    "diagnostic": "How does React internally track which hook corresponds to which state call across renders?",
                    "objective": "Design reusable, composable custom hooks adhering strictly to hook invariants.",
                    "prereqs": ["All core hooks"],
                    "starter_code": "function useDebounce(value, delay) {\n  const [debounced, setDebounced] = useState(value);\n  useEffect(() => {\n    const handler = setTimeout(() => setDebounced(value), delay);\n    return () => clearTimeout(handler);\n  }, [value, delay]);\n  return debounced;\n}\n",
                    "resources": ["React.dev: Reusing Logic with Custom Hooks"],
                },
            ],
        },
        {
            "stage_number": 4,
            "stage_name": "Intermediate React",
            "description": "Context API, state management, client-side routing, data fetching, loading & error states, and form validation.",
            "lessons": [
                {
                    "title": "Context API & Prop Drilling Elimination",
                    "topic": "createContext, Provider, useContext & Context Splitting",
                    "summary": "Share global data across deep component trees without prop drilling, optimizing against context re-render cascades.",
                    "challenge": "Why does updating a Context value cause all consumer components to re-render? How do you split state and dispatch contexts to prevent unnecessary updates?",
                    "diagnostic": "How does context splitting prevent leaf components from re-rendering when unrelated state changes?",
                    "objective": "Implement scalable context providers with split state and dispatcher contracts.",
                    "prereqs": ["Custom hooks"],
                    "starter_code": "const StateContext = createContext();\nconst DispatchContext = createContext();\n",
                    "resources": ["React.dev: Passing Data Deeply with Context"],
                },
                {
                    "title": "Data Fetching, Loading & Error States",
                    "topic": "Async State Machines, SWR / React Query Concepts",
                    "summary": "Handle asynchronous network lifecycles cleanly with loading spinners, error boundaries, and optimistic updates.",
                    "challenge": "Design an async state machine (idle, loading, success, error) for data fetching that handles network drops and retries gracefully.",
                    "diagnostic": "What is cache invalidation in client-side data fetching libraries?",
                    "objective": "Build resilient asynchronous state handling with clean boundary states.",
                    "prereqs": ["useEffect and custom hooks"],
                    "starter_code": "type State = { status: 'idle' | 'loading' | 'success' | 'error'; data?: any; error?: Error };\n",
                    "resources": ["TanStack Query Documentation"],
                },
                {
                    "title": "Client-Side Routing & Navigation",
                    "topic": "Browser History, Route Layouts & Protected Routes",
                    "summary": "Master client-side routing, URL parameters, nested layouts, and auth-protected routes.",
                    "challenge": "How does client-side routing intercept URL navigation without full page reloads, and how do you implement a robust ProtectedRoute component?",
                    "diagnostic": "What is the difference between client-side routing and server-side page routing?",
                    "objective": "Structure nested layouts and role-based protected route wrappers.",
                    "prereqs": ["Component composition"],
                    "starter_code": "function ProtectedRoute({ user, children }) {\n  if (!user) return <Navigate to='/login' replace />;\n  return children;\n}\n",
                    "resources": ["React Router Documentation"],
                },
            ],
        },
        {
            "stage_number": 5,
            "stage_name": "Advanced React",
            "description": "Fiber reconciler internals, performance profiling, code splitting, Suspense, error boundaries, accessibility, and security.",
            "lessons": [
                {
                    "title": "Fiber Reconciler & Rendering Behavior",
                    "topic": "Fiber Nodes, Work In Progress, Render Phase vs Commit Phase",
                    "summary": "Deep dive into how React Fiber breaks rendering into interruptible units of work.",
                    "challenge": "Walk me through how React's Fiber reconciler determines what DOM nodes need updating across re-renders. Explain the render phase vs commit phase.",
                    "diagnostic": "Why can the render phase be paused or aborted by React, while the commit phase must execute synchronously?",
                    "objective": "Master Fiber tree architecture and interruptible priority scheduling.",
                    "prereqs": ["Intermediate React"],
                    "starter_code": "// Fiber tree inspection and reconciliation invariants\n",
                    "resources": ["React Fiber Architecture by Andrew Clark"],
                },
                {
                    "title": "Code Splitting, Lazy Loading & Suspense",
                    "topic": "React.lazy, Dynamic Imports, Suspense Fallbacks & Chunking",
                    "summary": "Reduce initial bundle size from megabytes to kilobytes using dynamic imports and Suspense boundaries.",
                    "challenge": "How do dynamic imports with React.lazy allow Webpack/Vite to generate split chunks, and how does Suspense coordinate loading fallbacks?",
                    "diagnostic": "What happens if a lazy-loaded component fails to download due to a network error?",
                    "objective": "Implement route-based and component-based code splitting with Suspense.",
                    "prereqs": ["Build tooling fundamentals"],
                    "starter_code": "const HeavyChart = React.lazy(() => import('./HeavyChart'));\n<Suspense fallback={<Spinner />}>\n  <HeavyChart />\n</Suspense>\n",
                    "resources": ["React.dev: Code Splitting"],
                },
                {
                    "title": "Error Boundaries & Application Resilience",
                    "topic": "componentDidCatch, getDerivedStateFromError & Fail-Safe UI",
                    "summary": "Catch JavaScript errors anywhere in the child component tree and display graceful fallback interfaces.",
                    "challenge": "Why must Error Boundaries still be written as class components (or using specialized libraries)? What errors do Error Boundaries NOT catch?",
                    "diagnostic": "Do error boundaries catch errors inside async callbacks or event handlers?",
                    "objective": "Isolate catastrophic component crashes to prevent white-screen crashes.",
                    "prereqs": ["Component lifecycles"],
                    "starter_code": "class ErrorBoundary extends React.Component {\n  static getDerivedStateFromError(error) { return { hasError: true }; }\n  componentDidCatch(error, info) { logError(error, info); }\n}\n",
                    "resources": ["React.dev: Catching rendering errors with an error boundary"],
                },
            ],
        },
        {
            "stage_number": 6,
            "stage_name": "Real Projects",
            "description": "Building full applications incrementally, API contracts, auth tokens, reusable design systems, diagnosing real bugs, and architecture reviews.",
            "lessons": [
                {
                    "title": "Incremental Production App Architecture",
                    "topic": "Folder Architecture, Domain Modules & API Layer",
                    "summary": "Structure a real-world frontend project for scalability, testing, and team maintainability.",
                    "challenge": "How do you structure a production React application with 50+ screens to ensure features are self-contained and components remain reusable?",
                    "diagnostic": "Why should API network calls never be placed directly inside UI presentational components?",
                    "objective": "Architect scalable frontend modularity separating UI from business services.",
                    "prereqs": ["All previous stages"],
                    "starter_code": "# src/\n#   features/   (domain logic & screens)\n#   components/ (shared primitive design system)\n#   services/   (API client & auth)\n",
                    "resources": ["Bulletproof React Architecture Guide"],
                },
                {
                    "title": "Diagnosing Real-World Bugs & Performance Bottlenecks",
                    "topic": "React DevTools Profiler, Memory Leaks & Stale Closures",
                    "summary": "Profile re-render cascades using React DevTools, diagnose memory leaks, and fix elusive stale closures in async effects.",
                    "challenge": "Given a screen that stutters during fast typing in an input field, how do you use the React DevTools Profiler to identify which component is the culprit?",
                    "diagnostic": "What is a stale closure in JavaScript, and how does it manifest in a React hook?",
                    "objective": "Systematically diagnose and eliminate re-rendering bottlenecks and memory leaks.",
                    "prereqs": ["Performance hooks"],
                    "starter_code": "// Debugging profiling exercise\n",
                    "resources": ["React DevTools Profiler Documentation"],
                },
            ],
        },
        {
            "stage_number": 7,
            "stage_name": "Interview Readiness",
            "description": "Fundamental conceptual interview questions, scenario-based architecture, code-reading, debugging, and mock interview defense.",
            "lessons": [
                {
                    "title": "Core Conceptual Questions & Mental Models",
                    "topic": "Virtual DOM, State Batching, Closures & Reconciliation",
                    "summary": "Master answering top-tier technical interview questions on React fundamentals with authority.",
                    "challenge": "How does React 18 automatic batching work? Compare batching behavior in React 18 with React 17 across promises and timeouts.",
                    "diagnostic": "Does React 18 batch state updates inside setTimeout and Promise callbacks?",
                    "objective": "Deliver concise, authoritative answers on React core internals.",
                    "prereqs": ["Complete React journey"],
                    "starter_code": "// State batching interview demonstration\n",
                    "resources": ["React 18 Automatic Batching Release Notes"],
                },
                {
                    "title": "Frontend System Design & Project Explanation",
                    "topic": "Designing Infinite Feeds, State Cache & Defending Your Code",
                    "summary": "Design high-scale frontend systems (e.g. Infinite Scroll, Autocomplete, Real-time Dashboard) and explain your actual projects.",
                    "challenge": "Design an infinite-scroll feed (like Twitter or LinkedIn) in React: Address DOM node virtualization, scroll position restoration, caching, and network prefetching.",
                    "diagnostic": "Why does rendering 10,000 DOM nodes directly cause the browser to freeze, and how does windowing (react-window) solve it?",
                    "objective": "Ace frontend system design interviews and defend production architectural decisions.",
                    "prereqs": ["Production React Architecture"],
                    "starter_code": "// Virtualized windowing blueprint\n",
                    "resources": ["Frontend System Design Guide"],
                },
            ],
        },
    ],
    "python": [
        {
            "stage_number": 1,
            "stage_name": "Foundations",
            "description": "Python syntax, variables, data types, dynamic typing, control flow, functions, and standard data structures.",
            "lessons": [
                {
                    "title": "What is Python?",
                    "topic": "Python Overview, Philosophy & Use Cases",
                    "summary": "Understand what Python is, why it was created, and where it is used in industry.",
                    "challenge": "Why did Guido van Rossum design Python with readability as the primary goal? What does 'The Zen of Python' mean for everyday code decisions?",
                    "diagnostic": "Name three domains where Python is the dominant language choice and explain why it excels in each.",
                    "objective": "Understand Python's design philosophy, execution model, and industry applications.",
                    "prereqs": ["No prior experience required"],
                    "starter_code": "# Run this in any Python 3 interpreter\nimport this  # Prints the Zen of Python\nprint('Python version:', __import__('sys').version)\n",
                    "what_you_will_learn": [
                        "What Python is and why it was created",
                        "How Python's interpreter executes code",
                        "Where Python is used: AI/ML, web backends, scripting, data science",
                        "How to set up and run your first Python program",
                    ],
                    "key_takeaways": [
                        "Python is interpreted, dynamically typed, and garbage-collected",
                        "Python emphasizes readable, explicit code over clever one-liners",
                        "Python 3 is the only supported version (Python 2 is end-of-life)",
                    ],
                    "quick_check": {
                        "question": "What will `type(3.5)` return in Python?",
                        "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>"],
                        "answer": "<class 'float'>",
                    },
                    "resources": ["Python Official Docs: Getting Started", "Python Official Tutorial"],
                },
                {
                    "title": "Setup & First Program",
                    "topic": "Python Installation, REPL, and Hello World",
                    "summary": "Install Python 3, use the interactive REPL, and write your first Python script.",
                    "challenge": "What is the difference between running Python interactively (REPL) and running a .py script? When would you use each?",
                    "diagnostic": "What happens when you run `python hello.py` on the command line?",
                    "objective": "Successfully set up a Python development environment and run basic programs.",
                    "prereqs": ["What is Python?"],
                    "starter_code": "# Your first Python program\nprint('Hello, World!')\nname = input('What is your name? ')\nprint(f'Hello, {name}!')\n",
                    "what_you_will_learn": [
                        "How to install Python 3 and verify the installation",
                        "How to use the Python REPL interactively",
                        "How to write and run a .py script",
                        "How to use f-strings for string formatting",
                    ],
                    "key_takeaways": [
                        "Use `python3 --version` to verify your installation",
                        "The REPL (Read-Eval-Print Loop) is great for quick experiments",
                        "f-strings (f'Hello {name}') are the modern way to format Python strings",
                    ],
                    "quick_check": {
                        "question": "Which command runs a Python file named 'app.py'?",
                        "options": ["python app.py", "run app.py", "execute app.py"],
                        "answer": "python app.py",
                    },
                    "resources": ["Python Official Tutorial: Using the Interpreter"],
                },
                {
                    "title": "Variables & Data Types",
                    "topic": "Dynamic Typing, Built-in Types: int, float, str, bool, list, tuple, dict, set",
                    "summary": "Understand how Python's dynamic type system works and master the core built-in data types.",
                    "challenge": "What does 'dynamically typed' mean in Python? How does Python decide the type of a variable at runtime, and how do you inspect it?",
                    "diagnostic": "What will `type(3.5)` return? What about `type('hello')`? And `type([1, 2, 3])`?",
                    "objective": "Master all Python built-in types, understand dynamic typing, and use type() and isinstance() correctly.",
                    "prereqs": ["Setup & First Program"],
                    "starter_code": (
                        "name = 'Cyra'\n"
                        "age = 21\n"
                        "is_active = True\n"
                        "marks = [85, 92, 78]\n"
                        "print(type(name), type(age))  # <class 'str'> <class 'int'>\n"
                        "\n"
                        "# Type checking\n"
                        "print(isinstance(age, int))   # True\n"
                        "print(isinstance(age, float)) # False\n"
                        "\n"
                        "# Type conversion\n"
                        "score = '95'\n"
                        "print(int(score) + 5)  # 100\n"
                    ),
                    "what_you_will_learn": [
                        "What variables are and how to use them in Python",
                        "Common data types (int, float, str, bool, list, tuple, dict, set)",
                        "Type checking with type() and isinstance()",
                        "Type conversion between compatible types",
                    ],
                    "key_takeaways": [
                        "Variables store values and can change over time",
                        "Python has built-in types like int, float, str, bool, list, tuple, dict, set",
                        "Use type() to check a variable's type",
                        "Python is dynamically typed — you don't declare types, Python infers them",
                    ],
                    "quick_check": {
                        "question": "What will `type(3.5)` return?",
                        "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>"],
                        "answer": "<class 'float'>",
                    },
                    "resources": ["Python Official Docs: Built-in Types", "Python Tutorial: Introduction"],
                },
                {
                    "title": "Operators & Expressions",
                    "topic": "Arithmetic, Comparison, Logical & Bitwise Operators",
                    "summary": "Master Python's operator precedence, short-circuit evaluation, and walrus operator.",
                    "challenge": "Explain Python's short-circuit evaluation: when does `a and b` NOT evaluate `b`? What does the walrus operator `:=` do?",
                    "diagnostic": "What is the result of `10 // 3`, `10 % 3`, and `2 ** 8` in Python?",
                    "objective": "Write correct Python expressions using all operator categories.",
                    "prereqs": ["Variables & Data Types"],
                    "starter_code": (
                        "# Arithmetic operators\n"
                        "print(10 // 3)  # Integer division: 3\n"
                        "print(10 % 3)   # Modulo: 1\n"
                        "print(2 ** 8)   # Power: 256\n"
                        "\n"
                        "# Short-circuit evaluation\n"
                        "x = None\n"
                        "result = x or 'default'  # 'default' (x is falsy)\n"
                        "print(result)\n"
                        "\n"
                        "# Walrus operator (Python 3.8+)\n"
                        "data = [1, 2, 3, 4, 5]\n"
                        "if (n := len(data)) > 3:\n"
                        "    print(f'List has {n} elements')  # List has 5 elements\n"
                    ),
                    "what_you_will_learn": [
                        "Arithmetic operators: +, -, *, /, //, %, **",
                        "Comparison operators: ==, !=, <, >, <=, >=",
                        "Logical operators: and, or, not with short-circuit evaluation",
                        "The walrus operator := for assignment in expressions",
                    ],
                    "key_takeaways": [
                        "// is integer division, % is modulo, ** is exponentiation",
                        "and/or short-circuit: Python stops evaluating as soon as the result is determined",
                        "The walrus operator := assigns and returns a value in a single expression",
                    ],
                    "quick_check": {
                        "question": "What does `10 // 3` return in Python?",
                        "options": ["3", "3.33", "1"],
                        "answer": "3",
                    },
                    "resources": ["Python Official Docs: Expressions", "Python Operator Precedence Table"],
                },
            ],
        },
        {
            "stage_number": 2,
            "stage_name": "Core Python",
            "description": "Iterators, generators, comprehensions, decorators, context managers, and exception handling.",
            "lessons": [
                {
                    "title": "Iterators, Generators & Memory Streaming",
                    "topic": "__iter__, __next__, yield & Lazy Evaluation",
                    "summary": "Process massive datasets without out-of-memory crashes using generators and lazy evaluation.",
                    "challenge": "How does a generator function with 'yield' suspend execution state on the stack? Compare memory usage of reading a 10GB file with readlines() vs a generator.",
                    "diagnostic": "What exception signals the termination of an iterator in Python?",
                    "objective": "Build memory-efficient streaming pipelines using generator expressions.",
                    "prereqs": ["Foundations"],
                    "starter_code": "def stream_large_file(filepath):\n    with open(filepath, 'r') as f:\n        for line in f:\n            yield line.strip()\n",
                    "resources": ["Python Docs: Generators and Iterators"],
                },
                {
                    "title": "Decorators, Closures & First-Class Functions",
                    "topic": "Higher-Order Functions, functools.wraps & Parameterized Decorators",
                    "summary": "Write elegant decorators that preserve function signatures, metadata, and docstrings.",
                    "challenge": "How do closures retain outer scope variables in __closure__? Why must you always use @functools.wraps when authoring production decorators?",
                    "diagnostic": "What happens to a decorated function's __name__ and __doc__ if @functools.wraps is omitted?",
                    "objective": "Write robust logging, timing, and authentication decorators.",
                    "prereqs": ["Functions and scoping"],
                    "starter_code": "import functools\n\ndef retry(max_attempts=3):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            pass\n        return wrapper\n    return decorator\n",
                    "resources": ["Fluent Python: Decorators and Closures"],
                },
            ],
        },
        {
            "stage_number": 3,
            "stage_name": "Memory Model & GIL",
            "description": "CPython memory management, reference counting, cyclic garbage collection, and the Global Interpreter Lock.",
            "lessons": [
                {
                    "title": "CPython Memory Management & Garbage Collection",
                    "topic": "Reference Counting, PyMalloc, Generational GC & Table Bloat",
                    "summary": "Master CPython's reference counting mechanism and three-generation cyclic garbage collector.",
                    "challenge": "How does CPython detect and reclaim circular references (e.g. objA.child = objB, objB.parent = objA) that reference counting alone cannot free?",
                    "diagnostic": "How can you manually trigger or inspect garbage collection generations in Python?",
                    "objective": "Prevent memory leaks caused by circular references and unreleased event handlers.",
                    "prereqs": ["Core Python"],
                    "starter_code": "import gc\n# Inspect generation thresholds\nprint(gc.get_threshold())\n",
                    "resources": ["Python Developer Guide: Garbage Collection"],
                },
                {
                    "title": "The Global Interpreter Lock (GIL) Invariants",
                    "topic": "GIL Execution, Bytecode Opcode Stepping, CPU vs I/O Bound Concurrency",
                    "summary": "Understand the GIL's impact on multi-threaded CPU execution and when to use multiprocessing.",
                    "challenge": "Why does multi-threading in Python accelerate I/O-bound tasks but slow down CPU-bound tasks? When should you use multiprocessing or C-extensions?",
                    "diagnostic": "What does Python's GIL release when performing network requests or disk reads?",
                    "objective": "Architect high-performance concurrency respecting GIL boundaries.",
                    "prereqs": ["Operating system thread concepts"],
                    "starter_code": "# Demonstrating multi-threading vs multiprocessing on CPU tasks\n",
                    "resources": ["Understanding the Python GIL by David Beazley"],
                },
            ],
        },
        {
            "stage_number": 4,
            "stage_name": "Asyncio & Concurrency",
            "description": "Asynchronous event loops, coroutines, tasks, TaskGroups, non-blocking I/O, and threadpools.",
            "lessons": [
                {
                    "title": "Asyncio Event Loop & Cooperative Multitasking",
                    "topic": "Event Loop, Coroutines, Tasks & Non-Blocking Epoll/Kqueue",
                    "summary": "Handle 10,000+ concurrent network connections on a single OS thread using asyncio.",
                    "challenge": "How does Python's asyncio event loop schedule coroutines without preemptive OS thread switching? What happens if you call time.sleep() inside a coroutine?",
                    "diagnostic": "Why does a single blocking synchronous call stall an entire asyncio event loop?",
                    "objective": "Build high-throughput non-blocking services with asyncio.",
                    "prereqs": ["Generators and concurrency"],
                    "starter_code": "import asyncio\n\nasync def fetch_all(urls):\n    async with asyncio.TaskGroup() as tg:\n        tasks = [tg.create_task(fetch(u)) for u in urls]\n",
                    "resources": ["Python Official Docs: asyncio"],
                },
            ],
        },
        {
            "stage_number": 5,
            "stage_name": "Advanced Architecture",
            "description": "Metaclasses, dunder protocols, descriptors, type hinting, and structural pattern matching.",
            "lessons": [
                {
                    "title": "Descriptors & Metaclasses in Framework Design",
                    "topic": "__get__, __set__, type.__new__ & ORM Internals",
                    "summary": "Understand how modern frameworks like SQLAlchemy and Pydantic use descriptors and metaclasses.",
                    "challenge": "How does the descriptor protocol (__get__, __set__, __delete__) power Python properties, methods, and ORM column models?",
                    "diagnostic": "What is the difference between a data descriptor and a non-data descriptor in attribute lookup priority?",
                    "objective": "Author advanced domain libraries using descriptor protocols.",
                    "prereqs": ["Object-oriented Python"],
                    "starter_code": "class ValidatedString:\n    def __set_name__(self, owner, name): self.name = name\n    def __get__(self, obj, objtype=None): return obj.__dict__.get(self.name)\n    def __set__(self, obj, value):\n        if not isinstance(value, str): raise TypeError()\n        obj.__dict__[self.name] = value\n",
                    "resources": ["Python Docs: Descriptor HowTo Guide"],
                },
            ],
        },
        {
            "stage_number": 6,
            "stage_name": "Real Projects & Production",
            "description": "Packaging, virtual environments, Dockerization, logging, profiling, and production deployment.",
            "lessons": [
                {
                    "title": "Profiling & Production Performance Optimization",
                    "topic": "cProfile, py-spy, Memory Profiling & Vectorization",
                    "summary": "Profile production Python microservices to locate CPU and memory bottlenecks.",
                    "challenge": "Given a Python API endpoint responding in 2500ms, walk through how you would use cProfile, line_profiler, or py-spy to isolate the bottleneck without guessing.",
                    "diagnostic": "What is flame graph profiling?",
                    "objective": "Profile and optimize Python production services with empirical telemetry.",
                    "prereqs": ["Asyncio and standard library"],
                    "starter_code": "import cProfile\n# Profile critical section\n",
                    "resources": ["Python Profilers Documentation"],
                },
            ],
        },
        {
            "stage_number": 7,
            "stage_name": "Interview Readiness",
            "description": "Senior Python interview questions, scenario debugging, concurrency trade-offs, and architecture defense.",
            "lessons": [
                {
                    "title": "Senior Python Technical Interview Mastery",
                    "topic": "GIL, Memory Allocation, Asyncio vs Multiprocessing & Code Reading",
                    "summary": "Ace senior technical interview questions on Python internals, data structures, and architecture.",
                    "challenge": "How would you architect a Python service processing 5,000 webhook payloads per second with database writes and third-party API calls?",
                    "diagnostic": "How do you handle graceful shutdown (SIGTERM) in an asyncio service without dropping active transactions?",
                    "objective": "Confidently explain Python architectural trade-offs in high-stakes interviews.",
                    "prereqs": ["All stages"],
                    "starter_code": "# Production webhook consumer blueprint\n",
                    "resources": ["High Performance Python by Micha Gorelick"],
                },
            ],
        },
    ],
    "sql": [
        {
            "stage_number": 1,
            "stage_name": "Foundations",
            "description": "Relational data modeling, table schemas, primary and foreign keys, basic SELECT queries, and filtering.",
            "lessons": [
                {
                    "title": "Relational Modeling, Keys & Normalization",
                    "topic": "1NF, 2NF, 3NF, Primary Keys & Foreign Key Constraints",
                    "summary": "Design normalized relational schemas that guarantee data consistency and eliminate redundancy.",
                    "challenge": "Explain Third Normal Form (3NF). When is intentional denormalization justified in high-scale read-heavy applications?",
                    "diagnostic": "What anomaly occurs when a table violates 2NF?",
                    "objective": "Design clean 3NF database schemas with referential integrity.",
                    "prereqs": ["Basic database concepts"],
                    "starter_code": "CREATE TABLE users (\n    id SERIAL PRIMARY KEY,\n    email VARCHAR(255) UNIQUE NOT NULL\n);\n",
                    "resources": ["Database System Concepts: Relational Model"],
                },
            ],
        },
        {
            "stage_number": 2,
            "stage_name": "Core Queries & Joins",
            "description": "INNER, LEFT, RIGHT, FULL OUTER joins, self-joins, GROUP BY, HAVING, and aggregate functions.",
            "lessons": [
                {
                    "title": "Relational Joins & Execution Semantics",
                    "topic": "Hash Join, Merge Join, Nested Loops & Outer Joins",
                    "summary": "Master relational algebra joins and how database query engines choose join algorithms.",
                    "challenge": "How do Nested Loop Join, Hash Join, and Merge Join differ in algorithmic complexity? Under what data volume and index conditions does the query optimizer choose each?",
                    "diagnostic": "What is the difference between filtering inside a LEFT JOIN ON clause versus the WHERE clause?",
                    "objective": "Write optimal join queries and predict optimizer join mechanics.",
                    "prereqs": ["Foundations"],
                    "starter_code": "SELECT u.id, COUNT(o.id) \nFROM users u \nLEFT JOIN orders o ON u.id = o.user_id \nGROUP BY u.id;\n",
                    "resources": ["Use The Index, Luke: Joins"],
                },
            ],
        },
        {
            "stage_number": 3,
            "stage_name": "Indexing & B-Trees",
            "description": "B-Tree mechanics, composite indexes, the leftmost prefix rule, index selectivity, and partial indexes.",
            "lessons": [
                {
                    "title": "B-Tree Indexes & The Leftmost Prefix Rule",
                    "topic": "B-Tree Depth, Clustered vs Secondary Indexes & Composite Indexing",
                    "summary": "Design composite indexes that eliminate table scans for high-scale range and equality queries.",
                    "challenge": "Given a table with 50M rows and a query 'WHERE user_id = ? AND created_at > ? ORDER BY created_at', design the optimal composite index and explain why column ordering matters.",
                    "diagnostic": "Why can't a composite index on (A, B) be used to accelerate a query filtering solely on B?",
                    "objective": "Apply the leftmost prefix rule and eliminate sequential table scans.",
                    "prereqs": ["Core Queries"],
                    "starter_code": "CREATE INDEX idx_user_created ON orders (user_id, created_at);\n",
                    "resources": ["PostgreSQL Documentation: Index Types"],
                },
            ],
        },
        {
            "stage_number": 4,
            "stage_name": "Transactions & MVCC",
            "description": "ACID properties, isolation levels (Read Committed, Repeatable Read, Serializable), locks, and deadlocks.",
            "lessons": [
                {
                    "title": "ACID Properties & Multi-Version Concurrency Control (MVCC)",
                    "topic": "Isolation Levels, Dirty Reads, Phantom Reads & Row Locks",
                    "summary": "Understand how MVCC allows concurrent reads without blocking writes using row versions.",
                    "challenge": "How does MVCC eliminate read locks during write operations? Explain how a deadlock occurs between two transactions and how database engines detect and break it.",
                    "diagnostic": "What anomaly can still occur under Repeatable Read that only Serializable isolation eliminates?",
                    "objective": "Design safe concurrent database transactions that prevent deadlocks.",
                    "prereqs": ["Indexing"],
                    "starter_code": "BEGIN;\nSELECT * FROM accounts WHERE id = 1 FOR UPDATE;\nCOMMIT;\n",
                    "resources": ["PostgreSQL Documentation: Concurrency Control"],
                },
            ],
        },
        {
            "stage_number": 5,
            "stage_name": "Advanced SQL & Analytics",
            "description": "Window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD), CTEs, and recursive queries.",
            "lessons": [
                {
                    "title": "Window Functions & Analytical Partitions",
                    "topic": "OVER (PARTITION BY ... ORDER BY ...), Running Totals & Ranking",
                    "summary": "Perform complex analytical computations across partitioned data subsets without multiple group-by self-joins.",
                    "challenge": "Write a query to find the top 3 highest-earning employees per department using DENSE_RANK(). Why is a window function superior to correlated subqueries?",
                    "diagnostic": "Does a window function collapse rows like a GROUP BY aggregation does?",
                    "objective": "Write advanced analytical window queries.",
                    "prereqs": ["Core Queries"],
                    "starter_code": "SELECT name, dept, salary, \n       DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) as rank\nFROM employees;\n",
                    "resources": ["PostgreSQL Documentation: Window Functions"],
                },
            ],
        },
        {
            "stage_number": 6,
            "stage_name": "Query Optimization & EXPLAIN",
            "description": "Reading EXPLAIN ANALYZE execution plans, identifying bottlenecks, table partitioning, and connection pooling.",
            "lessons": [
                {
                    "title": "Diagnosing Query Plans with EXPLAIN ANALYZE",
                    "topic": "Cost Estimation, Seq Scan vs Index Scan, Buffers & Memory Spills",
                    "summary": "Diagnose slow queries using EXPLAIN ANALYZE execution trees.",
                    "challenge": "Walk through how to interpret an EXPLAIN ANALYZE output: What is the difference between an Index Scan, Index Only Scan, and Bitmap Index Scan?",
                    "diagnostic": "What causes an external Sort Spill to Disk in a query plan?",
                    "objective": "Optimize database queries using real execution plan metrics.",
                    "prereqs": ["Indexing and Transactions"],
                    "starter_code": "EXPLAIN (ANALYZE, BUFFERS) \nSELECT * FROM orders WHERE user_id = 42;\n",
                    "resources": ["PostgreSQL Documentation: Using EXPLAIN"],
                },
            ],
        },
        {
            "stage_number": 7,
            "stage_name": "Interview Readiness",
            "description": "Senior database interview questions, schema design trade-offs, sharding, replication, and query debugging.",
            "lessons": [
                {
                    "title": "Senior SQL & Database Architecture Interview Defense",
                    "topic": "Read Replicas, Connection Pooling (PgBouncer), Sharding & High Availability",
                    "summary": "Ace database architecture and performance interview questions.",
                    "challenge": "How do you scale a relational database that has reached write limits on the primary node? Discuss vertical scaling, read replicas, partitioning, and application-level sharding.",
                    "diagnostic": "What is replication lag and how does it cause stale reads on replica nodes?",
                    "objective": "Defend relational database scalability in engineering interviews.",
                    "prereqs": ["All stages"],
                    "starter_code": "// Scalability blueprint\n",
                    "resources": ["Designing Data-Intensive Applications by Martin Kleppmann"],
                },
            ],
        },
    ],
}


def _generate_generic_dynamic_skill_stages(skill_name: str) -> List[Dict[str, Any]]:
    """
    Synthesizes a tailored, 7-stage pedagogical curriculum for ANY technical skill
    (e.g., Java, FastAPI, Docker, Kubernetes, Go, TypeScript, Machine Learning, etc.)
    using systematic software engineering curriculum principles.
    """
    clean = skill_name.strip()
    return [
        {
            "stage_number": 1,
            "stage_name": "Foundations",
            "description": f"Core syntax, execution runtime, mental models, and foundational building blocks of {clean}.",
            "lessons": [
                {
                    "title": f"What {clean} Is & Architectural Motivation",
                    "topic": f"Runtime Architecture, Philosophy & Ecosystem of {clean}",
                    "summary": f"Understand the core problem {clean} solves, its execution lifecycle, and why it is chosen in modern software engineering.",
                    "challenge": f"Why does {clean} exist, and what core architectural problem or trade-off does it address compared to alternatives?",
                    "diagnostic": f"Under what runtime conditions or requirements is {clean} the optimal choice?",
                    "objective": f"Master the fundamental philosophy and execution semantics of {clean}.",
                    "prereqs": ["General programming fundamentals"],
                    "starter_code": f"# {clean} foundational syntax & setup\n",
                    "resources": [f"Official {clean} Documentation: Getting Started"],
                },
                {
                    "title": f"{clean} Core Primitives & Syntax Invariants",
                    "topic": f"Data Types, Scoping & Execution Mechanics in {clean}",
                    "summary": f"Master the fundamental syntax, typing, memory allocation, and data representation in {clean}.",
                    "challenge": f"How does {clean} handle variables, state mutation, and scope boundaries? Walk through a concrete example.",
                    "diagnostic": f"What common beginner pitfalls or syntax misconceptions occur in {clean}?",
                    "objective": f"Write idiomatic, error-free code adhering to {clean} best practices.",
                    "prereqs": [f"{clean} Foundations"],
                    "starter_code": f"# {clean} idiom demonstration\n",
                    "resources": [f"Official {clean} Language Guide"],
                },
            ],
        },
        {
            "stage_number": 2,
            "stage_name": "Core Concepts",
            "description": f"Standard library, control flow, functions, modularity, and error handling in {clean}.",
            "lessons": [
                {
                    "title": f"Modularity, Packaging & Code Organization in {clean}",
                    "topic": f"Modules, Packages, Dependency Invariants & Contracts",
                    "summary": f"Structure modular codebases with clean boundary contracts and dependency management in {clean}.",
                    "challenge": f"How do you organize a large-scale project in {clean} to prevent circular dependencies and enforce encapsulation?",
                    "diagnostic": f"How does {clean} resolve imports or package namespaces?",
                    "objective": f"Structure scalable multi-module architectures in {clean}.",
                    "prereqs": [f"{clean} Foundations"],
                    "starter_code": f"# Modular architecture blueprint for {clean}\n",
                    "resources": [f"{clean} Code Organization Standards"],
                },
                {
                    "title": f"Error Handling & Boundary Invariants in {clean}",
                    "topic": f"Exceptions, Return Codes & Graceful Failure in {clean}",
                    "summary": f"Enforce robust error handling, boundary validation, and fail-safe recovery patterns in {clean}.",
                    "challenge": f"How does {clean} model and handle errors (e.g. exceptions vs explicit Result types)? How do you prevent unhandled crashes?",
                    "diagnostic": f"What is the difference between recoverable errors and fatal panic/runtime crashes in {clean}?",
                    "objective": f"Implement fail-safe error recovery and logging in {clean}.",
                    "prereqs": ["Core syntax"],
                    "starter_code": f"# Resilient error handling in {clean}\n",
                    "resources": [f"{clean} Error Handling Practices"],
                },
            ],
        },
        {
            "stage_number": 3,
            "stage_name": "Deep-Dive & Specialized Invariants",
            "description": f"Memory allocation, concurrency invariants, resource lifecycles, and internal execution mechanics of {clean}.",
            "lessons": [
                {
                    "title": f"Memory Lifecycle & State Management in {clean}",
                    "topic": f"Heap vs Stack, Garbage Collection / Ownership & Allocation in {clean}",
                    "summary": f"Analyze how {clean} manages memory, allocates resources, and reclaims dead objects or buffers.",
                    "challenge": f"How does {clean} manage memory allocation under high throughput? What causes memory leaks or unexpected heap retention?",
                    "diagnostic": f"How do you inspect or profile memory consumption in {clean}?",
                    "objective": f"Master memory efficiency and prevent resource leaks in {clean}.",
                    "prereqs": [f"Core {clean}"],
                    "starter_code": f"# Memory optimization pattern in {clean}\n",
                    "resources": [f"{clean} Memory & Runtime Internals"],
                },
                {
                    "title": f"Concurrency, Threading & Asynchronous Execution in {clean}",
                    "topic": f"Threads, Coroutines, Event Loops & Synchronization in {clean}",
                    "summary": f"Master concurrent execution models, thread-safety, race condition prevention, and non-blocking I/O in {clean}.",
                    "challenge": f"How does {clean} execute concurrent workloads? How do you prevent race conditions, deadlocks, and thread contention?",
                    "diagnostic": f"What synchronization primitives (mutexes, channels, locks, event loops) does {clean} provide?",
                    "objective": f"Architect safe concurrent and asynchronous workflows in {clean}.",
                    "prereqs": ["Memory Lifecycle"],
                    "starter_code": f"# Concurrency synchronization blueprint in {clean}\n",
                    "resources": [f"{clean} Concurrency Guide"],
                },
            ],
        },
        {
            "stage_number": 4,
            "stage_name": "Intermediate Architecture",
            "description": f"Design patterns, interface contracts, dependency injection, and data persistence with {clean}.",
            "lessons": [
                {
                    "title": f"Architectural Design Patterns in {clean}",
                    "topic": f"Creational, Structural & Behavioral Patterns in {clean}",
                    "summary": f"Apply proven software engineering design patterns idiomatic to the {clean} ecosystem.",
                    "challenge": f"Which design patterns (e.g. Factory, Strategy, Observer, Dependency Injection) are most essential in {clean}, and why?",
                    "diagnostic": f"What is an anti-pattern commonly observed in {clean} codebases?",
                    "objective": f"Apply idiomatic architectural patterns to decouple system components.",
                    "prereqs": ["Deep-Dive Invariants"],
                    "starter_code": f"# Idiomatic design pattern implementation in {clean}\n",
                    "resources": [f"Design Patterns in {clean}"],
                },
                {
                    "title": f"API Integration & Data Flow in {clean}",
                    "topic": f"Serialization, HTTP/gRPC Contracts & Persistence in {clean}",
                    "summary": f"Connect {clean} services to databases, caches, and external network services securely.",
                    "challenge": f"How do you structure data serialization, validation, and database connection pooling in {clean}?",
                    "diagnostic": f"How do you handle connection pool exhaustion under sudden traffic spikes?",
                    "objective": f"Build resilient external integration and persistence layers.",
                    "prereqs": ["Design Patterns"],
                    "starter_code": f"# External integration layer in {clean}\n",
                    "resources": [f"{clean} Integration Best Practices"],
                },
            ],
        },
        {
            "stage_number": 5,
            "stage_name": "Advanced & Performance Engineering",
            "description": f"Performance profiling, bottleneck diagnosis, caching, and security hardening in {clean}.",
            "lessons": [
                {
                    "title": f"Profiling & Bottleneck Optimization in {clean}",
                    "topic": f"CPU Profiling, Latency Analysis & Benchmarking in {clean}",
                    "summary": f"Locate and eliminate runtime bottlenecks using empirical profiling tools.",
                    "challenge": f"When a service built with {clean} experiences severe latency spikes under production traffic, how do you profile and isolate the root cause?",
                    "diagnostic": f"What profiling tools and metrics are standard in the {clean} ecosystem?",
                    "objective": f"Profile and optimize execution speed and resource throughput.",
                    "prereqs": ["Intermediate Architecture"],
                    "starter_code": f"# Profiling and benchmark harness in {clean}\n",
                    "resources": [f"Performance Tuning in {clean}"],
                },
                {
                    "title": f"Security Invariants & Vulnerability Prevention in {clean}",
                    "topic": f"Input Sanitization, Authentication & Attack Surfaces in {clean}",
                    "summary": f"Protect applications from injection, deserialization vulnerabilities, and credential leakage.",
                    "challenge": f"What are the most dangerous security vulnerabilities encountered in {clean} applications, and how do you mitigate them at compile or runtime?",
                    "diagnostic": f"How do you audit dependencies and supply chain security for {clean}?",
                    "objective": f"Enforce production security boundaries and safe input sanitization.",
                    "prereqs": ["Profiling"],
                    "starter_code": f"# Security validation and sanitization pattern in {clean}\n",
                    "resources": [f"{clean} Security Hardening Standards"],
                },
            ],
        },
        {
            "stage_number": 6,
            "stage_name": "Real Projects & Production Deployment",
            "description": f"Building production-grade applications, containerization, CI/CD, and monitoring for {clean}.",
            "lessons": [
                {
                    "title": f"Containerization & CI/CD Pipelines for {clean}",
                    "topic": f"Docker Multi-Stage Builds, Automated Testing & Deployment",
                    "summary": f"Package and deploy {clean} services using lightweight, reproducible container environments.",
                    "challenge": f"How do you structure an optimal Dockerfile and automated CI pipeline for a {clean} application to minimize image size and build times?",
                    "diagnostic": f"Why should dev dependencies and build toolchains be excluded from production container images?",
                    "objective": f"Ship production-ready containers and automated test pipelines.",
                    "prereqs": ["All previous stages"],
                    "starter_code": f"# Production Dockerfile blueprint for {clean}\n",
                    "resources": [f"Container Best Practices for {clean}"],
                },
                {
                    "title": f"Observability, Telemetry & Telemetry Invariants in {clean}",
                    "topic": f"Structured Logging, Metrics, Tracing & Health Checks",
                    "summary": f"Instrument {clean} applications with structured logs, OpenTelemetry traces, and Prometheus metrics.",
                    "challenge": f"What metrics and telemetry signals are critical to monitor {clean} service health, error rates, and saturation in production?",
                    "diagnostic": f"What is the difference between RED metrics (Rate, Errors, Duration) and USE metrics (Utilization, Saturation, Errors)?",
                    "objective": f"Instrument production services with comprehensive observability.",
                    "prereqs": ["Containerization"],
                    "starter_code": f"# Structured logging and metrics setup in {clean}\n",
                    "resources": [f"Observability in {clean}"],
                },
            ],
        },
        {
            "stage_number": 7,
            "stage_name": "Interview Readiness",
            "description": f"Senior engineering interview questions, system design trade-offs, code walkthroughs, and technical defense.",
            "lessons": [
                {
                    "title": f"Senior Technical Interview Conceptual Mastery in {clean}",
                    "topic": f"Core Invariants, Deep Questions & Code Analysis in {clean}",
                    "summary": f"Prepare to articulate complex {clean} internals and architectural choices with crisp authority.",
                    "challenge": f"How would you explain the core design philosophy, trade-offs, and scaling limits of {clean} to a Principal Engineer in an interview?",
                    "diagnostic": f"What question would an interviewer ask to test whether you truly understand {clean} or just memorized syntax?",
                    "objective": f"Defend technical decisions and demonstrate deep senior mastery of {clean}.",
                    "prereqs": ["Full curriculum"],
                    "starter_code": f"# Technical interview scenario solution in {clean}\n",
                    "resources": [f"Technical Interview Questions: {clean}"],
                },
                {
                    "title": f"System Architecture & Scaling Scenarios with {clean}",
                    "topic": f"Designing Scalable Systems & High-Volume Workloads with {clean}",
                    "summary": f"Architect and defend high-scale systems utilizing {clean} under surging traffic conditions.",
                    "challenge": f"Design a high-throughput, low-latency system utilizing {clean}. Address horizontal scaling, failover, persistence, and caching.",
                    "diagnostic": f"What is the first bottleneck that will fail in your design when traffic increases by 100x?",
                    "objective": f"Ace system design and architecture interviews featuring {clean}.",
                    "prereqs": ["Conceptual Mastery"],
                    "starter_code": f"# High-scale architecture blueprint using {clean}\n",
                    "resources": [f"High Scale Architecture Patterns with {clean}"],
                },
            ],
        },
    ]


def build_skill_learning_path(
    db: Session,
    skill_name: str,
    current_user: User,
) -> SkillLearningPathResponse:
    """
    Constructs a complete, 7-stage structured curriculum for ANY technical skill:
    - Queries verified candidate progress from PostgreSQL TeachingProgress
    - Connects candidate GitHub repositories where this skill is demonstrated
    - Queries prerequisites and related skills
    - Supports diagnostic assessments to jump forward
    """
    key = skill_name.strip().lower()
    norm_name = skill_name.strip()

    # Normalize common aliases before curriculum lookup
    _SKILL_ALIASES: Dict[str, str] = {
        "react.js": "react",
        "reactjs": "react",
        "python3": "python",
        "python 3": "python",
        "node.js": "nodejs",
        "nodejs": "nodejs",
        "javascript": "javascript",
        "js": "javascript",
        "typescript": "typescript",
        "ts": "typescript",
        "sql": "sql",
        "mysql": "sql",
        "postgresql": "sql",
    }
    normalized_key = _SKILL_ALIASES.get(key, key)

    # 1. Exact match first (prevents "react" matching when "python" is requested)
    raw_stages = CURATED_SKILL_CURRICULA.get(normalized_key)
    if raw_stages:
        norm_name = normalized_key.title()
    else:
        # 2. Prefix/suffix match — but ONLY if no other curated key is a more-exact prefix
        for cur_key, stages_data in CURATED_SKILL_CURRICULA.items():
            if cur_key == normalized_key:
                raw_stages = stages_data
                norm_name = cur_key.title()
                break
            # Allow "react" to match "react native" but NOT allow "python" to match "react"
            if normalized_key.startswith(cur_key) or cur_key.startswith(normalized_key):
                # Guard: don't cross-match unrelated skills
                if not any(
                    other in normalized_key
                    for other in CURATED_SKILL_CURRICULA.keys()
                    if other != cur_key and len(other) >= 4
                ):
                    raw_stages = stages_data
                    norm_name = cur_key.title()
                    break

    if not raw_stages:
        raw_stages = _generate_generic_dynamic_skill_stages(norm_name)

    # Fetch candidate progress from PostgreSQL
    progress_records = (
        db.query(TeachingProgress)
        .filter(TeachingProgress.candidate_id == current_user.id)
        .all()
    )
    status_map = {p.lesson_id: p.status for p in progress_records}
    stage_map = {p.lesson_id: p.current_stage for p in progress_records}

    # Fetch verified candidate projects
    learner_profile = build_learner_knowledge_profile(db, current_user)
    connected_projects = [
        p for p in learner_profile.verified_projects
        if any(norm_name.lower() in str(t).lower() for t in p.get("technologies", []))
    ]

    built_stages: List[SkillCurriculumStage] = []
    total_lessons_count = 0
    demonstrated_count = 0
    recommended_start = None

    for st_data in raw_stages:
        stage_num = st_data["stage_number"]
        stage_name = st_data["stage_name"]
        stage_desc = st_data["description"]
        built_lessons: List[TeachingLesson] = []

        for l_idx, l_raw in enumerate(st_data["lessons"]):
            lesson_id = f"skill-{_slugify(norm_name)}-s{stage_num}-l{l_idx+1}-{_slugify(l_raw['title'])}"
            total_lessons_count += 1

            status = status_map.get(lesson_id, "not_started")
            current_stage = stage_map.get(lesson_id, "objective")
            is_demonstrated = status in ("completed", "mastered", "demonstrated_understanding")
            if is_demonstrated:
                demonstrated_count += 1
            elif not recommended_start:
                recommended_start = lesson_id

            # Retrieve resources
            resources_list = retrieve_teaching_resources_for_lesson(
                concept_title=f"{norm_name} {l_raw['topic']}",
                candidate_projects=connected_projects,
                limit=3,
            )
            res_dicts = [r.model_dump() for r in resources_list]

            lesson = TeachingLesson(
                id=lesson_id,
                title=f"{norm_name} • {l_raw['title']}",
                topic=l_raw["topic"],
                difficulty="Easy to Medium" if stage_num <= 2 else ("Medium" if stage_num <= 4 else "Hard"),
                concept_summary=l_raw["summary"],
                challenge_question=l_raw["challenge"],
                grounding_source=f"Skill Track: {norm_name} (Stage {stage_num})",
                stage_number=stage_num,
                stage_name=stage_name,
                learning_objective=l_raw.get("objective", f"Master core principles of {l_raw['topic']}."),
                prerequisites=l_raw.get("prereqs", [f"{norm_name} fundamentals"]),
                diagnostic_question=l_raw.get("diagnostic", f"How do you handle edge cases in {l_raw['topic']}?"),
                source_references=l_raw.get("resources", [f"Official {norm_name} Documentation"]),
                starter_code=l_raw.get("starter_code", f"# {norm_name} implementation\n"),
                hints=[
                    f"Consider how {norm_name} handles lifecycle, memory, or state in this scenario.",
                    "Formulate a concrete example with expected input and output.",
                ],
                constraints=["Production reliability & correctness", "Sub-second execution / minimal overhead"],
                status=status,
                current_stage=current_stage,
                resources=res_dicts,
                is_demonstrated=is_demonstrated,
                candidate_project_connection=(
                    f"Demonstrated in your repository '{connected_projects[0].get('title')}'."
                    if connected_projects else None
                ),
            )
            built_lessons.append(lesson)

        built_stages.append(
            SkillCurriculumStage(
                stage_number=stage_num,
                stage_name=stage_name,
                description=stage_desc,
                estimated_hours=float(len(built_lessons) * 0.75),
                lessons=built_lessons,
            )
        )

    if not recommended_start and built_stages and built_stages[0].lessons:
        recommended_start = built_stages[0].lessons[0].id

    # Find related skills
    related = [
        s for s in ["React", "TypeScript", "Python", "FastAPI", "SQL", "Docker", "PostgreSQL", "Redis", "System Design"]
        if s.lower() != norm_name.lower()
    ][:4]

    summary_text = (
        f"Complete 7-stage learning journey for {norm_name}. "
        f"Master {norm_name} from foundations and core invariants up to advanced performance, "
        f"production implementation, and technical interview defense."
    )

    # Validate that the stage order is well-formed before returning
    validate_topic_sequence(built_stages)

    return SkillLearningPathResponse(
        skill_name=norm_name,
        normalized_skill=_slugify(norm_name),
        summary=summary_text,
        prerequisites=["Core programming concepts", "Version control fundamentals"],
        stages=built_stages,
        total_stages=len(built_stages),
        total_lessons=total_lessons_count,
        diagnostic_question=f"Take a diagnostic assessment to test your current knowledge of {norm_name} and skip introductory stages.",
        demonstrated_lessons_count=demonstrated_count,
        recommended_start_lesson_id=recommended_start,
        connected_projects=connected_projects,
        related_skills=related,
    )


# ── TOPIC SEQUENCE VALIDATOR ──────────────────────────────────────────────────

# Canonical stage-name order pattern (each entry is a lowercase substring that
# must appear in the stage name at that position or later in the curriculum).
_STAGE_ORDER_PATTERNS = ["foundation", "core", "intermediate", "advanced", "project", "assessment"]

# Stage names we accept as "assessment-like" even when the word 'assessment' isn't present
_ASSESSMENT_ALIASES = {"interview readiness", "interview", "review", "assessment"}


def validate_topic_sequence(stages: List) -> None:
    """
    Asserts that the curriculum stages follow a logically ascending order.

    Primary check: stage_number values must be non-decreasing.  This catches
    outright shuffles (stage 5 before stage 2) regardless of stage name.

    Secondary check (name-based): if every stage name matches one of the six
    canonical patterns (foundation, core, intermediate, advanced, project,
    assessment/interview), their keyword positions must also be non-decreasing.
    When stage names are skill-specific (e.g. "Asyncio & Concurrency",
    "Hooks", "Memory Model & GIL") the keyword check is skipped so that rich,
    curated curricula are never rejected for using descriptive names.

    Args:
        stages: list of SkillCurriculumStage objects (or dicts with
                stage_number / stage_name keys).
    """
    if not stages:
        return  # Empty curriculum is fine

    # ── Primary: stage_number must be non-decreasing ──────────────────────────
    stage_numbers: List[int] = []
    stage_names: List[str] = []
    for s in stages:
        num = (
            s.stage_number
            if hasattr(s, "stage_number")
            else s.get("stage_number", 0)
        )
        name = (
            s.stage_name
            if hasattr(s, "stage_name")
            else s.get("stage_name", "")
        )
        stage_numbers.append(int(num))
        stage_names.append(str(name).lower().strip())

    for idx in range(1, len(stage_numbers)):
        assert stage_numbers[idx] >= stage_numbers[idx - 1], (
            f"Curriculum stage_number order violation: stage_number {stage_numbers[idx - 1]} "
            f"('{stage_names[idx - 1]}') appears before stage_number {stage_numbers[idx]} "
            f"('{stage_names[idx]}'), violating the required ascending stage order."
        )

    # ── Secondary: keyword-order check only when all names map to canonical ──
    def _canonical_index(name: str) -> Optional[int]:
        for i, pattern in enumerate(_STAGE_ORDER_PATTERNS):
            if pattern in name:
                return i
        for alias in _ASSESSMENT_ALIASES:
            if alias in name:
                return len(_STAGE_ORDER_PATTERNS) - 1
        return None  # Unknown name → skip keyword check

    positions: List[Optional[int]] = [_canonical_index(n) for n in stage_names]
    all_known = all(p is not None for p in positions)

    if all_known:
        for idx in range(1, len(positions)):
            assert positions[idx] >= positions[idx - 1], (  # type: ignore[operator]
                f"Curriculum stage order violation: '{stage_names[idx - 1]}' (canonical pos {positions[idx - 1]}) "
                f"appears before '{stage_names[idx]}' (canonical pos {positions[idx]}), "
                f"violating the expected Foundations→Core→...→Assessment order."
            )

