from types import SimpleNamespace

from app.services.job_service import deduplicate_jobs


def test_deduplicate_jobs_normalizes_case_and_whitespace():
    jobs = [
        SimpleNamespace(title="Cloud Infrastructure Lead Stabilization"),
        SimpleNamespace(title="  Cloud   Infrastructure Lead Stabilization "),
        SimpleNamespace(title="cloud infrastructure lead stabilization"),
        SimpleNamespace(title="Backend Developer"),
    ]

    result = deduplicate_jobs(jobs)

    assert [job.title for job in result] == [
        "Cloud Infrastructure Lead Stabilization",
        "Backend Developer",
    ]
