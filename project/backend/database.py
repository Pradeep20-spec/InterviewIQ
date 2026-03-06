import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "interviewiq"),
    "connection_timeout": 5,
}

# Create connection pool
connection_pool = None

def init_db():
    """Initialize database connection pool and ensure tables exist"""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="interviewiq_pool",
            pool_size=5,
            pool_reset_session=True,
            **db_config
        )
        print("✅ Database connection pool created successfully")
        _ensure_tables()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def _ensure_tables():
    """Create tables if they don't exist (idempotent)."""
    conn = connection_pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                name VARCHAR(255),
                password_hash VARCHAR(255) NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                resume_text TEXT,
                resume_filename VARCHAR(255),
                personality VARCHAR(50) NOT NULL,
                status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interview_responses (
                id VARCHAR(36) PRIMARY KEY,
                session_id VARCHAR(36) NOT NULL,
                question_index INT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                input_mode ENUM('text', 'audio', 'video') DEFAULT 'text',
                recording_duration INT DEFAULT 0,
                timestamp BIGINT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_results (
                id VARCHAR(36) PRIMARY KEY,
                session_id VARCHAR(36) NOT NULL UNIQUE,
                technical_accuracy DECIMAL(5,2),
                language_proficiency DECIMAL(5,2),
                confidence_level DECIMAL(5,2),
                sentiment_score DECIMAL(5,2),
                emotional_stability DECIMAL(5,2),
                overall_score DECIMAL(5,2),
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES interview_sessions(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions_bank (
                id VARCHAR(36) PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                personality VARCHAR(50) NOT NULL,
                question TEXT NOT NULL,
                difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"⚠️ Table creation warning: {e}")
    finally:
        cursor.close()
        conn.close()

def get_connection():
    """Get a connection from the pool"""
    if connection_pool is None:
        init_db()
    if connection_pool is None:
        raise RuntimeError("Database is unavailable — check DB_HOST, DB_USER, DB_PASSWORD, DB_NAME env vars")
    return connection_pool.get_connection()

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Execute a query and return results"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        return result
    finally:
        cursor.close()
        conn.close()

def execute_many(query: str, params_list: list):
    """Execute multiple queries in a transaction"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, params_list)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
