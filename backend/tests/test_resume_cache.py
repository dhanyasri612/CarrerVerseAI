from types import SimpleNamespace

from app.models.parsed_resume import ParsedResume
from app.models.resume import Resume
from app.parsers.resume_parser import RESUME_PARSER_VERSION
from app.services import parser_service
from app.services.resume_service import _sha256_file
from app.ai.stores import candidate_store_sync


class _Query:
    def __init__(self, result):
        self.result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self.result


class _Db:
    def __init__(self, resume, parsed):
        self.resume = resume
        self.parsed = parsed
        self.added = []
        self.deleted = []

    def query(self, model):
        return _Query(self.resume if model is Resume else self.parsed)

    def add(self, value):
        self.added.append(value)

    def delete(self, value):
        self.deleted.append(value)

    def commit(self):
        return None

    def refresh(self, value):
        return None


def _resume(tmp_path):
    path = tmp_path / "resume.pdf"
    path.write_bytes(b"resume contents")
    return SimpleNamespace(
        id=7,
        user_id=11,
        file_path=str(path),
        content_hash=_sha256_file(str(path)),
        parser_version=RESUME_PARSER_VERSION,
        parsed_status=True,
    )


def test_sha256_is_stable_for_resume_bytes(tmp_path):
    resume = _resume(tmp_path)
    assert resume.content_hash == _sha256_file(resume.file_path)
    assert len(resume.content_hash) == 64


def test_parse_resume_reuses_matching_cached_result(tmp_path, monkeypatch):
    resume = _resume(tmp_path)
    cached = object()
    db = _Db(resume, cached)

    def fail_if_called(_path):
        raise AssertionError("cached resume should not be parsed again")

    monkeypatch.setattr(parser_service, "parse_resume", fail_if_called)

    result = parser_service.parse_resume_by_id(db, resume.id, SimpleNamespace(id=resume.user_id))

    assert result is cached
    assert db.added == []


def test_parser_version_invalidates_cached_result(tmp_path, monkeypatch):
    resume = _resume(tmp_path)
    resume.parser_version = "older-parser"
    cached = SimpleNamespace(id=1)
    db = _Db(resume, cached)
    parsed = SimpleNamespace(
        name="Candidate",
        email=None,
        phone=None,
        skills=[],
        education=[],
        experience=[],
        projects=[],
        certifications=[],
    )
    monkeypatch.setattr(parser_service, "parse_resume", lambda _path: parsed)
    monkeypatch.setattr(candidate_store_sync, "sync_candidate_ai_stores_safe", lambda *_args: None)

    result = parser_service.parse_resume_by_id(db, resume.id, SimpleNamespace(id=resume.user_id))

    assert result is cached
    assert db.added == []
    assert resume.parser_version == RESUME_PARSER_VERSION
    assert resume.parsed_status is True
