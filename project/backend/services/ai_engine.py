"""
AI Engine Service — Custom-trained NLP engine.
No external AI APIs — uses InterviewIQ's own trained NLP pipeline.

Handles:
  1. Resume analysis & skill extraction (NLP + regex)
  2. Contextual interview question generation (skill-matched question bank)
  3. Answer evaluation with detailed NLP scoring
  4. Personalised feedback generation
"""

from __future__ import annotations

from typing import Optional

from services.nlp_utils import (
    extract_entities,
    extract_keywords,
    extract_skill_names,
    extract_skills,
    score_answer,
    generate_answer_feedback,
    generate_recommendations,
    generate_summary,
)
from services.question_bank import select_questions
from services.video_analyser import score_video_answer


# ── 1. Resume Analysis ───────────────────────────────────────────────


def analyse_resume(resume_text: str) -> dict:
    """
    Extract structured information from resume text using NLP.
    Returns: { name, email, skills[], experience[], education[], summary }
    """
    if not resume_text or len(resume_text.strip()) < 10:
        return {
            "name": None,
            "email": None,
            "skills": [],
            "experience": [],
            "education": [],
            "summary": "",
        }

    # Entity extraction (name, email, phone, urls)
    entities = extract_entities(resume_text)

    # Skill extraction
    skills_data = extract_skills(resume_text)
    technical_skills = list(skills_data.get("technical", {}).keys())
    soft_skills = list(skills_data.get("soft", {}).keys())

    # Convert skill keys to readable names
    skill_display_names = _format_skill_names(technical_skills + soft_skills)

    # Extract keywords for summary
    keywords = extract_keywords(resume_text, top_n=20)

    # Experience extraction (heuristic-based)
    experience = _extract_experience(resume_text)

    # Education extraction (heuristic-based)
    education = _extract_education(resume_text)

    # Generate summary
    summary = _generate_resume_summary(
        name=entities.get("name"),
        skills=skill_display_names,
        experience_count=len(experience),
        education=education,
    )

    return {
        "name": entities.get("name"),
        "email": entities.get("email"),
        "phone": entities.get("phone"),
        "urls": entities.get("urls", []),
        "skills": skill_display_names,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "experience": experience,
        "education": education,
        "keywords": keywords,
        "summary": summary,
    }


def _format_skill_names(skill_keys: list[str]) -> list[str]:
    """Convert internal skill keys to display-friendly names."""
    name_map = {
        "python": "Python",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "java": "Java",
        "cpp": "C++",
        "csharp": "C#",
        "go": "Go",
        "rust": "Rust",
        "ruby": "Ruby",
        "php": "PHP",
        "swift": "Swift",
        "kotlin": "Kotlin",
        "scala": "Scala",
        "r": "R",
        "react": "React",
        "angular": "Angular",
        "vue": "Vue.js",
        "svelte": "Svelte",
        "html_css": "HTML/CSS",
        "frontend": "Frontend Build Tools",
        "nodejs": "Node.js",
        "django": "Django",
        "flask": "Flask",
        "fastapi": "FastAPI",
        "spring": "Spring Boot",
        "rails": "Ruby on Rails",
        "sql": "SQL",
        "nosql": "NoSQL",
        "redis": "Redis",
        "elasticsearch": "Elasticsearch",
        "aws": "AWS",
        "azure": "Azure",
        "gcp": "Google Cloud",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "cicd": "CI/CD",
        "terraform": "Terraform",
        "linux": "Linux",
        "machine_learning": "Machine Learning",
        "data_science": "Data Science",
        "nlp": "NLP",
        "computer_vision": "Computer Vision",
        "android": "Android",
        "ios": "iOS",
        "react_native": "React Native",
        "flutter": "Flutter",
        "system_design": "System Design",
        "api_design": "API Design",
        "testing": "Testing",
        "design_patterns": "Design Patterns",
        "dsa": "Data Structures & Algorithms",
        "security": "Security",
        "devops": "DevOps",
        "git": "Git",
        "agile": "Agile/Scrum",
        "leadership": "Leadership",
        "communication": "Communication",
        "teamwork": "Teamwork",
        "problem_solving": "Problem Solving",
        "adaptability": "Adaptability",
        "time_management": "Time Management",
        "creativity": "Creativity",
        "mentoring": "Mentoring",
    }
    return [name_map.get(k, k.replace("_", " ").title()) for k in skill_keys]


def _extract_experience(text: str) -> list[dict]:
    """Extract work experience entries heuristically."""
    import re

    experience: list[dict] = []
    lines = text.split("\n")

    exp_header_pattern = re.compile(
        r"(?:^experience$|work\s*experience|professional\s*experience|employment|career\s*history|positions?\s*held|work\s*history)",
        re.IGNORECASE,
    )

    date_pattern = re.compile(
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s*\d{4}\s*[-\u2013\u2014to]+\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}|Present|Current)",
        re.IGNORECASE,
    )

    # match bare year-ranges with optional surrounding parens: (2022-Present) or 2020–2022
    year_range = re.compile(
        r"\(?\b(20\d{2}|19\d{2})\s*[-\u2013\u2014to]+\s*(20\d{2}|19\d{2}|Present|Current)\b\)?",
        re.IGNORECASE,
    )

    in_exp_section = False
    current_entry: Optional[dict] = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if exp_header_pattern.search(stripped):
            in_exp_section = True
            continue

        if in_exp_section and re.match(
            r"^(?:education|skills|projects|certifications?|awards?|publications?|interests?|hobbies|references?)\b",
            stripped,
            re.IGNORECASE,
        ):
            if current_entry:
                experience.append(current_entry)
                current_entry = None
            in_exp_section = False
            continue

        if in_exp_section:
            date_match = date_pattern.search(stripped) or year_range.search(stripped)
            if date_match:
                if current_entry:
                    experience.append(current_entry)

                title_part = stripped[: date_match.start()].strip().rstrip("|-\u2013\u2014,")
                parts = re.split(r"\s*[|@,]\s*", title_part, maxsplit=1)
                title = parts[0].strip() if parts else stripped
                company = parts[1].strip() if len(parts) > 1 else ""

                current_entry = {
                    "title": title,
                    "company": company,
                    "duration": date_match.group().strip(),
                    "highlights": [],
                }
            elif current_entry and (stripped.startswith("\u2022") or stripped.startswith("-") or stripped.startswith("*")):
                current_entry["highlights"].append(stripped.lstrip("\u2022-* ").strip())

    if current_entry:
        experience.append(current_entry)

    return experience[:10]


def _extract_education(text: str) -> list[dict]:
    """Extract education entries heuristically."""
    import re

    education: list[dict] = []
    lines = text.split("\n")

    edu_header_pattern = re.compile(r"(?:education|academic|qualification|degree)", re.IGNORECASE)

    degree_pattern = re.compile(
        r"\b(?:B\.\s*(?:Tech|Sc|A|E|Com|Eng)|M\.\s*(?:Tech|Sc|A|E|S|Com|Eng|BA)"
        r"|Bachelor|Master|Ph\.?D|Doctorate|MBA|MCA|BCA"
        r"|B\.?S\.?c?|M\.?S\.?c?|B\.?E\.?|M\.?E\.?|B\.?A\.?|M\.?A\.?)\b",
        re.IGNORECASE,
    )

    in_edu_section = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if edu_header_pattern.search(stripped) and len(stripped.split()) <= 4:
            in_edu_section = True
            continue

        if in_edu_section and re.match(
            r"^(?:experience|skills|projects|certifications?|work)\b", stripped, re.IGNORECASE
        ):
            in_edu_section = False
            continue

        if in_edu_section or degree_pattern.search(stripped):
            if degree_pattern.search(stripped):
                year_match = re.search(r"\b(19|20)\d{2}\b", stripped)
                year = year_match.group() if year_match else ""

                parts = re.split(r"\s*[-\u2013\u2014|,]\s*", stripped, maxsplit=2)
                degree_text = parts[0].strip() if parts else stripped
                institution = parts[1].strip() if len(parts) > 1 else ""

                education.append({
                    "degree": degree_text,
                    "institution": institution,
                    "year": year,
                })

    return education[:5]


def _generate_resume_summary(
    name: Optional[str],
    skills: list[str],
    experience_count: int,
    education: list[dict],
) -> str:
    """Generate a brief summary of the resume."""
    parts: list[str] = []

    if name:
        parts.append(f"{name} is a professional")
    else:
        parts.append("The candidate is a professional")

    if skills:
        top_skills = skills[:5]
        parts.append(f"with expertise in {', '.join(top_skills)}")

    if experience_count > 0:
        parts.append(f"and {experience_count} documented work experience{'s' if experience_count > 1 else ''}")

    if education:
        edu = education[0]
        degree = edu.get("degree", "")
        if degree:
            parts.append(f"holding a {degree}")

    summary = " ".join(parts) + "."
    return summary


# ── 2. Question Generation ───────────────────────────────────────────


PERSONALITY_INSTRUCTIONS = {
    "friendly": "Warm, supportive HR interviewer with encouraging questions.",
    "technical": "Strict senior engineer with deep technical dive questions.",
    "stress": "High-pressure stress interviewer with tough, challenging questions.",
    "panel": "Panel of interviewers covering technical, leadership, and cultural fit.",
}


def generate_questions(
    resume_text: str,
    personality: str = "friendly",
    num_questions: int = 10,
    resume_analysis: Optional[dict] = None,
) -> list[dict]:
    """
    Generate interview questions tailored to the candidate's resume.
    Uses the custom NLP question bank — no external API needed.
    Returns: [{ "question": "...", "category": "...", "difficulty": "..." }]
    """
    if resume_analysis and resume_analysis.get("technical_skills"):
        detected_skills = resume_analysis["technical_skills"]
    else:
        detected_skills = extract_skill_names(resume_text)

    questions = select_questions(
        detected_skills=detected_skills,
        personality=personality,
        num_questions=num_questions,
    )

    return [
        {
            "question": q["question"],
            "category": q["category"],
            "difficulty": q["difficulty"],
        }
        for q in questions
    ]


# ── 3. Answer Evaluation ─────────────────────────────────────────────


def evaluate_responses(
    resume_text: str,
    personality: str,
    responses: list[dict],
) -> dict:
    """
    Evaluate all interview responses using the custom NLP engine.

    Each response dict may contain:
      • question            (str, required)
      • answer              (str, required)
      • input_mode          (str: 'text' | 'audio' | 'video', optional)
      • recording_duration  (int | float seconds, optional)

    Video and audio responses are routed through the delivery-aware
    video_analyser model which scores confidence, emotional stability
    and sentiment from speaking pace, filler density and prosody proxies
    in addition to text NLP.

    Returns: {
        "technical_accuracy": float 0-100,
        "language_proficiency": float 0-100,
        "confidence_level": float 0-100,
        "sentiment_score": float 0-100,
        "emotional_stability": float 0-100,
        "overall_score": float 0-100,
        "per_question_feedback": [{ ... }],
        "recommendations": [str],
        "summary_feedback": str
    }
    """
    if not responses:
        return _empty_evaluation()

    skill_keywords = extract_keywords(resume_text, top_n=40)

    per_question_scores: list[dict] = []
    per_question_feedback: list[dict] = []
    all_scores: dict[str, list[float]] = {
        "technical_accuracy": [],
        "language_proficiency": [],
        "confidence_level": [],
        "sentiment_score": [],
        "emotional_stability": [],
    }

    for i, resp in enumerate(responses):
        question = resp.get("question", "")
        answer = resp.get("answer", "")
        input_mode = resp.get("input_mode", "text") or "text"
        recording_duration = float(resp.get("recording_duration", 0) or 0)

        # Route video/audio through delivery-aware model
        if input_mode in ("video", "audio") and answer.strip() and not answer.startswith("["):
            scores = score_video_answer(
                question=question,
                answer=answer,
                recording_duration=recording_duration,
                input_mode=input_mode,
                skill_keywords=skill_keywords,
            )
        else:
            scores = score_answer(question, answer, skill_keywords)

        per_question_scores.append(scores)

        if not scores.get("is_placeholder"):
            for key in all_scores:
                all_scores[key].append(scores.get(key, 50))

        feedback = generate_answer_feedback(question, answer, scores)
        feedback["question_index"] = i
        feedback["input_mode"] = input_mode

        # Attach delivery metrics for video/audio responses so frontend can display them
        if input_mode in ("video", "audio") and not scores.get("is_placeholder"):
            feedback["delivery"] = {
                "speaking_pace_wpm": scores.get("speaking_pace_wpm", 0),
                "filler_count": scores.get("filler_count", 0),
                "filler_density": round(scores.get("filler_density", 0) * 100, 1),  # as %
                "utilization_ratio": round(scores.get("utilization_ratio", 0) * 100, 1),  # as %
                "delivery_quality": scores.get("delivery_quality", 0),
                "confidence_marker_count": scores.get("confidence_marker_count", 0),
            }

        per_question_feedback.append(feedback)

    def safe_avg(values: list[float]) -> float:
        # Return 0 if no real (non-placeholder) responses contributed scores
        return sum(values) / len(values) if values else 0.0

    metric_scores = {
        "technical_accuracy": round(safe_avg(all_scores["technical_accuracy"]), 1),
        "language_proficiency": round(safe_avg(all_scores["language_proficiency"]), 1),
        "confidence_level": round(safe_avg(all_scores["confidence_level"]), 1),
        "sentiment_score": round(safe_avg(all_scores["sentiment_score"]), 1),
        "emotional_stability": round(safe_avg(all_scores["emotional_stability"]), 1),
    }

    weights = {
        "technical_accuracy": 0.30,
        "language_proficiency": 0.25,
        "confidence_level": 0.20,
        "sentiment_score": 0.10,
        "emotional_stability": 0.15,
    }
    overall = sum(metric_scores[k] * weights[k] for k in weights)

    if personality == "technical":
        overall = overall * 0.85 + metric_scores["technical_accuracy"] * 0.15
    elif personality == "stress":
        overall = overall * 0.85 + metric_scores["emotional_stability"] * 0.15

    metric_scores["overall_score"] = round(overall, 1)

    recommendations = generate_recommendations(metric_scores, per_question_scores, responses=responses)

    summary = generate_summary(
        metric_scores,
        num_questions=len(responses),
        personality=personality,
    )

    return {
        **metric_scores,
        "per_question_feedback": per_question_feedback,
        "recommendations": recommendations,
        "summary_feedback": summary,
    }


def _empty_evaluation() -> dict:
    """Return empty evaluation when no responses provided."""
    return {
        "technical_accuracy": 0,
        "language_proficiency": 0,
        "confidence_level": 0,
        "sentiment_score": 0,
        "emotional_stability": 0,
        "overall_score": 0,
        "per_question_feedback": [],
        "recommendations": [
            "Complete the interview by answering the questions to receive a full evaluation."
        ],
        "summary_feedback": "No responses were provided for evaluation.",
    }
