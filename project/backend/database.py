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
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="interviewiq_pool",
            pool_size=5,
            pool_reset_session=True,
            **db_config
        )
        print("✅ Database connection pool created successfully")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

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
