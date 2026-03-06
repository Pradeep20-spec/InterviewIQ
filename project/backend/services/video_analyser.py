"""
Video / Audio Response Analyser — InterviewIQ Sentiment & Delivery Engine.

Analyses the *transcript* plus recording metadata (duration, word count)
from video and audio responses to produce delivery-aware scores for:

  • confidence_level      — speaking pace, filler density, assertiveness
  • emotional_stability   — pace consistency, composure under pressure
  • sentiment_score       — text sentiment weighted by delivery signals
  • speaking_pace_wpm     — words per minute (diagnostic)
  • filler_density        — fraction of filler words (diagnostic)
  • utilization_ratio     — how well the candidate used the recording time

These scores REPLACE (not just supplement) the text-only scores for
video and audio responses, because delivery information is far more
informative than pure text NLP when the response came from speech.
"""

from __future__ import annotations

import re
from typing import Optional

# ── Filler Word Taxonomy ─────────────────────────────────────────────
# Weighted by how much each hurts perceived confidence
FILLER_WORDS: dict[str, float] = {
    # Classic fillers — heavy penalty
    "um": 1.0,
    "uh": 1.0,
    "er": 0.9,
    "ah": 0.8,
    "umm": 1.0,
    "uhh": 1.0,
    # Discourse fillers — medium penalty
    "like": 0.6,   # penalised only when high frequency (counted in context)
    "you know": 0.7,
    "i mean": 0.5,
    "basically": 0.5,
    "literally": 0.5,
    "actually": 0.4,
    "honestly": 0.4,
    "right": 0.3,
    "okay so": 0.5,
    "so yeah": 0.5,
    "kind of": 0.5,
    "sort of": 0.5,
    "you see": 0.4,
    # Confidence hedges — mild penalty
    "i think": 0.4,
    "i guess": 0.6,
    "i suppose": 0.5,
    "maybe": 0.3,
    "perhaps": 0.2,
    "possibly": 0.2,
    "i'm not sure": 0.8,
    "i don't know": 0.9,
    "if that makes sense": 0.6,
    "does that make sense": 0.6,
}

# ── Strong Confidence Markers (positive signal) ──────────────────────
CONFIDENCE_MARKERS: list[str] = [
    "i demonstrated",
    "i achieved",
    "i led",
    "i built",
    "i designed",
    "i implemented",
    "i improved",
    "i delivered",
    "we achieved",
    "specifically",
    "for example",
    "for instance",
    "in particular",
    "the key result",
    "the outcome was",
    "i can confirm",
    "i am confident",
    "clearly",
    "precisely",
    "i decided",
    "i chose",
    "i resolved",
]

# ── Speaking Pace Bands ──────────────────────────────────────────────
# WPM ranges and their associated confidence / stability signals
#   < 70  : very slow — uncertain, unprepared                  penalty
#   70-99 : slow — thoughtful but hesitant                     mild penalty
#   100-130: moderate — slightly slow but acceptable           small bonus
#   131-165: ideal — confident, natural, professional          full bonus
#   166-190: fast — enthusiastic or slightly rushed            small penalty
#   > 190 : very fast — anxious, rambling                      penalty

def _classify_wpm(wpm: float) -> tuple[float, float]:
    """
    Return (confidence_modifier, stability_modifier) for a given WPM.
    Both values are additive adjustments to base scores (range -20 to +15).
    """
    if wpm <= 0:
        return -25.0, -20.0  # no speech / complete silence

    if wpm < 70:
        return -18.0, -15.0
    elif wpm < 100:
        return -8.0, -5.0
    elif wpm < 131:
        return 2.0, 5.0
    elif wpm < 166:
        return 15.0, 12.0   # sweet spot
    elif wpm < 191:
        return 0.0, -5.0
    else:
        return -12.0, -10.0


def _count_filler_words(text: str) -> tuple[int, float]:
    """
    Count filler occurrences and their weighted severity.
    Returns (count, weighted_penalty_0_to_100).
    """
    text_lower = text.lower()
    total_count = 0
    weighted_sum = 0.0

    # Multi-word fillers first (order matters — longest first)
    multi_word = sorted(
        [(phrase, weight) for phrase, weight in FILLER_WORDS.items() if " " in phrase],
        key=lambda x: -len(x[0]),
    )
    for phrase, weight in multi_word:
        matches = len(re.findall(r"\b" + re.escape(phrase) + r"\b", text_lower))
        total_count += matches
        weighted_sum += matches * weight

    # Single-word fillers
    words = re.findall(r"\b[a-z']+\b", text_lower)
    for word in words:
        if word in FILLER_WORDS and " " not in word:
            total_count += 1
            weighted_sum += FILLER_WORDS[word]

    return total_count, weighted_sum


def _count_confidence_markers(text: str) -> int:
    """Count positive confidence markers in the transcript."""
    text_lower = text.lower()
    count = 0
    for marker in CONFIDENCE_MARKERS:
        count += len(re.findall(r"\b" + re.escape(marker) + r"\b", text_lower))
    return count


def _sentence_completeness(text: str) -> float:
    """
    Fraction of sentences that are complete (have a verb + subject structure).
    Proxy: sentences with >= 5 words.  Returns 0.0-1.0.
    """
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 0.0
    complete = sum(1 for s in sentences if len(s.split()) >= 5)
    return complete / len(sentences)


def analyse_video_response(
    transcript: str,
    recording_duration: float,       # seconds
    input_mode: str = "video",        # 'video' or 'audio'
    base_text_scores: Optional[dict] = None,  # pre-computed text NLP scores
) -> dict:
    """
    Analyse a spoken (video/audio) response and return delivery-aware scores.

    Parameters
    ----------
    transcript : str
        The speech-to-text transcript of the response.
    recording_duration : float
        Length of the recording in seconds.
    input_mode : str
        'video' or 'audio'.
    base_text_scores : dict | None
        Optional pre-computed scores from score_answer() to blend with
        delivery scores.

    Returns
    -------
    dict with keys:
        confidence_level, emotional_stability, sentiment_score,
        speaking_pace_wpm, filler_density, filler_count,
        utilization_ratio, completeness_ratio, confidence_marker_count,
        delivery_quality  (0-100 overall delivery signal)
    """
    text = transcript.strip()
    words = text.split()
    word_count = len(words)

    # ── 1. Speaking Pace ─────────────────────────────────────────────
    # Use actual duration if available; fall back to word-based estimate
    if recording_duration > 0:
        minutes = recording_duration / 60.0
        wpm = word_count / minutes if minutes > 0 else 0.0
    else:
        # Estimate: average speaker does ~140 WPM, so infer duration
        wpm = 0.0  # unknown duration with words = assume neutral

    pace_conf_mod, pace_stab_mod = _classify_wpm(wpm)

    # ── 2. Filler Word Analysis ───────────────────────────────────────
    filler_count, filler_weight = _count_filler_words(text)
    filler_density = filler_count / max(word_count, 1)

    # Filler penalty (0-40 deduction) — scales with density
    if filler_density > 0.15:        # > 15% of words are fillers → very bad
        filler_penalty = 35.0
    elif filler_density > 0.10:      # 10-15%
        filler_penalty = 25.0
    elif filler_density > 0.06:      # 6-10%
        filler_penalty = 15.0
    elif filler_density > 0.03:      # 3-6%
        filler_penalty = 8.0
    elif filler_density > 0.01:      # 1-3% — light natural use
        filler_penalty = 3.0
    else:
        filler_penalty = 0.0

    # ── 3. Confidence Marker Bonus ───────────────────────────────────
    confidence_marker_count = _count_confidence_markers(text)
    confidence_bonus = min(15.0, confidence_marker_count * 3.0)

    # ── 4. Sentence Completeness ─────────────────────────────────────
    completeness_ratio = _sentence_completeness(text)
    completeness_bonus = completeness_ratio * 10.0  # 0-10 bonus

    # ── 5. Utilization Ratio ─────────────────────────────────────────
    # How well did the candidate fill the recording time?
    # Expected: 120-160 WPM × duration in minutes = expected words
    expected_words = max(1, (recording_duration / 60.0) * 130.0) if recording_duration > 0 else word_count
    utilization_ratio = min(1.0, word_count / expected_words) if expected_words > 0 else 0.5
    utilization_bonus = utilization_ratio * 8.0  # 0-8 bonus

    # ── 6. Confidence Level Score ────────────────────────────────────
    # Base: 55 (neutral) + delivery modifiers
    conf_base = 55.0
    conf_base += pace_conf_mod
    conf_base -= filler_penalty
    conf_base += confidence_bonus
    conf_base += completeness_bonus
    conf_base += utilization_bonus

    # Blend with text-based confidence if available
    if base_text_scores and not base_text_scores.get("is_placeholder"):
        text_conf = base_text_scores.get("confidence_level", 50)
        # 60% delivery, 40% text content for video
        weight_delivery = 0.60 if input_mode == "video" else 0.50
        conf_base = conf_base * weight_delivery + text_conf * (1 - weight_delivery)

    confidence_level = round(min(95.0, max(10.0, conf_base)), 1)

    # ── 7. Emotional Stability Score ─────────────────────────────────
    stab_base = 55.0
    stab_base += pace_stab_mod

    # High filler usage indicates nervousness → lower stability
    stab_base -= filler_penalty * 0.6

    # Moderate pace + good completeness = composed delivery
    stab_base += completeness_ratio * 12.0
    stab_base += utilization_bonus * 0.8

    # Blend with text stability if available
    if base_text_scores and not base_text_scores.get("is_placeholder"):
        text_stab = base_text_scores.get("emotional_stability", 50)
        weight_delivery = 0.55 if input_mode == "video" else 0.45
        stab_base = stab_base * weight_delivery + text_stab * (1 - weight_delivery)

    emotional_stability = round(min(95.0, max(10.0, stab_base)), 1)

    # ── 8. Sentiment Score ───────────────────────────────────────────
    # For spoken responses, delivery pace affects perceived positivity
    if base_text_scores and not base_text_scores.get("is_placeholder"):
        text_sent = base_text_scores.get("sentiment_score", 50)
        # Adjust sentiment: very slow speech can indicate low energy/negativity
        delivery_sent_mod = 0.0
        if wpm > 0:
            if wpm < 80:
                delivery_sent_mod = -8.0
            elif wpm > 185:
                delivery_sent_mod = -5.0
            else:
                delivery_sent_mod = 5.0
        sentiment_score = round(min(95.0, max(10.0, text_sent + delivery_sent_mod)), 1)
    else:
        # No text scores — estimate from delivery and filler density alone
        sent_base = 60.0 - filler_penalty * 0.4 + (pace_conf_mod * 0.3)
        sentiment_score = round(min(95.0, max(10.0, sent_base)), 1)

    # ── 9. Overall Delivery Quality ──────────────────────────────────
    delivery_quality = round(
        (confidence_level * 0.4 + emotional_stability * 0.35 + sentiment_score * 0.25),
        1
    )

    return {
        "confidence_level": confidence_level,
        "emotional_stability": emotional_stability,
        "sentiment_score": sentiment_score,
        "speaking_pace_wpm": round(wpm, 1),
        "filler_density": round(filler_density, 4),
        "filler_count": filler_count,
        "utilization_ratio": round(utilization_ratio, 3),
        "completeness_ratio": round(completeness_ratio, 3),
        "confidence_marker_count": confidence_marker_count,
        "delivery_quality": delivery_quality,
    }


def score_video_answer(
    question: str,
    answer: str,
    recording_duration: float,
    input_mode: str,
    skill_keywords: Optional[list[str]] = None,
) -> dict:
    """
    Full scoring for a video/audio response.

    Combines:
      • Text NLP  (technical_accuracy, language_proficiency, relevance)
      • Video delivery analysis  (confidence, stability, sentiment)

    Returns the same schema as nlp_utils.score_answer() so it is a
    drop-in replacement for the evaluation pipeline.
    """
    # Import here to avoid circular imports
    from services.nlp_utils import score_answer, analyze_text_quality, calculate_relevance

    # 1. Base text-NLP scores (covers technical accuracy, language, relevance)
    base = score_answer(question, answer, skill_keywords)

    # If truly empty / placeholder — no delivery data to add
    if base.get("is_placeholder") or not answer.strip():
        base["recording_duration"] = recording_duration
        base["speaking_pace_wpm"] = 0.0
        base["filler_density"] = 0.0
        base["delivery_quality"] = 0.0
        return base

    # 2. Video delivery analysis — overrides confidence, stability, sentiment
    delivery = analyse_video_response(
        transcript=answer,
        recording_duration=recording_duration,
        input_mode=input_mode,
        base_text_scores=base,
    )

    # 3. Merge: keep technical_accuracy and language_proficiency from text NLP
    #           override confidence, stability, sentiment with delivery model
    merged = {
        "technical_accuracy": base["technical_accuracy"],
        "language_proficiency": base["language_proficiency"],
        "confidence_level": delivery["confidence_level"],
        "sentiment_score": delivery["sentiment_score"],
        "emotional_stability": delivery["emotional_stability"],
        "relevance": base["relevance"],
        "word_count": base["word_count"],
        "is_placeholder": False,
        # Extra diagnostic fields
        "speaking_pace_wpm": delivery["speaking_pace_wpm"],
        "filler_density": delivery["filler_density"],
        "filler_count": delivery["filler_count"],
        "utilization_ratio": delivery["utilization_ratio"],
        "delivery_quality": delivery["delivery_quality"],
        "confidence_marker_count": delivery["confidence_marker_count"],
    }

    return merged
