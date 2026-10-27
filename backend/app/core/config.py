import os
from pathlib import Path

# Force PyTorch backend for transformers to prevent Abseil mutex deadlock with TensorFlow on macOS
os.environ["USE_TF"] = "0"
os.environ["USE_FLAX"] = "0"
os.environ["USE_TORCH"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_ROOT / ".env")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "careerverse-secure-production-key-change-in-env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/linkedin/callback")
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip() or None
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_MAX_COMPLETION_TOKENS = int(os.getenv("GROQ_MAX_COMPLETION_TOKENS", "2048"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_MAX_COMPLETION_TOKENS = int(os.getenv("OLLAMA_MAX_COMPLETION_TOKENS", "400"))
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "180.0"))
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_configured_chroma_dir = Path(os.getenv("CHROMADB_DIR", "./chroma_db_v2"))
CHROMADB_DIR = str(
    _configured_chroma_dir
    if _configured_chroma_dir.is_absolute()
    else _BACKEND_ROOT / _configured_chroma_dir
)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "careerverse123")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Environment-based CORS Origins

raw_cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173"
)
CORS_ORIGINS = [origin.strip() for origin in raw_cors_origins.split(",") if origin.strip()]

# Multilingual AI Settings
raw_supported_langs = os.getenv("SUPPORTED_LANGUAGES", "en,ta,hi,te,kn,ml")
SUPPORTED_LANGUAGES = [lang.strip().lower() for lang in raw_supported_langs.split(",") if lang.strip()]
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en").strip().lower()
LANGUAGE_DETECTION_ENABLED = os.getenv("LANGUAGE_DETECTION_ENABLED", "true").strip().lower() in ("true", "1", "yes")