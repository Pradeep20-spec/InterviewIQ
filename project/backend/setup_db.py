"""Set up the InterviewIQ MySQL database and all tables."""
import mysql.connector
import uuid


def setup():
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="pradeep2006",
    )
    cur = conn.cursor()

    # Create database
    cur.execute("CREATE DATABASE IF NOT EXISTS interviewiq")
    cur.execute("USE interviewiq")
    print("Database 'interviewiq' ready")

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            name VARCHAR(255),
            password_hash VARCHAR(255) NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    print("  users table ready")

    # Interview sessions table
    cur.execute("""
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
    print("  interview_sessions table ready")

    # Interview responses table
    cur.execute("""
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
    print("  interview_responses table ready")

    # Performance results table
    cur.execute("""
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
    print("  performance_results table ready")

    # Questions bank table
    cur.execute("""
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
    print("  questions_bank table ready")

    conn.commit()

    # Ensure password_hash column exists (for existing installs)
    try:
        cur.execute("SELECT password_hash FROM users LIMIT 1")
        cur.fetchall()
    except mysql.connector.errors.ProgrammingError:
        cur.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''")
        conn.commit()
        print("  Added password_hash column to users")

    # Seed default questions if table is empty
    cur.execute("SELECT COUNT(*) FROM questions_bank")
    count = cur.fetchone()[0]
    if count == 0:
        questions = [
            ("general", "friendly", "Tell me about yourself and your background.", "easy"),
            ("general", "friendly", "What interests you most about this position?", "easy"),
            ("general", "friendly", "Can you describe a project you are particularly proud of?", "medium"),
            ("general", "friendly", "What are your greatest strengths?", "easy"),
            ("general", "friendly", "Where do you see yourself in five years?", "medium"),
            ("technical", "technical", "Explain the difference between let, const, and var in JavaScript.", "easy"),
            ("technical", "technical", "How would you optimize a slow database query?", "hard"),
            ("technical", "technical", "Describe the SOLID principles and give examples.", "hard"),
            ("technical", "technical", "What is the time complexity of your solution?", "medium"),
            ("technical", "technical", "Explain how garbage collection works in your preferred language.", "hard"),
            ("behavioral", "stress", "Why should we hire you over other candidates?", "hard"),
            ("behavioral", "stress", "Tell me about a time you failed. What happened?", "hard"),
            ("behavioral", "stress", "How do you handle tight deadlines with conflicting priorities?", "hard"),
            ("behavioral", "stress", "What is your biggest weakness?", "medium"),
            ("behavioral", "stress", "Convince me why this solution is better than the alternative.", "hard"),
            ("team", "panel", "How do you approach problem-solving in a team environment?", "medium"),
            ("team", "panel", "Describe your experience with agile methodologies.", "medium"),
            ("team", "panel", "What is your approach to code reviews?", "medium"),
            ("team", "panel", "How do you stay updated with new technologies?", "easy"),
            ("team", "panel", "Tell us about a time you had to make a difficult technical decision.", "hard"),
        ]
        for cat, pers, q, diff in questions:
            cur.execute(
                "INSERT INTO questions_bank (id, category, personality, question, difficulty) VALUES (%s, %s, %s, %s, %s)",
                (str(uuid.uuid4()), cat, pers, q, diff),
            )
        conn.commit()
        print(f"  Seeded {len(questions)} default questions")
    else:
        print(f"  Questions table already has {count} rows")

    # Create indexes (ignore if they already exist)
    indexes = [
        ("idx_sessions_user", "interview_sessions", "user_id"),
        ("idx_sessions_status", "interview_sessions", "status"),
        ("idx_responses_session", "interview_responses", "session_id"),
        ("idx_results_session", "performance_results", "session_id"),
        ("idx_questions_personality", "questions_bank", "personality"),
    ]
    for idx_name, table, col in indexes:
        try:
            cur.execute(f"CREATE INDEX {idx_name} ON {table}({col})")
        except mysql.connector.errors.ProgrammingError:
            pass  # Index already exists
    conn.commit()
    print("  Indexes ready")

    cur.close()
    conn.close()
    print("\nDatabase setup complete!")


if __name__ == "__main__":
    setup()
