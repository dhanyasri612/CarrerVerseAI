import re
from typing import Dict, List, Tuple, Optional, Set

# ==========================================
# 1. CANONICAL SKILL DEFINITIONS & CATEGORIES
# ==========================================

SKILL_CATEGORIES = [
    "Programming Languages",
    "Frameworks & Libraries",
    "Databases",
    "Cloud & DevOps",
    "Data Science & AI",
    "Tools & Technologies",
    "Soft & Professional Skills",
]

# Canonical Name -> (Category, [Aliases/Regexes])
CANONICAL_SKILL_DATABASE: Dict[str, Tuple[str, List[str]]] = {
    # ----------------------------------------------------
    # Programming Languages
    # ----------------------------------------------------
    "Python": (
        "Programming Languages",
        [r"^python\s*[0-9]*$", r"^python\s*programming$", r"^python3$", r"^py$"]
    ),
    "JavaScript": (
        "Programming Languages",
        [r"^javascript$", r"^js$", r"^es6$", r"^es20[0-9]{2}$", r"^vanilla\s*js$"]
    ),
    "TypeScript": (
        "Programming Languages",
        [r"^typescript$", r"^ts$"]
    ),
    "Java": (
        "Programming Languages",
        [r"^java$", r"^core\s*java$", r"^java\s*8$", r"^java\s*11$", r"^java\s*17$", r"^java\s*21$", r"^j2se$"]
    ),
    "C++": (
        "Programming Languages",
        [r"^c\+\+$", r"^cpp$", r"^c\s*plus\s*plus$"]
    ),
    "C": (
        "Programming Languages",
        [r"^c$", r"^c\s*programming$", r"^ansi\s*c$"]
    ),
    "C#": (
        "Programming Languages",
        [r"^c#$", r"^c\s*sharp$", r"^csharp$"]
    ),
    "Go": (
        "Programming Languages",
        [r"^go$", r"^golang$", r"^go\s*language$"]
    ),
    "Rust": (
        "Programming Languages",
        [r"^rust$", r"^rustlang$"]
    ),
    "PHP": (
        "Programming Languages",
        [r"^php$", r"^php\s*[0-9]*$"]
    ),
    "Ruby": (
        "Programming Languages",
        [r"^ruby$", r"^ruby\s*lang$"]
    ),
    "Swift": (
        "Programming Languages",
        [r"^swift$"]
    ),
    "Kotlin": (
        "Programming Languages",
        [r"^kotlin$"]
    ),
    "R": (
        "Programming Languages",
        [r"^r$", r"^r\s*programming$", r"^r\s*language$"]
    ),
    "SQL": (
        "Programming Languages",
        [r"^sql$", r"^structured\s*query\s*language$", r"^pl/sql$", r"^t-sql$"]
    ),
    "HTML": (
        "Programming Languages",
        [r"^html$", r"^html5$", r"^html\s*5$"]
    ),
    "CSS": (
        "Programming Languages",
        [r"^css$", r"^css3$", r"^css\s*3$", r"^sass$", r"^scss$"]
    ),
    "HTML / CSS": (
        "Programming Languages",
        [
            r"^html\s*/\s*css$",
            r"^html5\s*/\s*css3$",
            r"^html5\s*/\s*css$",
            r"^html\s*/\s*css3$",
            r"^html5/css3$",
            r"^html5/css$",
            r"^html/css3$",
            r"^html\s*and\s*css$",
            r"^html5\s*and\s*css3$",
        ]
    ),
    "Bash / Shell": (
        "Programming Languages",
        [r"^bash$", r"^shell$", r"^shell\s*scripting$", r"^zsh$", r"^sh$"]
    ),
    "Scala": (
        "Programming Languages",
        [r"^scala$"]
    ),
    "Dart": (
        "Programming Languages",
        [r"^dart$"]
    ),

    # ----------------------------------------------------
    # Frameworks & Libraries
    # ----------------------------------------------------
    "React": (
        "Frameworks & Libraries",
        [r"^react$", r"^react\.?js$", r"^reactjs$", r"^react\s*native$"]
    ),
    "Next.js": (
        "Frameworks & Libraries",
        [r"^next\.?js$", r"^nextjs$", r"^next\s*framework$"]
    ),
    "Node.js": (
        "Frameworks & Libraries",
        [r"^node\.?js$", r"^nodejs$", r"^node$"]
    ),
    "FastAPI": (
        "Frameworks & Libraries",
        [r"^fastapi$", r"^fast\s*api$"]
    ),
    "Django": (
        "Frameworks & Libraries",
        [r"^django$", r"^django\s*rest\s*framework$", r"^drf$"]
    ),
    "Flask": (
        "Frameworks & Libraries",
        [r"^flask$"]
    ),
    "Spring Boot": (
        "Frameworks & Libraries",
        [r"^spring\s*boot$", r"^spring$", r"^spring\s*framework$", r"^spring\s*mvc$"]
    ),
    "Express.js": (
        "Frameworks & Libraries",
        [r"^express$", r"^express\.?js$", r"^expressjs$"]
    ),
    "NestJS": (
        "Frameworks & Libraries",
        [r"^nestjs$", r"^nest\.?js$"]
    ),
    "Vue.js": (
        "Frameworks & Libraries",
        [r"^vue$", r"^vue\.?js$", r"^vuejs$", r"^vue\s*3$", r"^nuxt\.?js$"]
    ),
    "Angular": (
        "Frameworks & Libraries",
        [r"^angular$", r"^angular\.?js$", r"^angularjs$", r"^angular\s*[0-9]+$"]
    ),
    ".NET": (
        "Frameworks & Libraries",
        [r"^\.net$", r"^dotnet$", r"^\.net\s*core$", r"^asp\.net$", r"^asp\.net\s*core$"]
    ),
    "Tailwind CSS": (
        "Frameworks & Libraries",
        [r"^tailwind$", r"^tailwind\s*css$", r"^tailwindcss$"]
    ),
    "Bootstrap": (
        "Frameworks & Libraries",
        [r"^bootstrap$", r"^bootstrap\s*[0-9]*$"]
    ),
    "Redux": (
        "Frameworks & Libraries",
        [r"^redux$", r"^redux\s*toolkit$", r"^rtk$"]
    ),
    "GraphQL": (
        "Frameworks & Libraries",
        [r"^graphql$", r"^apollo\s*graphql$"]
    ),
    "REST APIs": (
        "Frameworks & Libraries",
        [r"^rest\s*api$", r"^rest\s*apis$", r"^restful\s*apis?$", r"^restful$", r"^api\s*development$"]
    ),
    "gRPC": (
        "Frameworks & Libraries",
        [r"^grpc$", r"^protocol\s*buffers$", r"^protobuf$"]
    ),
    "Pandas": (
        "Frameworks & Libraries",
        [r"^pandas$"]
    ),
    "NumPy": (
        "Frameworks & Libraries",
        [r"^numpy$"]
    ),
    "Scikit-Learn": (
        "Frameworks & Libraries",
        [r"^scikit-learn$", r"^scikit\s*learn$", r"^sklearn$"]
    ),
    "TensorFlow": (
        "Frameworks & Libraries",
        [r"^tensorflow$", r"^tf$", r"^keras$"]
    ),
    "PyTorch": (
        "Frameworks & Libraries",
        [r"^pytorch$", r"^torch$"]
    ),
    "Hugging Face": (
        "Frameworks & Libraries",
        [r"^hugging\s*face$", r"^huggingface$", r"^transformers\s*library$"]
    ),
    "OpenCV": (
        "Frameworks & Libraries",
        [r"^opencv$", r"^cv2$"]
    ),

    # ----------------------------------------------------
    # Databases
    # ----------------------------------------------------
    "PostgreSQL": (
        "Databases",
        [r"^postgresql$", r"^postgres$", r"^postgresql\s*database$", r"^postgres\s*db$"]
    ),
    "MySQL": (
        "Databases",
        [r"^mysql$", r"^mysql\s*db$"]
    ),
    "MongoDB": (
        "Databases",
        [r"^mongodb$", r"^mongo$", r"^mongodb\s*atlas$", r"^nosql\s*mongodb$"]
    ),
    "Redis": (
        "Databases",
        [r"^redis$", r"^redis\s*cache$"]
    ),
    "SQLite": (
        "Databases",
        [r"^sqlite$", r"^sqlite3$"]
    ),
    "Oracle DB": (
        "Databases",
        [r"^oracle\s*db$", r"^oracle\s*database$", r"^oracle\s*rdbms$"]
    ),
    "Microsoft SQL Server": (
        "Databases",
        [r"^sql\s*server$", r"^ms\s*sql$", r"^mssql$"]
    ),
    "Elasticsearch": (
        "Databases",
        [r"^elasticsearch$", r"^elastic\s*search$", r"^elk\s*stack$"]
    ),
    "DynamoDB": (
        "Databases",
        [r"^dynamodb$", r"^amazon\s*dynamodb$"]
    ),
    "Cassandra": (
        "Databases",
        [r"^cassandra$", r"^apache\s*cassandra$"]
    ),
    "Supabase": (
        "Databases",
        [r"^supabase$"]
    ),
    "Firebase": (
        "Databases",
        [r"^firebase$", r"^firestore$", r"^firebase\s*realtime\s*db$"]
    ),
    "Neo4j": (
        "Databases",
        [r"^neo4j$", r"^graph\s*database$"]
    ),

    # ----------------------------------------------------
    # Cloud & DevOps
    # ----------------------------------------------------
    "AWS": (
        "Cloud & DevOps",
        [r"^aws$", r"^amazon\s*web\s*services$", r"^aws\s*cloud$", r"^amazon\s*aws$"]
    ),
    "Azure": (
        "Cloud & DevOps",
        [r"^azure$", r"^microsoft\s*azure$", r"^azure\s*cloud$"]
    ),
    "Google Cloud Platform": (
        "Cloud & DevOps",
        [r"^gcp$", r"^google\s*cloud$", r"^google\s*cloud\s*platform$"]
    ),
    "Docker": (
        "Cloud & DevOps",
        [r"^docker$", r"^containerization$", r"^dockerfile$"]
    ),
    "Docker Compose": (
        "Cloud & DevOps",
        [r"^docker-compose$", r"^docker\s*compose$"]
    ),
    "Kubernetes": (
        "Cloud & DevOps",
        [r"^kubernetes$", r"^k8s$", r"^kubectl$", r"^helm$"]
    ),
    "Terraform": (
        "Cloud & DevOps",
        [r"^terraform$", r"^infrastructure\s*as\s*code$", r"^iac$"]
    ),
    "CI/CD": (
        "Cloud & DevOps",
        [r"^ci/cd$", r"^ci\s*/\s*cd$", r"^continuous\s*integration$", r"^continuous\s*deployment$"]
    ),
    "GitHub Actions": (
        "Cloud & DevOps",
        [r"^github\s*actions$", r"^gh\s*actions$"]
    ),
    "Jenkins": (
        "Cloud & DevOps",
        [r"^jenkins$"]
    ),
    "GitLab CI": (
        "Cloud & DevOps",
        [r"^gitlab\s*ci$", r"^gitlab\s*ci/cd$"]
    ),
    "Linux": (
        "Cloud & DevOps",
        [r"^linux$", r"^ubuntu$", r"^debian$", r"^centos$", r"^redhat$", r"^arch\s*linux$"]
    ),
    "Nginx": (
        "Cloud & DevOps",
        [r"^nginx$"]
    ),
    "Apache Kafka": (
        "Cloud & DevOps",
        [r"^kafka$", r"^apache\s*kafka$"]
    ),
    "Serverless / AWS Lambda": (
        "Cloud & DevOps",
        [r"^serverless$", r"^aws\s*lambda$", r"^lambda\s*functions?$"]
    ),

    # ----------------------------------------------------
    # Data Science & AI
    # ----------------------------------------------------
    "Machine Learning": (
        "Data Science & AI",
        [r"^machine\s*learning$", r"^ml$", r"^supervised\s*learning$", r"^unsupervised\s*learning$"]
    ),
    "Deep Learning": (
        "Data Science & AI",
        [r"^deep\s*learning$", r"^dl$", r"^neural\s*networks$", r"^artificial\s*neural\s*networks$", r"^ann$", r"^cnn$", r"^rnn$", r"^lstm$"]
    ),
    "Generative AI": (
        "Data Science & AI",
        [r"^generative\s*ai$", r"^genai$", r"^gen\s*ai$", r"^foundation\s*models$", r"^llms?$", r"^large\s*language\s*models?$", r"^chatgpt$", r"^diffusion\s*models?$"]
    ),
    "Prompt Engineering": (
        "Data Science & AI",
        [r"^prompt\s*engineering$", r"^prompting$", r"^prompt\s*design$", r"^chatgpt\s*prompting$"]
    ),
    "Transformers": (
        "Data Science & AI",
        [r"^transformers?$", r"^transformer\s*models?$", r"^bert$", r"^gpt$", r"^attention\s*mechanism$"]
    ),
    "Natural Language Processing": (
        "Data Science & AI",
        [r"^nlp$", r"^natural\s*language\s*processing$", r"^text\s*mining$", r"^spacy$", r"^nltk$"]
    ),
    "Computer Vision": (
        "Data Science & AI",
        [r"^computer\s*vision$", r"^cv$", r"^image\s*processing$", r"^object\s*detection$", r"^image\s*segmentation$"]
    ),
    "Data Science": (
        "Data Science & AI",
        [r"^data\s*science$", r"^data\s*analytics$", r"^data\s*analysis$", r"^exploratory\s*data\s*analysis$", r"^eda$"]
    ),
    "Data Engineering": (
        "Data Science & AI",
        [r"^data\s*engineering$", r"^etl$", r"^data\s*pipeline$", r"^spark$", r"^apache\s*spark$", r"^hadoop$"]
    ),
    "Data Visualization": (
        "Data Science & AI",
        [r"^data\s*visualization$", r"^matplotlib$", r"^seaborn$", r"^tableau$", r"^power\s*bi$", r"^plotly$"]
    ),
    "Reinforcement Learning": (
        "Data Science & AI",
        [r"^reinforcement\s*learning$", r"^rl$", r"^q-learning$"]
    ),
    "Data Structures & Algorithms": (
        "Data Science & AI",
        [r"^data\s*structures$", r"^algorithms$", r"^dsa$", r"^data\s*structures\s*(?:and|&)\s*algorithms$", r"^problem\s*solving\s*\(dsa\)$"]
    ),

    # ----------------------------------------------------
    # Tools & Technologies
    # ----------------------------------------------------
    "Git": (
        "Tools & Technologies",
        [r"^git$", r"^version\s*control$", r"^github$", r"^gitlab$", r"^bitbucket$"]
    ),
    "VS Code": (
        "Tools & Technologies",
        [r"^vs\s*code$", r"^visual\s*studio\s*code$", r"^vscode$"]
    ),
    "Postman": (
        "Tools & Technologies",
        [r"^postman$", r"^api\s*testing$"]
    ),
    "Jupyter Notebook": (
        "Tools & Technologies",
        [r"^jupyter$", r"^jupyter\s*notebook$", r"^google\s*colab$", r"^colab$"]
    ),
    "Jira": (
        "Tools & Technologies",
        [r"^jira$", r"^confluence$"]
    ),
    "Figma": (
        "Tools & Technologies",
        [r"^figma$", r"^ui/ux$", r"^ui\s*design$", r"^ux\s*design$"]
    ),
    "Webpack / Vite": (
        "Tools & Technologies",
        [r"^webpack$", r"^vite$", r"^npm$", r"^yarn$", r"^pnpm$"]
    ),
    "PyMuPDF": (
        "Tools & Technologies",
        [r"^pymupdf$", r"^fitz$"]
    ),

    # ----------------------------------------------------
    # Soft & Professional Skills
    # ----------------------------------------------------
    "Email Writing": (
        "Soft & Professional Skills",
        [r"^email\s*writing$", r"^business\s*email$", r"^email\s*etiquette$", r"^professional\s*email$"]
    ),
    "Presentation Skills": (
        "Soft & Professional Skills",
        [r"^presentation\s*skills$", r"^effective\s*presentation$", r"^public\s*speaking$", r"^slide\s*design$"]
    ),
    "Business Communication": (
        "Soft & Professional Skills",
        [r"^business\s*communication$", r"^workplace\s*communication$", r"^communication\s*skills?$", r"^professional\s*communication$"]
    ),
    "Technical Writing": (
        "Soft & Professional Skills",
        [r"^technical\s*writing$", r"^documentation$", r"^report\s*writing$"]
    ),
    "Problem Solving": (
        "Soft & Professional Skills",
        [r"^problem\s*solving$", r"^critical\s*thinking$", r"^analytical\s*skills?$", r"^troubleshooting$"]
    ),
    "Agile / Scrum": (
        "Soft & Professional Skills",
        [r"^agile$", r"^scrum$", r"^kanban$", r"^sprint\s*planning$", r"^scrum\s*master$"]
    ),
    "Project Management": (
        "Soft & Professional Skills",
        [r"^project\s*management$", r"^pmp$", r"^agile\s*project\s*management$"]
    ),
    "Leadership & Teamwork": (
        "Soft & Professional Skills",
        [r"^leadership$", r"^teamwork$", r"^collaboration$", r"^cross-functional\s*collaboration$", r"^mentoring$"]
    ),
    "Time Management": (
        "Soft & Professional Skills",
        [r"^time\s*management$", r"^organization\s*skills?$"]
    ),
}


# ==========================================
# 2. NORMALIZATION FUNCTIONS
# ==========================================

def clean_raw_skill_string(raw: str) -> str:
    """Strip punctuation and extra whitespace from raw skill name."""
    if not raw:
        return ""
    cleaned = raw.strip()
    # Remove leading/trailing bullet points or dashes
    cleaned = re.sub(r"^[\s•\-*#]+", "", cleaned)
    cleaned = re.sub(r"[\s•\-*#]+$", "", cleaned)
    # Remove trailing versions like "v3.2", "(intermediate)", "[beginner]"
    cleaned = re.sub(r"\s*v?[0-9]+(?:\.[0-9]+)*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\((?:basic|beginner|intermediate|advanced|expert|proficient)\)$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*\[(?:basic|beginner|intermediate|advanced|expert)\]$", "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def normalize_skill(raw_skill: str) -> Tuple[str, str]:
    """
    Normalize a raw skill string into its Canonical Name and Category.
    Returns: (canonical_name, category)
    """
    cleaned = clean_raw_skill_string(raw_skill)
    if not cleaned:
        return "", "Tools & Technologies"

    cleaned_lower = cleaned.lower()

    # 1. Direct Canonical Database Match (via Regex Aliases)
    for canonical_name, (category, regex_list) in CANONICAL_SKILL_DATABASE.items():
        # Exact match on canonical name
        if cleaned_lower == canonical_name.lower():
            return canonical_name, category
        
        # Regex alias match
        for pattern in regex_list:
            if re.match(pattern, cleaned_lower, re.IGNORECASE):
                return canonical_name, category

    # 2. Substring & Keyword Matching for known domains
    # AI / ML
    if any(k in cleaned_lower for k in ["prompt engineer", "prompt design"]):
        return "Prompt Engineering", "Data Science & AI"
    if any(k in cleaned_lower for k in ["generative ai", "genai", "gen ai", "large language model"]):
        return "Generative AI", "Data Science & AI"
    if any(k in cleaned_lower for k in ["machine learning", "supervised learning"]):
        return "Machine Learning", "Data Science & AI"
    if any(k in cleaned_lower for k in ["deep learning", "neural network"]):
        return "Deep Learning", "Data Science & AI"
    if any(k in cleaned_lower for k in ["data science", "data analytic"]):
        return "Data Science", "Data Science & AI"
    
    # Cloud
    if "aws" in cleaned_lower or "amazon web service" in cleaned_lower:
        return "AWS", "Cloud & DevOps"
    if "azure" in cleaned_lower:
        return "Azure", "Cloud & DevOps"
    if "google cloud" in cleaned_lower or "gcp" in cleaned_lower:
        return "Google Cloud Platform", "Cloud & DevOps"
    if "docker" in cleaned_lower:
        return "Docker", "Cloud & DevOps"
    if "kubernetes" in cleaned_lower or "k8s" in cleaned_lower:
        return "Kubernetes", "Cloud & DevOps"
    
    # Databases
    if "postgres" in cleaned_lower:
        return "PostgreSQL", "Databases"
    if "mysql" in cleaned_lower:
        return "MySQL", "Databases"
    if "mongo" in cleaned_lower:
        return "MongoDB", "Databases"
    if "redis" in cleaned_lower:
        return "Redis", "Databases"
    
    # Programming Languages
    if cleaned_lower.startswith("python"):
        return "Python", "Programming Languages"
    if cleaned_lower.startswith("java") and "script" not in cleaned_lower:
        return "Java", "Programming Languages"
    if "javascript" in cleaned_lower:
        return "JavaScript", "Programming Languages"
    if "typescript" in cleaned_lower:
        return "TypeScript", "Programming Languages"
    if cleaned_lower in ["c++", "cpp"]:
        return "C++", "Programming Languages"
    if cleaned_lower in ["c#", "csharp", ".net"]:
        return "C#", "Programming Languages"
    
    # Soft skills
    if "email writing" in cleaned_lower or "business email" in cleaned_lower:
        return "Email Writing", "Soft & Professional Skills"
    if "presentation" in cleaned_lower or "public speaking" in cleaned_lower:
        return "Presentation Skills", "Soft & Professional Skills"
    if "communication" in cleaned_lower:
        return "Business Communication", "Soft & Professional Skills"

    # 3. Fallback: Clean Title Case formatting & Heuristic Category
    # Determine fallback category
    fallback_category = "Tools & Technologies"
    if any(term in cleaned_lower for term in ["framework", "library", "sdk", "api"]):
        fallback_category = "Frameworks & Libraries"
    elif any(term in cleaned_lower for term in ["database", "db", "sql", "storage"]):
        fallback_category = "Databases"
    elif any(term in cleaned_lower for term in ["cloud", "devops", "ci/cd", "server", "deploy"]):
        fallback_category = "Cloud & DevOps"
    elif any(term in cleaned_lower for term in ["ai", "data", "learning", "vision", "nlp"]):
        fallback_category = "Data Science & AI"
    elif any(term in cleaned_lower for term in ["management", "writing", "communication", "skills", "leadership"]):
        fallback_category = "Soft & Professional Skills"

    if cleaned.islower():
        formatted_name = cleaned.title()
    else:
        formatted_name = cleaned

    return formatted_name, fallback_category


def deduplicate_and_group_skills(raw_skills: List[str]) -> Dict[str, List[str]]:
    """
    Deduplicate a list of raw skills by mapping to Canonical Name and grouping by category.
    Returns dict: category -> [canonical_skill_names]
    """
    grouped: Dict[str, List[str]] = {cat: [] for cat in SKILL_CATEGORIES}
    seen_canonical: Set[str] = set()

    for r in raw_skills:
        if not r or not isinstance(r, str):
            continue
        canonical_name, category = normalize_skill(r)
        if not canonical_name:
            continue
        if canonical_name not in seen_canonical:
            seen_canonical.add(canonical_name)
            if category in grouped:
                grouped[category].append(canonical_name)
            else:
                grouped["Tools & Technologies"].append(canonical_name)

    # Return only categories that have at least one skill
    return {cat: skills for cat, skills in grouped.items() if skills}


def deduplicate_skills_with_metadata(raw_skills: List[str]) -> Dict[str, Tuple[str, List[str]]]:
    """
    Deduplicate a list of raw skills and track raw variants.
    Returns dict: canonical_name -> (category, [raw_variants_found])
    """
    results: Dict[str, Tuple[str, List[str]]] = {}
    for r in raw_skills:
        if not r or not isinstance(r, str):
            continue
        canonical_name, category = normalize_skill(r)
        if not canonical_name:
            continue
        if canonical_name not in results:
            results[canonical_name] = (category, [r])
        else:
            cat, variants = results[canonical_name]
            if r not in variants:
                variants.append(r)
            results[canonical_name] = (cat, variants)
    return results
