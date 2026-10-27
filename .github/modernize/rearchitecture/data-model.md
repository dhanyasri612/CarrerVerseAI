# Data model

- `User`: authenticated account and candidate identity.
- `Resume` / `ParsedResume`: uploaded document metadata and extracted resume evidence.
- `CandidateProfile`: normalized profile assembled from resume and connected sources.
- `Job` / `Role`: target-role requirements used for recommendations and gap analysis.
- `InterviewSession`: resumable interview state and evaluation results.
- Connected evidence models include GitHub, LeetCode, HackerRank, LinkedIn, certifications, repositories, and repository files.
- The frontend redesign treats these as existing backend contracts; it does not rename or reshape persisted entities.
