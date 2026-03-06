from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
from database import execute_query
from models import CreateSessionRequest, UpdateStatusRequest

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/")
async def create_session(request: CreateSessionRequest):
    """Create a new interview session"""
    session_id = str(uuid.uuid4())
    
    query = """
        INSERT INTO interview_sessions (id, user_id, resume_text, resume_filename, personality, status)
        VALUES (%s, %s, %s, %s, %s, 'in_progress')
    """
    
    try:
        execute_query(
            query,
            (session_id, request.user_id, request.resume_text, request.resume_filename, request.personality),
            fetch=False
        )
        return {
            "success": True,
            "data": {"id": session_id, "personality": request.personality, "status": "in_progress"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session by ID"""
    query = "SELECT * FROM interview_sessions WHERE id = %s"
    
    try:
        result = execute_query(query, (session_id,))
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "data": result[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_all_sessions(page: int = 1, limit: int = 10):
    """Get all sessions with pagination"""
    offset = (page - 1) * limit
    
    try:
        sessions = execute_query(
            "SELECT * FROM interview_sessions ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (limit, offset)
        )
        
        count_result = execute_query("SELECT COUNT(*) as total FROM interview_sessions")
        total = count_result[0]["total"]
        
        return {
            "success": True,
            "data": sessions,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": (total + limit - 1) // limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{session_id}/status")
async def update_session_status(session_id: str, request: UpdateStatusRequest):
    """Update session status"""
    completed_at = "NOW()" if request.status == "completed" else "NULL"
    
    query = f"""
        UPDATE interview_sessions 
        SET status = %s, completed_at = {completed_at}
        WHERE id = %s
    """
    
    try:
        execute_query(query, (request.status, session_id), fetch=False)
        return {"success": True, "message": "Session status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        execute_query("DELETE FROM interview_sessions WHERE id = %s", (session_id,), fetch=False)
        return {"success": True, "message": "Session deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}/full")
async def get_full_session(session_id: str):
    """Get session with all responses and results"""
    try:
        session = execute_query("SELECT * FROM interview_sessions WHERE id = %s", (session_id,))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        responses = execute_query(
            "SELECT * FROM interview_responses WHERE session_id = %s ORDER BY question_index",
            (session_id,)
        )
        
        results = execute_query(
            "SELECT * FROM performance_results WHERE session_id = %s",
            (session_id,)
        )
        
        return {
            "success": True,
            "data": {
                "session": session[0],
                "responses": responses,
                "results": results[0] if results else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
