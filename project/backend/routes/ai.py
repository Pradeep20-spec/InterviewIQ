"""
AI Routes — resume upload/parsing, AI question generation, AI evaluation,
server-side speech-to-text transcription.
"""
import io
import tempfile
import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from database import execute_query
from services.resume_parser import parse_resume
from services.ai_engine import analyse_resume, generate_questions, evaluate_responses

router = APIRouter(prefix="/ai", tags=["AI"])


# ── Request / Response Models ─────────────────────────────────────────

class GenerateQuestionsRequest(BaseModel):
    session_id: str
    personality: str = "friendly"
    num_questions: int = 15


class EvaluateRequest(BaseModel):
    session_id: str


# ── 1. Resume Upload & Parse ─────────────────────────────────────────

@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
):
    """
    Upload a resume file (PDF, DOCX, TXT), extract text, and optionally
    analyse it with AI. Returns the extracted text + AI analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    # Extract text from file
    try:
        resume_text = parse_resume(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not resume_text or len(resume_text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful text from the file. Try pasting your resume text instead.",
        )

    # Run AI analysis
    analysis = analyse_resume(resume_text)

    # If a session_id was provided, update the session with the parsed text
    if session_id:
        try:
            execute_query(
                "UPDATE interview_sessions SET resume_text = %s, resume_filename = %s WHERE id = %s",
                (resume_text, file.filename, session_id),
                fetch=False,
            )
        except Exception:
            pass  # non-critical

    return {
        "success": True,
        "data": {
            "resume_text": resume_text,
            "filename": file.filename,
            "analysis": analysis,
            "char_count": len(resume_text),
        },
    }


@router.post("/resume/analyse")
async def analyse_resume_text(data: dict):
    """Analyse already-extracted resume text with AI."""
    resume_text = data.get("resume_text", "")
    if not resume_text or len(resume_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Resume text too short")

    analysis = analyse_resume(resume_text)
    return {"success": True, "data": analysis}


# ── 2. AI Question Generation ────────────────────────────────────────

@router.post("/questions/generate")
async def generate_ai_questions(request: GenerateQuestionsRequest):
    """
    Generate interview questions tailored to the candidate's resume,
    using the specified interviewer personality.
    """
    # Get resume text from the session
    sessions = execute_query(
        "SELECT resume_text FROM interview_sessions WHERE id = %s",
        (request.session_id,),
    )
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    resume_text = sessions[0].get("resume_text", "")
    if not resume_text or len(resume_text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="No resume text found for this session. Please upload a resume first.",
        )

    # Optionally analyse the resume for better question targeting
    analysis = analyse_resume(resume_text)

    # Generate questions
    questions = generate_questions(
        resume_text=resume_text,
        personality=request.personality,
        num_questions=request.num_questions,
        resume_analysis=analysis,
    )

    return {
        "success": True,
        "data": {
            "questions": questions,
            "personality": request.personality,
            "resume_skills": analysis.get("skills", []),
        },
    }


# ── 3. AI Evaluation ─────────────────────────────────────────────────

@router.post("/evaluate")
async def evaluate_interview(request: EvaluateRequest):
    """
    Evaluate all responses for a session using AI.
    Returns detailed scores, per-question feedback, and recommendations.
    """
    # Get session info
    sessions = execute_query(
        "SELECT resume_text, personality FROM interview_sessions WHERE id = %s",
        (request.session_id,),
    )
    if not sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[0]
    resume_text = session.get("resume_text", "") or ""
    personality = session.get("personality", "friendly")

    # Get all responses for this session (including delivery metadata)
    responses_rows = execute_query(
        "SELECT question, answer, input_mode, recording_duration FROM interview_responses WHERE session_id = %s ORDER BY question_index",
        (request.session_id,),
    )
    if not responses_rows:
        raise HTTPException(status_code=400, detail="No responses found for this session")

    responses = [
        {
            "question": r["question"],
            "answer": r["answer"],
            "input_mode": r.get("input_mode", "text") or "text",
            "recording_duration": float(r.get("recording_duration", 0) or 0),
        }
        for r in responses_rows
    ]

    # Run AI evaluation
    evaluation = evaluate_responses(
        resume_text=resume_text,
        personality=personality,
        responses=responses,
    )

    # Save the results to performance_results table
    import uuid
    result_id = str(uuid.uuid4())
    overall = evaluation.get("overall_score", 0)

    try:
        # Delete any existing results for this session (re-evaluation)
        execute_query(
            "DELETE FROM performance_results WHERE session_id = %s",
            (request.session_id,),
            fetch=False,
        )

        execute_query(
            """INSERT INTO performance_results
               (id, session_id, technical_accuracy, language_proficiency,
                confidence_level, sentiment_score, emotional_stability,
                overall_score, feedback)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                result_id,
                request.session_id,
                evaluation.get("technical_accuracy", 0),
                evaluation.get("language_proficiency", 0),
                evaluation.get("confidence_level", 0),
                evaluation.get("sentiment_score", 0),
                evaluation.get("emotional_stability", 0),
                overall,
                evaluation.get("summary_feedback", ""),
            ),
            fetch=False,
        )

        # Mark session as completed
        execute_query(
            "UPDATE interview_sessions SET status = 'completed', completed_at = NOW() WHERE id = %s",
            (request.session_id,),
            fetch=False,
        )
    except Exception as e:
        print(f"Warning: Failed to save AI evaluation results: {e}")

    return {
        "success": True,
        "data": evaluation,
    }


# ── 4. Server-side Speech-to-Text Transcription ──────────────────────

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
):
    """
    Receive a WAV audio file recorded in the browser,
    transcribe it using Google's free Web Speech API (server-side),
    and return the transcript text.

    This is the primary transcription path — the browser's
    SpeechRecognition API is used only as an optional live preview.
    """
    import speech_recognition as sr

    if not file.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    audio_bytes = await file.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file is too small / empty")
    if len(audio_bytes) > 20 * 1024 * 1024:  # 20 MB cap
        raise HTTPException(status_code=400, detail="Audio file too large (max 20 MB)")

    # Write to a temp file so speech_recognition can read it
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        recognizer = sr.Recognizer()
        # Increase energy threshold sensitivity for quieter mics
        recognizer.energy_threshold = 200
        recognizer.dynamic_energy_threshold = False

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)

        # Try Google free STT (no API key needed)
        transcript = recognizer.recognize_google(audio_data, language="en-US")
        return {
            "success": True,
            "data": {"transcript": transcript},
        }

    except sr.UnknownValueError:
        # Google could not understand the audio
        return {
            "success": True,
            "data": {"transcript": ""},
            "message": "Speech was not clear enough to transcribe.",
        }
    except sr.RequestError as e:
        print(f"Google STT API error: {e}")
        raise HTTPException(
            status_code=502,
            detail="Speech-to-text service is temporarily unavailable. Please try again.",
        )
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to transcribe audio: {str(e)}",
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
