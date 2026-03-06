from fastapi import APIRouter, HTTPException
import uuid
from database import execute_query, get_connection
from models import SaveResponseRequest, BatchResponsesRequest, SaveResultsRequest

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("/responses")
async def save_response(request: SaveResponseRequest):
    """Save a single interview response"""
    response_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO interview_responses 
        (id, session_id, question_index, question, answer, input_mode, recording_duration, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        execute_query(
            query,
            (response_id, request.session_id, request.question_index, request.question,
             request.answer, request.input_mode, request.recording_duration, request.timestamp),
            fetch=False
        )
        return {"success": True, "data": {"id": response_id, "session_id": request.session_id}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/responses/batch")
async def save_responses_batch(request: BatchResponsesRequest):
    """Save multiple responses at once"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        conn.start_transaction()
        
        query = """
            INSERT INTO interview_responses 
            (id, session_id, question_index, question, answer, input_mode, recording_duration, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for response in request.responses:
            response_id = str(uuid.uuid4())
            cursor.execute(query, (
                response_id, request.session_id, response.question_index,
                response.question, response.answer, response.input_mode,
                response.recording_duration, response.timestamp
            ))
        
        conn.commit()
        return {"success": True, "message": f"{len(request.responses)} responses saved"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.get("/responses/{session_id}")
async def get_responses(session_id: str):
    """Get responses for a session"""
    try:
        responses = execute_query(
            "SELECT * FROM interview_responses WHERE session_id = %s ORDER BY question_index",
            (session_id,)
        )
        return {"success": True, "data": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/results")
async def save_results(request: SaveResultsRequest):
    """Save performance results"""
    result_id = str(uuid.uuid4())
    overall_score = (
        request.technical_accuracy +
        request.language_proficiency +
        request.confidence_level +
        request.sentiment_score +
        request.emotional_stability
    ) / 5
    
    try:
        # Insert results
        execute_query(
            """
            INSERT INTO performance_results 
            (id, session_id, technical_accuracy, language_proficiency, confidence_level,
             sentiment_score, emotional_stability, overall_score, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (result_id, request.session_id, request.technical_accuracy, request.language_proficiency,
             request.confidence_level, request.sentiment_score, request.emotional_stability,
             overall_score, request.feedback),
            fetch=False
        )
        
        # Update session status
        execute_query(
            "UPDATE interview_sessions SET status = 'completed', completed_at = NOW() WHERE id = %s",
            (request.session_id,),
            fetch=False
        )
        
        return {"success": True, "data": {"id": result_id, "overall_score": overall_score}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{session_id}")
async def get_results(session_id: str):
    """Get performance results for a session"""
    try:
        results = execute_query(
            "SELECT * FROM performance_results WHERE session_id = %s",
            (session_id,)
        )
        if not results:
            raise HTTPException(status_code=404, detail="Results not found")
        return {"success": True, "data": results[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{personality}")
async def get_questions(personality: str):
    """Get questions by personality type"""
    try:
        questions = execute_query(
            "SELECT * FROM questions_bank WHERE personality = %s AND is_active = TRUE",
            (personality,)
        )
        return {"success": True, "data": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/overview")
async def get_stats():
    """Get interview statistics"""
    try:
        total = execute_query("SELECT COUNT(*) as count FROM interview_sessions")[0]["count"]
        completed = execute_query(
            "SELECT COUNT(*) as count FROM interview_sessions WHERE status = 'completed'"
        )[0]["count"]
        
        avg_result = execute_query("SELECT AVG(overall_score) as avg FROM performance_results")
        avg_score = avg_result[0]["avg"] or 0
        
        personality_stats = execute_query(
            "SELECT personality, COUNT(*) as count FROM interview_sessions GROUP BY personality"
        )
        
        return {
            "success": True,
            "data": {
                "total_sessions": total,
                "completed_sessions": completed,
                "average_score": round(avg_score, 2),
                "personality_distribution": personality_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
