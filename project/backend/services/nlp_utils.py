"""
Custom NLP Utilities for InterviewIQ — Zero external AI dependencies.

Provides:
  - Tokenisation & keyword extraction
  - Skill taxonomy matching
  - Sentiment analysis (custom word-list-based)
  - Confidence / hedging detection
  - Text quality metrics
  - Relevance scoring between question & answer
  - Entity extraction (name, email, phone)
"""

import math
import re
from collections import Counter
from typing import Optional

# ────────────────────────────────────────────────────────────────
# Stop-words (common English words to ignore in keyword extraction)
# ────────────────────────────────────────────────────────────────

STOP_WORDS: set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "get", "got", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how",
    "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "just", "let's", "like", "me",
    "might", "more", "most", "mustn't", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "quite", "really", "s",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "t", "than", "that", "that's",
    "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up",
    "upon", "us", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when",
    "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "will", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "also", "still", "well", "using", "used",
    "use", "make", "made", "one", "two", "new", "even", "work",
    "worked", "working", "many", "much", "way", "may", "need",
}

# ────────────────────────────────────────────────────────────────
# Comprehensive Skill Taxonomy
# ────────────────────────────────────────────────────────────────

TECHNICAL_SKILLS: dict[str, list[str]] = {
    # Programming Languages
    "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "scipy", "matplotlib", "pytorch", "tensorflow", "keras"],
    "javascript": ["javascript", "js", "es6", "es2015", "ecmascript", "vanilla js"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "jvm", "spring", "spring boot", "hibernate", "maven", "gradle"],
    "cpp": ["c++", "cpp", "c plus plus"],
    "csharp": ["c#", "csharp", "c sharp", ".net", "asp.net", "dotnet"],
    "go": ["go", "golang"],
    "rust": ["rust", "cargo"],
    "ruby": ["ruby", "rails", "ruby on rails"],
    "php": ["php", "laravel", "symfony", "wordpress"],
    "swift": ["swift", "swiftui", "ios development"],
    "kotlin": ["kotlin", "android development"],
    "scala": ["scala", "akka", "play framework"],
    "r": ["r programming", "r language", "rstudio", "ggplot"],

    # Web Frontend
    "react": ["react", "reactjs", "react.js", "react native", "jsx", "tsx", "hooks", "redux", "next.js", "nextjs"],
    "angular": ["angular", "angularjs", "angular.js", "rxjs", "ngrx"],
    "vue": ["vue", "vuejs", "vue.js", "vuex", "nuxt", "nuxt.js"],
    "svelte": ["svelte", "sveltekit"],
    "html_css": ["html", "html5", "css", "css3", "sass", "scss", "less", "tailwind", "tailwindcss", "bootstrap", "material ui", "mui"],
    "frontend": ["webpack", "vite", "babel", "rollup", "parcel", "esbuild"],

    # Web Backend
    "nodejs": ["node", "node.js", "nodejs", "express", "express.js", "nestjs", "koa", "hapi"],
    "django": ["django", "django rest framework", "drf"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "starlette", "pydantic"],
    "spring": ["spring", "spring boot", "spring mvc", "spring security"],
    "rails": ["rails", "ruby on rails", "activerecord"],

    # Databases
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "sql server", "mssql", "mariadb"],
    "nosql": ["mongodb", "nosql", "couchdb", "dynamodb", "cassandra", "hbase"],
    "redis": ["redis", "memcached", "caching"],
    "elasticsearch": ["elasticsearch", "elastic", "kibana", "logstash", "elk"],

    # Cloud & DevOps
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "rds", "cloudfront", "sqs", "sns", "ecs", "eks", "fargate"],
    "azure": ["azure", "microsoft azure", "azure devops", "azure functions"],
    "gcp": ["gcp", "google cloud", "google cloud platform", "bigquery", "cloud run", "firebase"],
    "docker": ["docker", "dockerfile", "docker-compose", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s", "helm", "kubectl", "container orchestration"],
    "cicd": ["ci/cd", "cicd", "jenkins", "github actions", "gitlab ci", "circleci", "travis ci", "bamboo", "argo cd"],
    "terraform": ["terraform", "infrastructure as code", "iac", "cloudformation", "pulumi"],
    "linux": ["linux", "unix", "bash", "shell scripting", "ubuntu", "centos", "debian"],

    # Data & ML
    "machine_learning": ["machine learning", "ml", "deep learning", "neural network", "ai", "artificial intelligence"],
    "data_science": ["data science", "data analysis", "data analytics", "data engineering", "etl", "data pipeline"],
    "nlp": ["nlp", "natural language processing", "text mining", "text analysis", "language model"],
    "computer_vision": ["computer vision", "image processing", "opencv", "image recognition", "object detection"],

    # Mobile
    "android": ["android", "android studio", "kotlin android", "java android"],
    "ios": ["ios", "xcode", "swiftui", "uikit", "cocoapods"],
    "react_native": ["react native"],
    "flutter": ["flutter", "dart"],

    # Architecture & Concepts
    "system_design": ["system design", "architecture", "microservices", "monolith", "distributed systems", "scalability", "high availability"],
    "api_design": ["rest", "rest api", "restful", "graphql", "grpc", "websocket", "api design", "openapi", "swagger"],
    "testing": ["unit testing", "integration testing", "e2e testing", "tdd", "bdd", "jest", "pytest", "junit", "selenium", "cypress", "playwright"],
    "design_patterns": ["design patterns", "solid", "singleton", "factory", "observer", "strategy", "mvc", "mvvm"],
    "dsa": ["data structures", "algorithms", "sorting", "searching", "trees", "graphs", "dynamic programming", "big o", "complexity"],
    "security": ["security", "cybersecurity", "authentication", "authorization", "oauth", "jwt", "encryption", "ssl", "tls", "owasp"],
    "devops": ["devops", "sre", "site reliability", "monitoring", "logging", "observability", "prometheus", "grafana", "datadog"],

    # Tools
    "git": ["git", "github", "gitlab", "bitbucket", "version control", "branching"],
    "agile": ["agile", "scrum", "kanban", "sprint", "jira", "trello", "project management"],
}

SOFT_SKILLS: dict[str, list[str]] = {
    "leadership": ["leadership", "lead", "leading", "leader", "managed", "managing", "manager", "directed", "oversaw", "supervised"],
    "communication": ["communication", "communicated", "presented", "presenting", "presentation", "articulate", "writing", "written"],
    "teamwork": ["teamwork", "team", "collaborated", "collaborating", "collaboration", "cross-functional", "cooperative"],
    "problem_solving": ["problem solving", "problem-solving", "troubleshooting", "debugging", "root cause", "analytical", "analysis"],
    "adaptability": ["adaptability", "adaptable", "flexible", "flexibility", "versatile", "agile", "quick learner"],
    "time_management": ["time management", "deadline", "deadlines", "prioritization", "multitasking", "organized"],
    "creativity": ["creativity", "creative", "innovative", "innovation", "ideation", "brainstorming"],
    "mentoring": ["mentoring", "mentor", "coaching", "training", "onboarding", "knowledge sharing"],
}

# ────────────────────────────────────────────────────────────────
# Sentiment Word Lists (trained data)
# ────────────────────────────────────────────────────────────────

POSITIVE_WORDS: set[str] = {
    "excellent", "great", "good", "amazing", "outstanding", "exceptional",
    "achieved", "accomplished", "improved", "increased", "enhanced",
    "optimized", "streamlined", "innovative", "efficient", "effective",
    "successful", "proficient", "experienced", "skilled", "expertise",
    "passionate", "motivated", "dedicated", "committed", "enthusiastic",
    "proactive", "reliable", "thorough", "precise", "accurate",
    "wonderful", "fantastic", "superb", "brilliant", "impressive",
    "strong", "confident", "capable", "competent", "qualified",
    "love", "enjoy", "excited", "thrilled", "proud", "delighted",
    "rewarding", "meaningful", "impactful", "significant", "valuable",
    "positive", "optimistic", "constructive", "beneficial", "productive",
    "robust", "scalable", "performant", "elegant", "clean",
    "comprehensive", "advanced", "sophisticated", "strategic", "critical",
    "mastered", "delivered", "spearheaded", "championed", "transformed",
    "accelerated", "reduced", "saved", "resolved", "solved",
    "contributed", "collaborated", "mentored", "led", "built",
    "designed", "developed", "implemented", "deployed", "launched",
    "definitely", "absolutely", "certainly", "clearly", "exactly",
}

NEGATIVE_WORDS: set[str] = {
    "bad", "poor", "terrible", "awful", "horrible", "worst",
    "failed", "failure", "failing", "mistake", "error", "wrong",
    "weak", "weakness", "lacking", "insufficient", "inadequate",
    "difficult", "struggle", "struggled", "struggling", "hard",
    "never", "couldn't", "can't", "unable", "impossible",
    "confusing", "confused", "complicated", "complex", "messy",
    "slow", "delayed", "missed", "lost", "broke", "broken",
    "frustrated", "frustrating", "annoying", "boring", "tedious",
    "hate", "dislike", "unfortunately", "sadly", "regret",
    "problem", "issue", "bug", "crash", "downtime",
    "quit", "fired", "terminated", "rejected", "denied",
    "worried", "anxious", "nervous", "stressed", "overwhelmed",
    "mediocre", "average", "basic", "minimal", "limited",
    "don't know", "not sure", "no idea", "no experience",
}

CONFIDENCE_WORDS: set[str] = {
    "definitely", "absolutely", "certainly", "clearly", "obviously",
    "confident", "sure", "positive", "convinced", "believe",
    "know", "proven", "demonstrated", "established", "achieved",
    "successfully", "effectively", "efficiently", "precisely", "expertly",
    "always", "consistently", "thoroughly", "completely", "fully",
    "strong", "solid", "robust", "extensive", "comprehensive",
    "mastered", "excelled", "specialized", "proficient", "fluent",
    "without doubt", "no question", "undoubtedly", "unquestionably",
    # Strong action verbs (past tense — evidence of confident delivery)
    "designed", "implemented", "led", "built", "created", "developed",
    "delivered", "managed", "architected", "launched", "deployed",
    "improved", "optimised", "optimized", "reduced", "increased",
    "solved", "resolved", "automated", "streamlined", "integrated",
    "mentored", "trained", "presented", "negotiated", "coordinated",
    "owned", "drove", "executed", "completed", "shipped",
    "specifically", "directly", "precisely", "exactly",
    "i designed", "i implemented", "i led", "i built", "i created",
    "i developed", "i delivered", "i managed", "i achieved", "i resolved",
}

HEDGING_WORDS: set[str] = {
    "maybe", "perhaps", "possibly", "probably", "might",
    "could", "would", "should", "kind of", "sort of",
    "i think", "i guess", "i suppose", "i believe", "i feel",
    "somewhat", "fairly", "rather", "quite", "a bit",
    "not sure", "not certain", "not really", "not exactly",
    "like", "basically", "essentially", "generally", "typically",
    "sometimes", "occasionally", "often", "usually",
    "try", "trying", "attempt", "hope", "hopefully",
    "tend to", "seems like", "appears to", "in a way",
}

FILLER_WORDS: set[str] = {
    "um", "uh", "like", "you know", "basically", "actually",
    "literally", "honestly", "right", "so", "well", "anyway",
    "i mean", "sort of", "kind of", "stuff", "things",
}

# ────────────────────────────────────────────────────────────────
# Core NLP Functions
# ────────────────────────────────────────────────────────────────


def tokenize(text: str) -> list[str]:
    """Split text into lowercase word tokens, stripping punctuation."""
    return re.findall(r"[a-z0-9#+.]+", text.lower())


def extract_keywords(text: str, top_n: int = 30) -> list[str]:
    """Extract top-N keywords by frequency, ignoring stop-words."""
    words = [w for w in tokenize(text) if w not in STOP_WORDS and len(w) > 2]
    counts = Counter(words)
    return [w for w, _ in counts.most_common(top_n)]


def extract_skills(text: str) -> dict[str, list[str]]:
    """
    Detect technical and soft skills from text.
    Returns: {"technical": {"python": [...matches], ...}, "soft": {"leadership": [...matches], ...}}
    """
    text_lower = text.lower()
    found_technical: dict[str, list[str]] = {}
    found_soft: dict[str, list[str]] = {}

    for skill_key, keywords in TECHNICAL_SKILLS.items():
        matches = [kw for kw in keywords if kw.lower() in text_lower]
        if matches:
            found_technical[skill_key] = matches

    for skill_key, keywords in SOFT_SKILLS.items():
        matches = [kw for kw in keywords if kw.lower() in text_lower]
        if matches:
            found_soft[skill_key] = matches

    return {"technical": found_technical, "soft": found_soft}


def extract_skill_names(text: str) -> list[str]:
    """Get flat list of detected skill domain names."""
    skills = extract_skills(text)
    all_skills = list(skills["technical"].keys()) + list(skills["soft"].keys())
    return all_skills


def extract_entities(text: str) -> dict:
    """Extract structured entities from text using regex patterns."""
    entities: dict = {
        "name": None,
        "email": None,
        "phone": None,
        "urls": [],
    }

    # Email
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    if email_match:
        entities["email"] = email_match.group()

    # Phone
    phone_match = re.search(r"[\+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]{7,15}", text)
    if phone_match:
        entities["phone"] = phone_match.group().strip()

    # URLs (LinkedIn, GitHub, portfolio)
    urls = re.findall(r"https?://[^\s<>\"']+|www\.[^\s<>\"']+", text)
    entities["urls"] = urls[:5]

    # Name heuristic: first non-empty line that looks like a name
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        # Skip lines with email, phone, urls, or too many words
        if "@" in line or "http" in line or len(line.split()) > 4:
            continue
        # Check if it looks like a name (2-3 title-case words, no digits)
        words = line.split()
        if 1 <= len(words) <= 3 and all(w[0].isupper() for w in words if w) and not re.search(r"\d", line):
            entities["name"] = line
            break

    return entities


# ────────────────────────────────────────────────────────────────
# Sentiment & Confidence Analysis
# ────────────────────────────────────────────────────────────────


def analyze_sentiment(text: str) -> dict:
    """
    Analyse sentiment of text using word-list scoring.
    Returns: {"score": 0-100, "positive_count": int, "negative_count": int, "ratio": float}
    """
    words = tokenize(text)
    text_lower = text.lower()

    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

    # Also check multi-word phrases
    for phrase in POSITIVE_WORDS:
        if " " in phrase and phrase in text_lower:
            pos_count += 1
    for phrase in NEGATIVE_WORDS:
        if " " in phrase and phrase in text_lower:
            neg_count += 1

    total = pos_count + neg_count
    word_count = len(words)
    ratio = 0.0
    if total == 0:
        # No sentiment signal detected — score proportional to response length.
        # Very short answers can't demonstrate positive engagement so they score low.
        # 0 words → 0, 10 words → ~14, 30+ words → cap at 45 (still below a positive answer).
        score = min(45, max(0, word_count * 1.4))
    else:
        ratio = pos_count / total
        # Map ratio to 0-100 score (0.0 → 15, 0.5 → 55, 1.0 → 95)
        raw = min(95, max(15, ratio * 80 + 15))
        # Scale down slightly for very brief answers even when they have sentiment words
        length_factor = min(1.0, word_count / 20)
        score = raw * length_factor

    return {
        "score": round(score, 1),
        "positive_count": pos_count,
        "negative_count": neg_count,
        "ratio": round(ratio, 3),
    }


def analyze_confidence(text: str) -> dict:
    """
    Measure confidence vs hedging in text.
    Returns: {"score": 0-100, "confident_count": int, "hedging_count": int}
    """
    text_lower = text.lower()

    conf_count = sum(1 for w in CONFIDENCE_WORDS if w in text_lower)
    hedge_count = sum(1 for w in HEDGING_WORDS if w in text_lower)
    filler_count = sum(1 for w in FILLER_WORDS if w in text_lower)

    total = conf_count + hedge_count + filler_count
    if total == 0:
        score = 55.0  # neutral
    else:
        confidence_ratio = conf_count / total
        score = min(95, max(15, confidence_ratio * 85 + 15))

    # Penalise heavy filler word usage
    word_count = len(tokenize(text))
    if word_count > 0:
        filler_density = filler_count / word_count
        if filler_density > 0.1:
            score = max(15, score - 15)

    return {
        "score": round(score, 1),
        "confident_count": conf_count,
        "hedging_count": hedge_count,
        "filler_count": filler_count,
    }


def analyze_text_quality(text: str) -> dict:
    """
    Analyse text quality: vocabulary richness, sentence length, structure.
    Returns: {"score": 0-100, "word_count", "sentence_count", "avg_sentence_len",
              "vocabulary_richness", "has_structure"}
    """
    words = tokenize(text)
    word_count = len(words)

    # Sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = max(len(sentences), 1)
    avg_sentence_len = word_count / sentence_count

    # Vocabulary richness (type-token ratio)
    unique_words = set(words)
    vocab_richness = len(unique_words) / max(word_count, 1)

    # Structure detection (numbered points, paragraphs, etc.)
    has_structure = bool(
        re.search(r"(?:^|\n)\s*(?:\d+[.)]|\-|\•|\*)\s", text)
        or text.count("\n\n") >= 1
    )

    # Calculate score
    score = 30.0  # base

    # Word count bonus (longer = more detailed, up to a point)
    if word_count >= 200:
        score += 25
    elif word_count >= 100:
        score += 20
    elif word_count >= 50:
        score += 15
    elif word_count >= 20:
        score += 8
    else:
        score -= 10

    # Sentence length bonus (ideal: 12-25 words per sentence)
    if 12 <= avg_sentence_len <= 25:
        score += 15
    elif 8 <= avg_sentence_len <= 35:
        score += 8
    else:
        score -= 5

    # Vocabulary richness bonus
    if vocab_richness >= 0.6:
        score += 15
    elif vocab_richness >= 0.4:
        score += 10
    elif vocab_richness >= 0.25:
        score += 5

    # Structure bonus
    if has_structure:
        score += 10

    score = min(95, max(10, score))

    return {
        "score": round(score, 1),
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_len": round(avg_sentence_len, 1),
        "vocabulary_richness": round(vocab_richness, 3),
        "has_structure": has_structure,
    }


def calculate_relevance(question: str, answer: str, context_keywords: Optional[list[str]] = None) -> float:
    """
    Calculate how relevant an answer is to a question.
    Returns a score from 0.0 to 1.0.
    """
    q_words = set(tokenize(question)) - STOP_WORDS
    a_words = set(tokenize(answer)) - STOP_WORDS

    if not q_words or not a_words:
        return 0.2

    # Word overlap
    overlap = q_words & a_words
    overlap_ratio = len(overlap) / max(len(q_words), 1)

    # Context keyword match (skills mentioned in resume)
    context_score = 0.0
    if context_keywords:
        context_lower = {kw.lower() for kw in context_keywords}
        a_text_lower = answer.lower()
        matched = sum(1 for kw in context_lower if kw in a_text_lower)
        context_score = matched / max(len(context_lower), 1)

    # Combined score
    relevance = overlap_ratio * 0.5 + context_score * 0.3 + 0.2  # base 0.2
    return min(1.0, relevance)


# ────────────────────────────────────────────────────────────────
# Comprehensive Answer Scoring
# ────────────────────────────────────────────────────────────────


def score_answer(question: str, answer: str, skill_keywords: Optional[list[str]] = None) -> dict:
    """
    Full NLP scoring of a single answer.
    Returns scores for: technical_accuracy, language, confidence, sentiment, stability.
    """
    # Skip placeholder/empty answers — every score is 0 when no input was given
    if not answer.strip() or answer.startswith("["):
        return {
            "technical_accuracy": 0,
            "language_proficiency": 0,
            "confidence_level": 0,
            "sentiment_score": 0,
            "emotional_stability": 0,
            "relevance": 0.0,
            "word_count": 0,
            "is_placeholder": True,
        }

    text_quality = analyze_text_quality(answer)
    sentiment = analyze_sentiment(answer)
    confidence = analyze_confidence(answer)
    relevance = calculate_relevance(question, answer, skill_keywords)

    # Technical accuracy: relevance + keyword depth + detail
    tech_base = relevance * 50 + text_quality["score"] * 0.3
    if skill_keywords:
        answer_lower = answer.lower()
        skill_hits = sum(1 for kw in skill_keywords if kw.lower() in answer_lower)
        tech_base += min(20, skill_hits * 5)
    technical_accuracy = min(95, max(10, tech_base))

    # Language proficiency: text quality + vocabulary
    language = text_quality["score"]

    # Confidence level
    conf = confidence["score"]

    # Sentiment score
    sent = sentiment["score"]

    # Emotional stability: derived from actual content volume + composure indicators.
    # Base scales from 0 → 50 as word count grows (0 words=0, 20 words=~30, 40+ words=50).
    # This means an answer with no content can never score a phantom 55.
    wc = text_quality["word_count"]
    stability_base = min(50.0, wc * 1.25)
    # Adjust for composure signals
    if sentiment["negative_count"] > sentiment["positive_count"] * 2:
        stability_base -= 10
    if confidence["hedging_count"] > confidence["confident_count"] * 2:
        stability_base -= 8
    # Reward substantive answers (30+ words show composure under pressure)
    if wc >= 30:
        stability_base += 18
    # Reward positive/confident framing
    if sentiment["positive_count"] >= 2 and confidence["confident_count"] >= 1:
        stability_base += 8
    stability = min(95, max(0, stability_base))

    return {
        "technical_accuracy": round(technical_accuracy),
        "language_proficiency": round(language),
        "confidence_level": round(conf),
        "sentiment_score": round(sent),
        "emotional_stability": round(stability),
        "relevance": round(relevance, 2),
        "word_count": text_quality["word_count"],
        "is_placeholder": False,
    }


def generate_answer_feedback(question: str, answer: str, scores: dict) -> dict:
    """Generate specific, crystal-clear feedback for a single interview answer."""
    if scores.get("is_placeholder"):
        return {
            "score": 0,
            "strength": "No response recorded",
            "improvement": "Provide a verbal or text response to receive a proper evaluation",
        }

    wc = scores.get("word_count", 0)

    # Weighted score matching the overall evaluation weights
    final_score = round(
        scores["technical_accuracy"] * 0.30
        + scores["language_proficiency"] * 0.25
        + scores["confidence_level"] * 0.20
        + scores["sentiment_score"] * 0.10
        + scores["emotional_stability"] * 0.15
    )

    # Identify the strongest dimension with a specific, informative label
    dims = [
        ("technical_accuracy", scores["technical_accuracy"],
         f"Strong technical content — answer was {scores['technical_accuracy']}% accurate with solid topic relevance"),
        ("language_proficiency", scores["language_proficiency"],
         f"Well-structured communication — clear, articulate sentences ({scores['language_proficiency']}% language score)"),
        ("confidence_level", scores["confidence_level"],
         f"Confident delivery — assertive language with minimal hedging ({scores['confidence_level']}% confidence)"),
        ("sentiment_score", scores["sentiment_score"],
         f"Positive and professional tone maintained ({scores['sentiment_score']}% sentiment)"),
        ("emotional_stability", scores["emotional_stability"],
         f"Composed and consistent response style ({scores['emotional_stability']}% stability)"),
    ]
    best = max(dims, key=lambda x: x[1])
    if best[1] >= 65:
        strength = best[2]
    elif wc >= 80:
        strength = f"Detailed response — provided {wc} words with reasonable coverage of the topic"
    else:
        strength = "Made an attempt to address the question — foundation exists to build on"

    # Identify the most critical specific improvement needed
    worst = min(dims, key=lambda x: x[1])
    if worst[1] < 55:
        if worst[0] == "technical_accuracy":
            improvement = (
                f"Technical depth scored only {worst[1]}% — include concrete specifics: "
                "name the exact technologies you used, describe your approach, and state a measurable outcome"
            )
        elif worst[0] == "language_proficiency":
            improvement = (
                f"Language clarity scored {worst[1]}% — use the STAR method: "
                "start with the direct answer, give context, then elaborate with action and result"
            )
        elif worst[0] == "confidence_level":
            improvement = (
                f"Confidence scored only {worst[1]}% — replace 'I think', 'maybe', 'sort of' "
                "with direct statements: 'I implemented', 'I led', 'the outcome was'"
            )
        elif worst[0] == "sentiment_score":
            improvement = (
                f"Tone scored {worst[1]}% — reframe negatives as growth: "
                "instead of 'I had difficulty with X', say 'I tackled X by doing Y and achieved Z'"
            )
        else:
            improvement = (
                f"Stability scored {worst[1]}% — keep pace and tone steady throughout; "
                "avoid trailing off or rushing at the end of your answer"
            )
    elif wc < 30:
        improvement = (
            f"Response was only {wc} words — too brief to assess competency. "
            "Aim for 60–90 seconds: cover what you did, how you did it, and the outcome"
        )
    elif scores.get("relevance", 1) < 0.35:
        improvement = (
            "Answer didn't directly address the question asked. "
            "Lead with the direct answer, then support it with a relevant example or data point"
        )
    else:
        improvement = (
            "Good foundation — add a specific quantified achievement: "
            "include percentages, time savings, team sizes, or project scale to make your answer memorable"
        )

    return {
        "score": final_score,
        "strength": strength,
        "improvement": improvement,
    }


def generate_recommendations(
    metric_scores: dict,
    per_question_scores: list[dict],
    responses: list[dict] | None = None,
) -> list[str]:
    """
    Generate interview-specific, actionable recommendations based on the
    actual questions asked and answers given — not generic advice.
    """
    recs: list[str] = []
    actual_responses = responses or []

    ta = metric_scores.get("technical_accuracy", 50)
    lp = metric_scores.get("language_proficiency", 50)
    cl = metric_scores.get("confidence_level", 50)
    ss = metric_scores.get("sentiment_score", 50)
    es = metric_scores.get("emotional_stability", 50)
    total = len(per_question_scores)

    # ── 1. Identify the weakest specific questions (content-aware) ──
    scored = [
        (i, s) for i, s in enumerate(per_question_scores)
        if not s.get("is_placeholder") and i < len(actual_responses)
    ]
    scored.sort(key=lambda x: (
        x[1].get("technical_accuracy", 50)
        + x[1].get("language_proficiency", 50)
        + x[1].get("confidence_level", 50)
    ) / 3)

    for idx, scores in scored[:2]:  # focus on 2 lowest-scoring questions
        q_text = actual_responses[idx].get("question", "") if idx < len(actual_responses) else ""
        snippet = q_text[:65].rstrip() + ("…" if len(q_text) > 65 else "")
        avg = round((
            scores.get("technical_accuracy", 50)
            + scores.get("language_proficiency", 50)
            + scores.get("confidence_level", 50)
        ) / 3)
        if avg < 55 and snippet:
            if scores.get("relevance", 1) < 0.35:
                recs.append(
                    f'Q{idx + 1} ("{snippet}") scored {avg}/100. '
                    "Your answer strayed off-topic. Lead with the direct answer to exactly what was asked, "
                    "then support it with one specific example or data point."
                )
            elif scores.get("word_count", 100) < 30:
                recs.append(
                    f'Q{idx + 1} ("{snippet}") scored {avg}/100. '
                    "Response was too brief (under 30 words). Use the 2-minute rule: "
                    "state the answer → give context → describe your action → state the measurable result."
                )
            elif scores.get("technical_accuracy", 60) < 50:
                recs.append(
                    f'Q{idx + 1} ("{snippet}") scored {avg}/100. '
                    "Answer lacked technical specificity. Name the exact tools or technologies used, "
                    "describe your methodology step by step, and include a measurable outcome."
                )

    # ── 2. Metric-based targeted recommendations ────────────────────
    if ta < 65:
        recs.append(
            f"Technical accuracy was {round(ta)}% — below the 65% target. "
            "For each skill on your resume, prepare a 2-minute story: problem faced → "
            "technical approach → measurable result. Practice until it feels natural."
        )
    if lp < 65:
        recs.append(
            f"Language proficiency scored {round(lp)}%. Practice structuring every answer with STAR: "
            "Situation (1–2 sentences) → Task (your role) → Action (specific steps you took) → "
            "Result (number, percentage, or clear outcome)."
        )
    if cl < 65:
        recs.append(
            f"Confidence level was {round(cl)}%. Record your practice sessions and count hedging phrases per minute. "
            "Replace 'I think I could handle it' with 'I handled this by doing X, which achieved Y'."
        )
    if ss < 60:
        recs.append(
            f"Positive sentiment dropped to {round(ss)}%. Frame every challenge as a growth story: "
            "instead of 'I struggled with X', say 'I tackled X by implementing Y and achieved Z'. "
            "Enthusiasm is a strong signal of cultural fit."
        )
    if es < 60:
        recs.append(
            f"Emotional stability scored {round(es)}% — practice the 2-second pause before each reply. "
            "A brief, composed pause signals careful thinking; rushing signals anxiety."
        )

    # ── 3. Answer length pattern ────────────────────────────────────
    short = [i for i, s in enumerate(per_question_scores)
             if s.get("word_count", 0) < 30 and not s.get("is_placeholder")]
    if total > 0 and len(short) / total > 0.3:
        q_nums = ", ".join(f"Q{i + 1}" for i in short[:4])
        recs.append(
            f"Responses for {q_nums} were under 30 words — too brief for interview standards. "
            "Target 60–120 words per answer. If unsure, give more detail and let the interviewer redirect."
        )

    # ── 4. Delivery-specific feedback (audio/video responses) ───────
    av_indices = [
        i for i in range(len(per_question_scores))
        if i < len(actual_responses)
        and actual_responses[i].get("input_mode") in ("audio", "video")
        and not per_question_scores[i].get("is_placeholder")
    ]
    high_filler = [
        i for i in av_indices
        if per_question_scores[i].get("filler_density", 0) > 0.05
    ]
    if high_filler:
        q_nums = ", ".join(f"Q{i + 1}" for i in high_filler[:3])
        recs.append(
            f"Filler words (um, uh, like, you know) were detected in {q_nums}. "
            "A 1–2 second silent pause sounds more confident than any filler word — "
            "it signals you're thinking carefully, not struggling."
        )

    # ── 5. Padding to minimum of 4 recommendations ──────────────────
    if len(recs) < 4:
        recs.append(
            "Practice with all four interviewer personalities (Friendly, Technical, Stress, Panel). "
            "Each requires a different tone and depth — cross-training builds the versatility "
            "that impresses diverse interview panels."
        )
    if len(recs) < 5:
        recs.append(
            "Quantify every achievement: replace 'I improved performance' with "
            "'35% faster page load time', 'reduced bug backlog by 60%', or 'led a team of 5 engineers'."
        )
    if len(recs) < 6:
        recs.append(
            "Research the company's tech stack and recent projects before a real interview. "
            "Referencing their specific context in 2–3 answers significantly boosts recall and relevance."
        )

    return recs[:6]


def generate_summary(metric_scores: dict, num_questions: int, personality: str) -> str:
    """Generate an overall summary assessment."""
    overall = metric_scores.get("overall_score", 50)
    ta = metric_scores.get("technical_accuracy", 50)
    lp = metric_scores.get("language_proficiency", 50)

    if overall >= 80:
        level = "an excellent"
        outlook = "You demonstrated strong competency across all assessed dimensions and would likely perform well in a real interview setting."
    elif overall >= 65:
        level = "a good"
        outlook = "You showed solid foundational skills with room for improvement in specific areas identified above."
    elif overall >= 50:
        level = "a fair"
        outlook = "With targeted practice in the areas highlighted, you can significantly improve your interview performance."
    else:
        level = "a developing"
        outlook = "We recommend focused practice on the recommendations above to build your interview readiness."

    personality_names = {
        "friendly": "Friendly HR",
        "technical": "Technical Deep-Dive",
        "stress": "Stress/Pressure",
        "panel": "Panel Board",
    }
    p_name = personality_names.get(personality, personality.title())

    return (
        f"The candidate completed {level} {p_name} interview with {num_questions} questions, "
        f"achieving an overall score of {overall}%. "
        f"Technical accuracy scored {ta}% and communication clarity scored {lp}%. "
        f"{outlook}"
    )
