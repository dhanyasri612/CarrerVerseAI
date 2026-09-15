import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.leetcode_profile import LeetCodeProfile


LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"


def build_leetcode_query(username: str) -> str:
    return f"""
{{
  matchedUser(username: "{username}") {{
    username
    githubUrl
    twitterUrl
    linkedinUrl
    profile {{
      realName
      userAvatar
      aboutMe
      ranking
      reputation
      websites
      countryName
      company
      school
      skillTags
      starRating
    }}
    submitStatsGlobal {{
      acSubmissionNum {{
        difficulty
        count
        submissions
      }}
      totalSubmissionNum {{
        difficulty
        count
        submissions
      }}
    }}
    badges {{
      id
      displayName
      icon
      creationDate
    }}
    languageProblemCount {{
      languageName
      problemsSolved
    }}
    tagProblemCounts {{
      advanced {{
        tagName
        tagSlug
        problemsSolved
      }}
      intermediate {{
        tagName
        tagSlug
        problemsSolved
      }}
      fundamental {{
        tagName
        tagSlug
        problemsSolved
      }}
    }}
  }}
  userContestRanking(username: "{username}") {{
    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage
    badge {{
      name
    }}
  }}
  recentAcSubmissionList(username: "{username}", limit: 15) {{
    id
    title
    titleSlug
    timestamp
  }}
}}
"""


def fetch_leetcode_data_from_graphql(username: str) -> dict:
    headers = {
        "Content-Type": "application/json",
    }

    query = build_leetcode_query(username)

    try:
        response = httpx.post(
            LEETCODE_GRAPHQL_URL,
            json={"query": query},
            headers=headers,
            timeout=15.0,
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Failed to connect to LeetCode GraphQL API",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch data from LeetCode GraphQL API",
        )

    try:
        response_data = response.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Invalid response received from LeetCode GraphQL API",
        )

    graphql_data = response_data.get("data") or {}
    matched_user = graphql_data.get("matchedUser")

    if not matched_user:
        raise HTTPException(
            status_code=404,
            detail="LeetCode user not found",
        )

    profile_info = matched_user.get("profile") or {}
    submit_stats = matched_user.get("submitStatsGlobal") or {}
    ac_submissions = submit_stats.get("acSubmissionNum") or []
    total_submissions_list = submit_stats.get("totalSubmissionNum") or []

    total_solved = 0
    easy_solved = 0
    medium_solved = 0
    hard_solved = 0

    for item in ac_submissions:
        diff = item.get("difficulty")
        cnt = item.get("count", 0)
        if diff == "All":
            total_solved = cnt
        elif diff == "Easy":
            easy_solved = cnt
        elif diff == "Medium":
            medium_solved = cnt
        elif diff == "Hard":
            hard_solved = cnt

    total_submissions = 0
    total_ac_submissions = 0
    for item in total_submissions_list:
        diff = item.get("difficulty")
        cnt = item.get("submissions", 0)
        if diff == "All":
            total_submissions = cnt

    for item in ac_submissions:
        if item.get("difficulty") == "All":
            total_ac_submissions = item.get("submissions", 0)

    acceptance_rate = None
    if total_submissions > 0 and total_ac_submissions > 0:
        acceptance_rate = round((total_ac_submissions / total_submissions) * 100, 2)

    contest_data = graphql_data.get("userContestRanking") or {}
    contest_rating = contest_data.get("rating")
    contest_ranking = contest_data.get("globalRanking")
    contest_attended = contest_data.get("attendedContestsCount") or 0
    contest_top_percentage = contest_data.get("topPercentage")
    contest_badge = None
    if contest_data.get("badge"):
        contest_badge = contest_data.get("badge", {}).get("name")

    return {
        "username": matched_user.get("username", username),
        "profile_url": f"https://leetcode.com/u/{matched_user.get('username', username)}/",
        "real_name": profile_info.get("realName"),
        "about": profile_info.get("aboutMe"),
        "avatar_url": profile_info.get("userAvatar"),
        "ranking": profile_info.get("ranking"),
        "reputation": profile_info.get("reputation"),
        "total_solved": total_solved,
        "easy_solved": easy_solved,
        "medium_solved": medium_solved,
        "hard_solved": hard_solved,
        "acceptance_rate": acceptance_rate,
        "total_submissions": total_submissions,
        "contest_rating": contest_rating,
        "contest_ranking": contest_ranking,
        "contest_attended": contest_attended,
        "contest_top_percentage": contest_top_percentage,
        "contest_badge": contest_badge,
        "badges": matched_user.get("badges") or [],
        "languages": matched_user.get("languageProblemCount") or [],
        "skills": matched_user.get("tagProblemCounts") or {},
        "recent_submissions": graphql_data.get("recentAcSubmissionList") or [],
    }


def sync_leetcode_profile(
    db: Session,
    username: str,
    current_user: User,
) -> LeetCodeProfile:
    parsed_data = fetch_leetcode_data_from_graphql(username)

    leetcode_profile = (
        db.query(LeetCodeProfile)
        .filter(LeetCodeProfile.user_id == current_user.id)
        .first()
    )

    if not leetcode_profile:
        leetcode_profile = LeetCodeProfile(
            user_id=current_user.id,
            username=parsed_data["username"],
        )
        db.add(leetcode_profile)

    leetcode_profile.username = parsed_data["username"]
    leetcode_profile.profile_url = parsed_data["profile_url"]
    leetcode_profile.real_name = parsed_data["real_name"]
    leetcode_profile.about = parsed_data["about"]
    leetcode_profile.avatar_url = parsed_data["avatar_url"]
    leetcode_profile.ranking = parsed_data["ranking"]
    leetcode_profile.reputation = parsed_data["reputation"]
    leetcode_profile.total_solved = parsed_data["total_solved"]
    leetcode_profile.easy_solved = parsed_data["easy_solved"]
    leetcode_profile.medium_solved = parsed_data["medium_solved"]
    leetcode_profile.hard_solved = parsed_data["hard_solved"]
    leetcode_profile.acceptance_rate = parsed_data["acceptance_rate"]
    leetcode_profile.total_submissions = parsed_data["total_submissions"]
    leetcode_profile.contest_rating = parsed_data["contest_rating"]
    leetcode_profile.contest_ranking = parsed_data["contest_ranking"]
    leetcode_profile.contest_attended = parsed_data["contest_attended"]
    leetcode_profile.contest_top_percentage = parsed_data["contest_top_percentage"]
    leetcode_profile.contest_badge = parsed_data["contest_badge"]
    leetcode_profile.badges = parsed_data["badges"]
    leetcode_profile.languages = parsed_data["languages"]
    leetcode_profile.skills = parsed_data["skills"]
    leetcode_profile.recent_submissions = parsed_data["recent_submissions"]

    db.commit()
    db.refresh(leetcode_profile)

    return leetcode_profile


def get_leetcode_profile(
    db: Session,
    current_user: User,
) -> LeetCodeProfile:
    leetcode_profile = (
        db.query(LeetCodeProfile)
        .filter(LeetCodeProfile.user_id == current_user.id)
        .first()
    )

    if not leetcode_profile:
        raise HTTPException(
            status_code=404,
            detail="LeetCode profile not found",
        )

    return leetcode_profile


def get_leetcode_problems(
    db: Session,
    current_user: User,
) -> dict:
    leetcode_profile = (
        db.query(LeetCodeProfile)
        .filter(LeetCodeProfile.user_id == current_user.id)
        .first()
    )

    if not leetcode_profile:
        raise HTTPException(
            status_code=404,
            detail="LeetCode profile not found",
        )

    return {
        "username": leetcode_profile.username,
        "total_solved": leetcode_profile.total_solved,
        "easy_solved": leetcode_profile.easy_solved,
        "medium_solved": leetcode_profile.medium_solved,
        "hard_solved": leetcode_profile.hard_solved,
        "acceptance_rate": leetcode_profile.acceptance_rate,
        "total_submissions": leetcode_profile.total_submissions,
        "languages": leetcode_profile.languages,
        "skills": leetcode_profile.skills,
        "recent_submissions": leetcode_profile.recent_submissions,
    }
