import os
import re
import fitz
import shutil
import subprocess
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

# ==========================================
# 1. TRUSTED DOMAINS & PLATFORMS
# ==========================================

TRUSTED_VERIFICATION_DOMAINS = [
    "coursera.org",
    "credly.com",
    "udemy.com",
    "nptel.ac.in",
    "swayam.gov.in",
    "edx.org",
    "learn.microsoft.com",
    "microsoft.com",
    "aws.amazon.com",
    "cloud.google.com",
    "cisco.com",
    "linkedin.com",
    "accredible.com",
    "badgr.com",
    "badgr.io",
    "skilljar.com",
    "certmetrics.com",
    "trailhead.salesforce.com",
    "salesforce.com",
    "hackerrank.com",
    "freecodecamp.org",
    "datacamp.com",
    "scrum.org",
    "scrumalliance.org",
    "mongodb.com",
    "oracle.com",
    "ibm.com",
    "guvi.in",
    "greatlearning.in",
    "mygreatlearning.com",
    "infosys.com",
    "infosysspringboard.com",
    "tcsion.com",
    "simplilearn.com",
    "geeksforgeeks.org",
]

ISSUER_SIGNATURES: Dict[str, List[str]] = {
    "GUVI": [
        r"\bguvi\b", r"\bguvi geek\b", r"\biitm pravartak\b"
    ],
    "NPTEL": [
        r"\bnptel\b", r"\bswayam\b", r"\biit madras\b", r"\biit bombay\b",
        r"\biit kharagpur\b", r"\biit roorkee\b", r"\biit kanpur\b", r"\biit delhi\b"
    ],
    "Great Learning": [
        r"\bgreat learning\b", r"\bgreat lakes\b"
    ],
    "Infosys Springboard": [
        r"\binfosys springboard\b", r"\binfosys\b"
    ],
    "TCS iON": [
        r"\btcs ion\b", r"\btata consultancy services\b"
    ],
    "Amazon Web Services (AWS)": [
        r"\baws\b", r"\bamazon web services\b", r"\baws certified\b"
    ],
    "Microsoft": [
        r"\bmicrosoft\b", r"\bazure\b", r"\bmicrosoft learn\b", r"\bmicrosoft certified\b"
    ],
    "Google Cloud": [
        r"\bgoogle cloud\b", r"\bgcp\b", r"\bgoogle cloud certified\b", r"\bgoogle developers\b"
    ],
    "Coursera": [
        r"\bcoursera\b", r"\bdeeplearning\.ai\b"
    ],
    "Udemy": [
        r"\budemy\b"
    ],
    "edX": [
        r"\bedx\b", r"\bharvardx\b", r"\bmitx\b"
    ],
    "Cisco": [
        r"\bcisco\b", r"\bccna\b", r"\bccnp\b", r"\bccie\b", r"\bcisco networking academy\b"
    ],
    "LinkedIn Learning": [
        r"\blinkedin learning\b", r"\blinkedin\b"
    ],
    "Credly": [
        r"\bcredly\b", r"\byouracclaim\b"
    ],
    "Oracle": [
        r"\boracle\b", r"\boracle certified\b", r"\boracle academy\b"
    ],
    "IBM": [
        r"\bibm\b", r"\bibm certified\b", r"\bibm skillsbuild\b", r"\bcognitive class\b"
    ],
    "HackerRank": [
        r"\bhackerrank\b"
    ],
    "Stanford Online": [
        r"\bstanford online\b", r"\bstanford university\b", r"\bstanford\b"
    ],
    "Harvard Online": [
        r"\bharvard online\b", r"\bharvard university\b", r"\bharvard\b", r"\bcs50\b"
    ],
    "University of Michigan": [
        r"\buniversity of michigan\b", r"\bumich\b"
    ],
    "GeeksforGeeks": [
        r"\bgeeksforgeeks\b", r"\bgfg\b"
    ],
    "Coding Ninjas": [
        r"\bcoding ninjas\b"
    ],
    "Scaler": [
        r"\bscaler academy\b", r"\bscaler\b"
    ],
    "SkillRack": [
        r"\bskillrack\b"
    ],
    "UpGrad": [
        r"\bupgrad\b"
    ],
    "Forage": [
        r"\bforage\b", r"\binsidesherpa\b"
    ],
    "Simplilearn": [
        r"\bsimplilearn\b"
    ],
    "Linux Foundation": [
        r"\blinux foundation\b", r"\bcncf\b", r"\bcka\b", r"\bckad\b"
    ],
    "CompTIA": [
        r"\bcomptia\b", r"\bsecurity\+\b", r"\bnetwork\+\b", r"\ba\+\b"
    ],
    "Scrum.org": [
        r"\bscrum\.org\b", r"\bprofessional scrum master\b", r"\bpsm\b"
    ],
    "MongoDB University": [
        r"\bmongodb university\b", r"\bmongodb\b"
    ],
    "Salesforce": [
        r"\bsalesforce\b", r"\btrailhead\b"
    ],
    "Meta": [
        r"\bmeta\b", r"\bmeta front-end\b", r"\bmeta back-end\b"
    ],
    "Databricks": [
        r"\bdatabricks\b"
    ],
    "HashiCorp": [
        r"\bhashicorp\b", r"\bterraform associate\b"
    ],
}

# ==========================================
# 2. SKILL TAXONOMY (Technical + Professional)
# ==========================================

SKILL_TAXONOMY: Dict[str, List[str]] = {
    # AI / LLM / Machine Learning / Deep Learning
    "Prompt Engineering": ["prompt engineering", "prompt design", "prompting", "chatgpt prompt", "prompt engineer"],
    "Generative AI": ["generative ai", "genai", "gen ai", "foundation models", "llm", "large language model", "chatgpt", "midjourney", "diffusion models"],
    "Transformers": ["transformer", "transformers", "attention mechanism", "bert", "gpt", "huggingface"],
    "Deep Learning": ["deep learning", "neural networks", "cnn", "rnn", "lstm", "computer vision", "backpropagation"],
    "Machine Learning": ["machine learning", "supervised learning", "unsupervised learning", "scikit-learn", "random forest", "svm", "regression", "classification"],
    "Natural Language Processing": ["nlp", "natural language processing", "spacy", "nltk", "text processing", "tokenization", "sentiment analysis"],
    "TensorFlow": ["tensorflow", "keras"],
    "PyTorch": ["pytorch", "torch"],
    
    # Cloud & DevOps
    "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation", "iam", "cloud practitioner", "solutions architect"],
    "Azure": ["azure", "azure devops", "azure cloud", "microsoft azure", "az-900", "az-204", "az-104"],
    "Google Cloud Platform": ["gcp", "google cloud", "bigquery", "cloud run", "app engine"],
    "Docker": ["docker", "containerization", "containers", "dockerfile", "docker-compose"],
    "Kubernetes": ["kubernetes", "k8s", "helm", "kubectl", "cka", "ckad"],
    "Terraform": ["terraform", "infrastructure as code", "iac", "hashicorp"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "jenkins", "github actions", "gitlab ci"],
    "Linux": ["linux", "bash", "shell scripting", "ubuntu", "redhat", "centos"],
    
    # Programming Languages & Backend
    "Python": ["python", "python3", "django", "fastapi", "flask", "numpy", "pandas"],
    "Java": ["java", "spring", "spring boot", "hibernate", "jvm"],
    "C++": ["c++", "cpp"],
    "C": ["\bc\b", "c programming"],
    "C# / .NET": ["c#", ".net", "asp.net", "dotnet"],
    "Go": ["golang", "go language"],
    "Rust": ["rust"],
    "Node.js": ["node.js", "nodejs", "express", "nestjs"],
    "Microservices": ["microservices", "distributed systems", "event-driven architecture"],
    "REST APIs": ["rest api", "restful", "api development", "fastapi", "endpoints"],
    "GraphQL": ["graphql", "apollo"],
    
    # Frontend
    "JavaScript": ["javascript", "es6", "vanilla js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react", "react.js", "reactjs", "redux", "next.js"],
    "Vue.js": ["vue", "vue.js", "vuejs", "vuex", "pinia", "nuxt"],
    "Angular": ["angular", "angularjs", "rxjs"],
    "HTML5 / CSS3": ["html", "html5", "css", "css3", "sass", "tailwind", "responsive design", "web design"],
    
    # Data & Databases
    "Data Science": ["data science", "data analysis", "pandas", "numpy", "matplotlib", "seaborn", "data analytics"],
    "Data Engineering": ["data engineering", "spark", "hadoop", "kafka", "airflow", "etl"],
    "SQL": ["sql", "mysql", "postgresql", "oracle db", "sql server", "relational database", "database management"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MongoDB": ["mongodb", "nosql", "document database"],
    "Redis": ["redis", "in-memory cache", "caching"],
    
    # Cybersecurity & Networking
    "Cybersecurity": ["cybersecurity", "cyber security", "penetration testing", "ethical hacking", "vulnerability assessment", "information security"],
    "Network Security": ["network security", "firewall", "vpn", "tcp/ip", "dns", "cisco", "ccna", "ccnp"],
    "Cryptography": ["cryptography", "ssl", "tls", "encryption", "public key"],
    
    # Professional & Soft Skills
    "Email Writing": ["email writing", "business email", "email etiquette", "professional correspondence"],
    "Presentation Skills": ["presentation skills", "effective presentation", "public speaking", "slide design", "presentation mastery"],
    "Business Communication": ["business communication", "workplace communication", "communication skills", "professional communication"],
    "Technical Writing": ["technical writing", "documentation", "report writing"],
    "Problem Solving": ["problem solving", "analytical thinking", "critical thinking", "algorithmic thinking"],
    "Agile / Scrum": ["agile", "scrum", "kanban", "sprint planning", "scrum master", "psm", "csm"],
    "Project Management": ["project management", "pmp", "product management", "jira"],
}


# ==========================================
# 3. EXTRACTION HELPER FUNCTIONS
# ==========================================

MONTH_MAPPING = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

GENERIC_TITLE_BLACKLIST = [
    "certificate of completion",
    "certificate of achievement",
    "certificate of excellence",
    "certificate of merit",
    "certificate of participation",
    "certificate of training",
    "certificate",
    "certification",
    "participation",
    "completion certificate",
    "course completion",
    "has successfully completed",
    "successfully completed",
    "for successfully completing",
    "for successfully completing the course",
    "is hereby awarded to",
    "presented to",
    "awarded to",
    "this is to certify that",
    "national board of accreditation",
    "national board",
    "aicte",
    "ministry of",
    "department of",
    "government of",
    "authorized signatory",
    "authorized signature",
    "signature",
    "signatures",
    "head of department",
    "instructor",
    "co-ordinator",
    "coordinator",
    "convener",
    "dean",
    "principal",
    "director",
    "faculty",
    "founder",
    "ceo",
    "president",
    "verification url",
    "credential id",
    "date",
    "date of issue",
]


def clean_filename_to_title(filename: Optional[str]) -> str:
    """Convert filename like '23AM018_PromptEngineering_GUVI.pdf' to 'Prompt Engineering'."""
    if not filename:
        return ""
    base = os.path.splitext(filename)[0]
    
    # Strip common prefixes like student IDs, timestamps, cert_
    base = re.sub(r"^[0-9A-Za-z]{5,10}[_\-\s]+", "", base) # e.g. 23AM018_
    base = re.sub(r"^(?:cert|certificate|img|doc|file|scan)[_\-\s]*[0-9]*[_\-\s]*", "", base, flags=re.IGNORECASE)
    
    # Strip trailing issuer keywords from filename
    base = re.sub(r"[_\-\s]+(?:guvi|nptel|coursera|udemy|infosys|stanford|aws|google|iit)[_\-\s0-9]*$", "", base, flags=re.IGNORECASE)

    # Convert camelCase to spaces (e.g. PromptEngineering -> Prompt Engineering)
    base = re.sub(r"([a-z])([A-Z])", r"\1 \2", base)
    
    # Replace underscores/hyphens with spaces
    base = re.sub(r"[_\-]+", " ", base).strip()
    
    # Title-case if clean
    if len(base) >= 3 and not any(b in base.lower() for b in ["certificate", "unknown"]):
        return " ".join([w.capitalize() for w in base.split()])

    return ""


RECIPIENT_PREFIX_REGEX = r"^(?:mr|ms|mrs|dr|prof|miss|shri|smt)\.?\s+"
STUDENT_ID_REGEX = r"\b[0-9]{2}[A-Za-z]{2,4}[0-9]{2,5}\b"


def is_invalid_or_generic_title(title: Optional[str]) -> bool:
    """Check if title is empty, recipient name, student ID, or generic boilerplate phrase."""
    if not title:
        return True
    t = title.strip()
    t_lower = t.lower()
    if len(t) < 3:
        return True
    
    # 1. Exact match, prefix match, or suffix match in blacklist
    if any(g == t_lower or t_lower.startswith(g) or t_lower.endswith(g) for g in GENERIC_TITLE_BLACKLIST):
        return True
    
    # 2. Key phrases anywhere inside text
    boilerplate_phrases = [
        "presented to", "awarded to", "this is to certify", "certifies that",
        "hereby certifies", "for successfully completing", "completion of the course",
        "national board of accreditation", "authorized signature", "authorized signatory",
        "organizing secretary", "convenor", "co-ordinator", "coordinator", "programme coordinator",
        "department of", "ministry of", "government of"
    ]
    if any(bp in t_lower for bp in boilerplate_phrases):
        return True
        
    # 3. Recipient name prefixes (e.g. "Ms. DHANYASRI K", "Dr. John Doe")
    if re.search(RECIPIENT_PREFIX_REGEX, t, re.IGNORECASE):
        return True
        
    # 4. Student reg number / roll number (e.g. 23AM018)
    if re.search(STUDENT_ID_REGEX, t):
        return True
        
    # 5. Names like "DHANYASRI K" or "K. DHANYASRI" (two words where one is a single letter initial and neither is a course keyword)
    words = t.split()
    if len(words) == 2 and (len(words[0].rstrip(".")) == 1 or len(words[1].rstrip(".")) == 1):
        course_keywords = ["programming", "language", "test", "course", "bootcamp", "workshop", "specialization", "cert", "skills", "engineering"]
        if not any(k in t_lower for k in course_keywords):
            return True
        
    return False


def parse_flexible_date(date_str: str) -> Optional[date]:
    """Parse various date representations into datetime.date."""
    if not date_str:
        return None
    cleaned = date_str.strip().replace(",", " ")
    
    # Format: YYYY-MM-DD
    match = re.search(r"\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b", cleaned)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass

    # Format: DD/MM/YYYY or MM/DD/YYYY
    match = re.search(r"\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b", cleaned)
    if match:
        v1, v2, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            if v1 > 12:
                return date(year, v2, v1)
            else:
                return date(year, v1, v2)
        except ValueError:
            pass

    # Format: Month DD, YYYY or DD Month YYYY or Month YYYY
    for m_name, m_num in MONTH_MAPPING.items():
        pattern_with_day = rf"\b(\d{{1,2}})?\s*{m_name}\.?\s*(\d{{1,2}})?\s*,?\s*(\d{{4}})\b"
        match = re.search(pattern_with_day, cleaned, re.IGNORECASE)
        if match:
            day_str = match.group(1) or match.group(2) or "1"
            year_str = match.group(3)
            try:
                day = int(day_str)
                year = int(year_str)
                return date(year, m_num, min(max(day, 1), 28))
            except ValueError:
                pass

    return None


def extract_issuing_organization(text: str, filename: Optional[str] = None) -> str:
    """Identify the issuing organization using regex signatures, contextual labels, and filename fallback."""
    text_lower = text.lower()
    
    # 1. Signature check in text
    for issuer, patterns in ISSUER_SIGNATURES.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return issuer

    # 2. Contextual regex: "issued by [Org]", "awarded by [Org]", etc.
    context_patterns = [
        r"(?:issued by|offered by|authorized by|granted by|organized by|provided by|partnered with|conducted by|certified by)[:\s]+([A-Za-z0-9\s&.,'-]{3,50})",
        r"(?:institution|academy|university|institute|provider|platform)[:\s]+([A-Za-z0-9\s&.,'-]{3,50})",
    ]
    for cp in context_patterns:
        match = re.search(cp, text, re.IGNORECASE)
        if match:
            cand = match.group(1).split("\n")[0].strip()
            cand = re.sub(r"[\s,.:;]+$", "", cand).strip()
            if len(cand) >= 3 and not any(w in cand.lower() for w in ["date", "signature", "credential", "id", "mr.", "ms.", "this is"]):
                return cand

    # 3. Filename clue fallback
    if filename:
        fn_clean = re.sub(r"[_\-]+", " ", filename.lower())
        for issuer, patterns in ISSUER_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, fn_clean):
                    return issuer

    return "Unknown Organization"


def extract_certification_name(text: str, filename: Optional[str] = None) -> str:
    """
    Extract certification title using structural patterns, explicit domain titles,
    contextual relative lines, and filename fallback.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # 1. High-priority explicit domain patterns
    explicit_patterns = [
        r"\b(Prompt Engineering[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(Generative AI[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(GenAI[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(Deep Learning Specialization[A-Za-z0-9\t :,\-–—()&+/]{0,40})",
        r"\b(Machine Learning Specialization[A-Za-z0-9\t :,\-–—()&+/]{0,40})",
        r"\b(Email Writing[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(Presentation Skills[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(Business Communication[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(Python Programming[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(C\s+Programming[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(C\s+test[A-Za-z0-9\t :,\-–—()&+/]{0,50})",
        r"\b(AWS Certified\s+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(Microsoft Certified[:\s]+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(Google Cloud Certified[:\s]+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(Certified Kubernetes\s+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(CompTIA\s+[A-Za-z0-9\s:,\-+]{2,50})",
        r"\b(Cisco Certified\s+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(Oracle Certified\s+[A-Za-z0-9\t :,\-–—()&+/]{3,60})",
        r"\b(Professional Scrum Master\s+[I|II|III]*)\b",
    ]

    for pat in explicit_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            cand = match.group(1).split("\n")[0].strip()
            cand = re.sub(r"[\s,.:;–—]+$", "", cand).strip()
            if not is_invalid_or_generic_title(cand):
                return cand

    # 2. Structural labeled patterns: "Course Title: ...", "Course on: ...", etc.
    structural_patterns = [
        r"(?:Course Title|Certification Title|Certificate Name|Course Name|Course on|Specialization in|Masterclass on|Workshop on|Bootcamp on|Training on|Program Title|Program on)[:\s]+([A-Za-z0-9\t :,\-–—()&+/]{4,80})",
        r"(?:Certificate of (?:Completion|Achievement|Excellence|Merit|Participation))\s*(?:in|for)?\s*[\n:]\s*([A-Za-z0-9\t :,\-–—()&+/]{4,80})",
        r"(?:for successfully completing the course (?:on|in)|for successfully completing the course|for successfully completing|has successfully completed|has completed the course|has completed the program|has earned the credential|successfully achieved)\s+(?:the requirements to be recognized as an?\s+|all requirements for\s+)?[\"']?([A-Za-z0-9\t :,\-–—()&+/]{4,80})[\"']?",
    ]

    for pat in structural_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            candidate = match.group(1).split("\n")[0].strip()
            # Clean prefixes
            candidate = re.sub(r"^(?:the requirements to be recognized as an?|all requirements for|the course (?:on|in)?|the course|the program)\s+", "", candidate, flags=re.IGNORECASE).strip()
            candidate = re.sub(r"[\s,.:;–—]+$", "", candidate).strip()
            if not is_invalid_or_generic_title(candidate):
                return candidate

    # 3. Contextual line check (lines right after certificate header or recipient name)
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        if any(h in line_clean.lower() for h in ["certificate of", "certification of", "awarded to", "presented to", "this is to certify that", "completed the"]):
            # Look at next 1-3 lines
            for offset in range(1, 4):
                if idx + offset < len(lines):
                    next_line = lines[idx + offset].strip()
                    next_line = re.sub(r"[\s,.:;–—]+$", "", next_line).strip()
                    if len(next_line) >= 4 and not is_invalid_or_generic_title(next_line):
                        return next_line

    # 4. Check top lines for title-like headings
    for line in lines[:10]:
        line_clean = re.sub(r"[\s,.:;]+$", "", line).strip()
        if 4 <= len(line_clean) <= 80:
            if not is_invalid_or_generic_title(line_clean):
                lower = line_clean.lower()
                if any(k in lower for k in ["prompt", "genai", "ai", "learning", "python", "data", "cloud", "aws", "azure", "presentation", "email", "writing", "communication", "developer", "architect", "engineer", "specialization", "course", "bootcamp", "c programming", "c test"]):
                    return line_clean

    # 5. Filename Fallback (e.g. 23AM018_PromptEngineering.pdf -> Prompt Engineering)
    filename_title = clean_filename_to_title(filename)
    if filename_title and not is_invalid_or_generic_title(filename_title):
        return filename_title

    return "Certificate of Completion"


def extract_credential_id(text: str) -> Optional[str]:
    """Find credential ID, license number, or certificate identifier."""
    patterns = [
        r"(?:Credential ID|Certificate (?:ID|No|Number)|License (?:Number|No)|Badge ID|Validation (?:ID|Number)|Cert ID|Verification Code|Certificate Validation Code|ID)[:\s#]+([A-Za-z0-9_\-\.]{5,50})",
        r"\b(UC-[a-f0-9\-]{8,40})\b", # Udemy format
        r"\b(Coursera Verify:\s*([A-Za-z0-9]{8,24}))\b",
        r"\b([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})\b",
    ]

    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            for g in reversed(match.groups()):
                if g and len(g.strip()) >= 5:
                    return g.strip()
    return None


def extract_credential_url(text: str, link_annotations: Optional[List[str]] = None) -> Optional[str]:
    """Extract public verification link from embedded links or text."""
    if link_annotations:
        for url in link_annotations:
            if not url or not isinstance(url, str):
                continue
            parsed = urlparse(url)
            if any(domain in parsed.netloc.lower() for domain in TRUSTED_VERIFICATION_DOMAINS):
                return url
            if any(k in url.lower() for k in ["verify", "certificate", "credential", "badge", "cert"]):
                return url

    patterns = [
        r"https?://(?:www\.)?credly\.com/badges/[a-f0-9\-]+(?:/[a-z0-9\-]+)?",
        r"https?://(?:www\.)?coursera\.org/verify/[A-Za-z0-9]+",
        r"https?://(?:www\.)?udemy\.com/certificate/[A-Za-z0-9_\-]+/?",
        r"https?://(?:www\.)?nptel\.ac\.in/noc/Ecertificate/\?id=[A-Za-z0-9_\-]+",
        r"https?://(?:www\.)?learn\.microsoft\.com/[a-z]{2}-[a-z]{2}/users/[^\s]+/credentials/[^\s]+",
        r"https?://(?:www\.)?guvi\.in/verify-certificate\?[^\s]+",
        r"https?://[a-zA-Z0-9.\-]+/(?:verify|certificates?|credentials?|badges?)/[a-zA-Z0-9_\-\.\?=\&]+",
    ]

    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            url = match.group(0).rstrip(".,;)")
            if len(url) > 10 and "." in url:
                return url

    return None


def extract_dates(text: str) -> Tuple[Optional[date], Optional[date]]:
    """Extract issue date and expiry date."""
    issue_date = None
    expiry_date = None
    
    # 1. Search for Issue Date
    issue_patterns = [
        r"(?:Issue Date|Issued on|Date Issued|Date of Achievement|Date of Issue|Awarded on|Completed on|Date of Completion|Granted on|Issued|Date)[:\s]+([A-Za-z0-9\s,/\.\-]{4,25})",
        r"(?:Valid From|Start Date)[:\s]+([A-Za-z0-9\s,/\.\-]{4,25})",
    ]
    for pat in issue_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            d = parse_flexible_date(match.group(1))
            if d:
                issue_date = d
                break

    # 2. Search for Expiry Date
    expiry_patterns = [
        r"(?:Expiry Date|Expiration Date|Expires on|Valid Through|Valid Until|Expires|Renewal Date)[:\s]+([A-Za-z0-9\s,/\.\-]{4,25})",
    ]
    for pat in expiry_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            d = parse_flexible_date(match.group(1))
            if d:
                expiry_date = d
                break

    # 3. Fallback: if no explicit label, search for standalone dates in the document
    if not issue_date:
        generic_date_match = re.search(r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b", text, re.IGNORECASE)
        if generic_date_match:
            issue_date = parse_flexible_date(generic_date_match.group(0))

    return issue_date, expiry_date


def extract_skills_from_text(text: str, certification_name: str) -> List[str]:
    """
    Map skills from certification title and parsed syllabus/text.
    Prioritizes skills directly found in the certification title to avoid
    extracting spurious mentions from page footers or institute logos.
    """
    found_skills = set()

    # 1. First priority: match against certification_name directly
    if certification_name and not is_invalid_or_generic_title(certification_name):
        name_lower = certification_name.lower()
        for canonical_skill, keywords in SKILL_TAXONOMY.items():
            if canonical_skill == "C":
                if re.search(r"\b(?:c\s*programming|c\s*language|course\s*in\s*c|c\s*test|learn\s*c)\b", name_lower) or (re.search(r"\bc\b", name_lower) and not re.search(r"\b(?:c\+\+|c#)\b", name_lower)):
                    found_skills.add("C")
                continue
            for kw in keywords:
                pattern = rf"\b{re.escape(kw)}\b"
                if re.search(pattern, name_lower):
                    found_skills.add(canonical_skill)
                    break

        # If skills were identified directly in the title, return them (highest precision)
        if found_skills:
            return sorted(list(found_skills))

    # 2. Second priority: clean body text (filter out footer catalogs / partner logos)
    cleaned_body = text.lower()
    cleaned_body = re.sub(r"(?:spoken tutorial|nmeict|mhrd|funded by|offered courses).*$", "", cleaned_body, flags=re.DOTALL)

    for canonical_skill, keywords in SKILL_TAXONOMY.items():
        if canonical_skill == "C":
            if re.search(r"\b(?:c\s*programming|c\s*language|course\s*in\s*c|c\s*test)\b", cleaned_body):
                found_skills.add("C")
            continue
        for kw in keywords:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, cleaned_body):
                found_skills.add(canonical_skill)
                break

    return sorted(list(found_skills))


def calculate_confidence_score(
    name: str,
    issuer: str,
    credential_id: Optional[str],
    credential_url: Optional[str],
    issue_date: Optional[date],
    skills: List[str]
) -> float:
    """
    Calculate confidence score (0.0 to 1.0).
    Penalize generic titles ('Certificate of Completion') and 'Unknown Organization'.
    """
    score = 0.0

    # Title score
    if name and not is_invalid_or_generic_title(name):
        score += 0.35
    elif name:
        score += 0.05

    # Issuer score
    if issuer and issuer != "Unknown Organization":
        score += 0.30
    elif issuer:
        score += 0.05

    # Credential ID or verification link
    if credential_id or credential_url:
        score += 0.20

    # Date
    if issue_date:
        score += 0.10

    # Skills mapped
    if skills and len(skills) > 0:
        score += 0.05

    return min(round(score, 2), 1.0)


def evaluate_initial_verification_status(
    credential_url: Optional[str],
    issuing_organization: Optional[str]
) -> str:
    """
    Trust evaluation rules:
    - If URL belongs to a trusted domain -> 'VERIFICATION_PENDING' (never auto-mark VERIFIED)
    - If no URL or untrusted -> 'UNVERIFIED'
    """
    if not credential_url:
        return "UNVERIFIED"

    try:
        parsed = urlparse(credential_url)
        domain = parsed.netloc.lower()
        if any(trusted in domain for trusted in TRUSTED_VERIFICATION_DOMAINS):
            return "VERIFICATION_PENDING"
    except Exception:
        pass

    return "UNVERIFIED"


# ==========================================
# 4. ROBUST OCR ENGINES & MAIN PARSERS
# ==========================================

def ocr_image_bytes(image_bytes: bytes, ext: str = "png") -> str:
    """Run OCR on raw image bytes using Tesseract CLI or PyMuPDF."""
    tess_path = shutil.which("tesseract") or "/opt/homebrew/bin/tesseract"
    
    if os.path.exists(tess_path):
        try:
            proc = subprocess.Popen(
                [tess_path, "stdin", "stdout", "--oem", "1", "-l", "eng"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = proc.communicate(input=image_bytes, timeout=15)
            if proc.returncode == 0 and out.strip():
                return out.decode("utf-8", errors="ignore")
        except Exception:
            pass

    try:
        clean_ext = ext.lstrip(".").lower()
        if clean_ext not in ["png", "jpg", "jpeg", "webp", "tiff"]:
            clean_ext = "png"
        img_doc = fitz.open(stream=image_bytes, filetype=clean_ext)
        pdf_doc = fitz.open()
        p0 = img_doc[0]
        page = pdf_doc.new_page(width=p0.rect.width, height=p0.rect.height)
        page.insert_image(page.rect, stream=image_bytes)
        tp = page.get_textpage_ocr()
        ocr_text = page.get_text(textpage=tp)
        img_doc.close()
        pdf_doc.close()
        if ocr_text.strip():
            return ocr_text
    except Exception:
        pass

    return ""


def ocr_pdf_page(page: fitz.Page) -> str:
    """Render a scanned PDF page to high-res image and perform OCR."""
    try:
        pix = page.get_pixmap(dpi=150)
        png_bytes = pix.tobytes("png")
        return ocr_image_bytes(png_bytes, "png")
    except Exception:
        return ""


def extract_from_pdf_bytes(file_bytes: bytes, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract text, annotations, links, and metadata from PDF bytes using PyMuPDF + Page OCR.
    """
    extracted_text_parts = []
    link_annotations = []
    ocr_applied_pages = []
    raw_metadata = {"filename": filename or "certificate.pdf", "extractor": "PyMuPDF"}

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        raw_metadata["page_count"] = len(doc)
        raw_metadata["doc_metadata"] = doc.metadata or {}

        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 1. Plain text vector extraction
            page_text = page.get_text()
            
            # 2. Hyperlink extraction
            links = page.get_links()
            for link in links:
                uri = link.get("uri")
                if uri:
                    link_annotations.append(uri)

            # 3. If page text is empty or sparse (< 25 chars), trigger page-level OCR
            if not page_text or len(page_text.strip()) < 25:
                ocr_text = ocr_pdf_page(page)
                if ocr_text and len(ocr_text.strip()) > 5:
                    page_text = ocr_text
                    ocr_applied_pages.append(page_num + 1)

            if page_text:
                extracted_text_parts.append(page_text)

        doc.close()
    except Exception as e:
        raw_metadata["pdf_error"] = str(e)

    full_text = "\n".join(extracted_text_parts).strip()
    raw_metadata["extracted_text_length"] = len(full_text)
    raw_metadata["link_annotations"] = link_annotations
    raw_metadata["ocr_pages"] = ocr_applied_pages
    raw_metadata["ocr_used"] = len(ocr_applied_pages) > 0

    if raw_metadata["ocr_used"] and len(extracted_text_parts) > len(ocr_applied_pages):
        raw_metadata["extractor"] = "PyMuPDF+OCR"
    elif raw_metadata["ocr_used"]:
        raw_metadata["extractor"] = "OCR"
    else:
        raw_metadata["extractor"] = "PyMuPDF"

    # If full text is still empty, perform fallback stream OCR
    if len(full_text) < 20:
        fallback_text, image_meta = extract_fallback_from_images(file_bytes, filename)
        if fallback_text:
            full_text = fallback_text
            raw_metadata["fallback_used"] = True
            raw_metadata["image_meta"] = image_meta
            raw_metadata["extractor"] = "OCR"

    return parse_structured_certification(full_text, link_annotations, raw_metadata, filename)


def extract_fallback_from_images(file_bytes: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Extract text from image files (JPG, PNG, WEBP, JPEG) using OCR.
    """
    meta = {"extractor": "OCR"}
    ext = "png"
    if filename:
        ext_candidate = filename.split(".")[-1].lower()
        if ext_candidate in ["png", "jpg", "jpeg", "webp", "tiff"]:
            ext = ext_candidate

    text_content = ocr_image_bytes(file_bytes, ext)
    meta["ocr_length"] = len(text_content)
    meta["ocr_used"] = True
    return text_content.strip(), meta


def parse_structured_certification(
    text: str,
    link_annotations: Optional[List[str]] = None,
    raw_metadata: Optional[Dict[str, Any]] = None,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse raw extracted certificate text into standardized certification object.
    """
    if raw_metadata is None:
        raw_metadata = {}

    issuer = extract_issuing_organization(text, filename)
    cert_name = extract_certification_name(text, filename)
    cred_id = extract_credential_id(text)
    cred_url = extract_credential_url(text, link_annotations)
    issue_date, expiry_date = extract_dates(text)
    skills = extract_skills_from_text(text, cert_name)
    confidence = calculate_confidence_score(cert_name, issuer, cred_id, cred_url, issue_date, skills)
    verification_status = evaluate_initial_verification_status(cred_url, issuer)

    # Store safe clean text sample for debugging in metadata
    raw_metadata["extracted_text_sample"] = text[:500].replace("\n", " ").strip() if text else ""
    raw_metadata["filename"] = filename or "certificate.pdf"

    return {
        "certification_name": cert_name,
        "issuing_organization": issuer,
        "issue_date": issue_date,
        "expiry_date": expiry_date,
        "credential_id": cred_id,
        "credential_url": cred_url,
        "verification_status": verification_status,
        "extracted_skills": skills,
        "confidence_score": confidence,
        "raw_metadata": raw_metadata,
    }
