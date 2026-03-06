from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from database import init_db
from routes.sessions import router as sessions_router
from routes.interviews import router as interviews_router
from routes.auth import router as auth_router
from routes.ai import router as ai_router
from routes.reports import router as reports_router

load_dotenv()

_ENV = os.getenv("ENVIRONMENT", "production")
_IS_DEV = _ENV == "development"

app = FastAPI(
    title="InterviewIQ API",
    description="Backend API for InterviewIQ — AI Interview Simulation Platform",
    version="1.0.0",
    # Disable interactive docs in production to avoid exposing the API surface
    docs_url="/docs" if _IS_DEV else None,
    redoc_url="/redoc" if _IS_DEV else None,
    openapi_url="/openapi.json" if _IS_DEV else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(interviews_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("""
╔═══════════════════════════════════════════════════╗
║                                                   ║
║   🚀 InterviewIQ Backend Server (Python)          ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
    """)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "InterviewIQ API is running"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    resp = {"message": "Welcome to InterviewIQ API", "health": "/api/health"}
    if _IS_DEV:
        resp["docs"] = "/docs"
    return resp

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=_IS_DEV)
