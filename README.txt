================================================================================
  InterviewIQ — AI-Powered Interview Simulation Platform
  Version  : 1.0.0
  Author   : Pradeep J  (pradeepj2726@gmail.com)
  Date     : March 2026
================================================================================


────────────────────────────────────────────────────────────────────────────────
  TABLE OF CONTENTS
────────────────────────────────────────────────────────────────────────────────

  1.  Project Overview
  2.  Features
  3.  Tech Stack
  4.  Project Structure
  5.  Prerequisites
  6.  Installation & Setup
  7.  Environment Variables
  8.  Running the Application
  9.  API Endpoints
  10. Testing
  11. Production Build
  12. Email Report Setup (Gmail)
  13. Database Schema
  14. Known Limitations
  15. Troubleshooting


────────────────────────────────────────────────────────────────────────────────
  1. PROJECT OVERVIEW
────────────────────────────────────────────────────────────────────────────────

  InterviewIQ is a full-stack web application that simulates real job interviews
  using AI-powered Natural Language Processing (NLP). Candidates upload their
  resume, choose an interview personality, and are asked tailored questions.
  Their spoken or typed answers are analyzed in real-time and a detailed
  performance report is generated with per-question feedback, metric scores,
  and personalized recommendations.

  The platform supports:
    • Text-based answers typed into the browser
    • Audio answers recorded via the microphone (speech-to-text via backend STT)
    • Video answers recorded via webcam (delivery scoring + facial sentiment)

  Reports can be downloaded as a styled PDF or sent directly to the candidate's
  email address using Gmail SMTP.


────────────────────────────────────────────────────────────────────────────────
  2. FEATURES
────────────────────────────────────────────────────────────────────────────────

  Authentication
  ──────────────
    • Secure registration and login with bcrypt password hashing
    • JWT-based session tokens (24-hour expiry)
    • Rate-limited auth endpoints (10 requests / 60 seconds)
    • Persistent login via sessionStorage

  Resume Upload & Parsing
  ────────────────────────
    • Supports PDF and DOCX resume uploads (max 10 MB)
    • Extracts skills, experience, education, email, and career summary
    • Resume content is used to generate interview-relevant questions

  Interview Simulation
  ─────────────────────
    • 4 interview personalities:
        - Friendly HR          (easy, conversational)
        - Strict Technical     (hard, deep-dive questions)
        - Stress Interview     (pressure-testing)
        - Panel Interview      (multi-perspective questioning)
    • Configurable number of questions (default 5, up to 10)
    • Question bank with difficulty tags (easy / medium / hard)
    • Real-time answer input via text, audio (WAV), or video (WebM)

  AI Evaluation Engine
  ─────────────────────
    • Technical Accuracy    — keyword relevance, domain coverage
    • Language Proficiency  — vocabulary richness, grammar, fluency
    • Confidence Level      — assertive vs. hedging language patterns
    • Sentiment Score       — positive/neutral/negative tone analysis
    • Emotional Stability   — delivery consistency, filler word density
    • Speaking Pace         — words-per-minute analysis (audio/video)
    • Overall Score         — weighted composite of all dimensions

  Per-Question Feedback
  ──────────────────────
    • Score out of 100 per question
    • Specific strength highlight ("Great use of the STAR method")
    • Specific improvement tip ("Reduce filler words like 'um', 'uh'")
    • Placeholder detection for unanswered questions (score = 0)

  Performance Report
  ───────────────────
    • Color-coded dashboard with metric progress bars
    • Per-question breakdown with score badges
    • Numbered, interview-specific recommendations
    • AI-generated summary assessment paragraph
    • Download as multi-page styled PDF (jsPDF)
    • Send directly to any email address (Gmail SMTP)


────────────────────────────────────────────────────────────────────────────────
  3. TECH STACK
────────────────────────────────────────────────────────────────────────────────

  Frontend
  ─────────
    Framework    : React 18 + TypeScript
    Build Tool   : Vite 5
    Styling      : Tailwind CSS 3
    Icons        : Lucide React
    PDF Export   : jsPDF 4
    Linting      : ESLint 9 + TypeScript-ESLint

  Backend
  ────────
    Framework    : FastAPI (Python 3.11+)
    Server       : Uvicorn (ASGI)
    Auth         : bcrypt + PyJWT
    ORM/DB       : mysql-connector-python (raw SQL)
    Parsing      : PyPDF2, python-docx
    Speech-to-Text : SpeechRecognition (Google STT)
    Email        : smtplib (Gmail SMTP, TLS on port 587)
    Validation   : Pydantic v2

  Database
  ─────────
    Engine       : MySQL 8+
    Name         : interviewiq
    Tables       : users, interview_sessions, interview_responses,
                   performance_results, questions_bank

  DevOps / Tooling
  ─────────────────
    Version Ctrl : Git
    Env Secrets  : python-dotenv (.env files)
    Test Suite   : Custom Python test runner (112 checks)


────────────────────────────────────────────────────────────────────────────────
  4. PROJECT STRUCTURE
────────────────────────────────────────────────────────────────────────────────

  InterviewIQ/
  ├── start.ps1                    # One-click startup script (Windows)
  ├── README.txt                   # This file
  │
  └── project/
      ├── backend/                 # FastAPI application
      │   ├── main.py              # App entry point, CORS, router registration
      │   ├── database.py          # MySQL connection pool + execute_query helper
      │   ├── models.py            # Pydantic request/response models
      │   ├── schema.sql           # Database schema (CREATE TABLE statements)
      │   ├── setup_db.py          # One-time database initialisation script
      │   ├── run_tests.py         # Full test suite (112 checks)
      │   ├── requirements.txt     # Python package dependencies
      │   ├── .env                 # Secrets: DB, JWT, SMTP (never commit!)
      │   │
      │   ├── routes/
      │   │   ├── auth.py          # POST /api/auth/register, /login, /me
      │   │   ├── sessions.py      # POST/GET /api/sessions
      │   │   ├── interviews.py    # GET /api/interviews/questions
      │   │   ├── ai.py            # POST /api/ai/evaluate, /transcribe
      │   │   └── reports.py       # POST /api/reports/generate, /email
      │   │
      │   └── services/
      │       ├── ai_engine.py     # Core evaluation pipeline (orchestrator)
      │       ├── nlp_utils.py     # Scoring algorithms, feedback generator
      │       ├── question_bank.py # Question selection + personalisation
      │       ├── resume_parser.py # PDF/DOCX skill + experience extraction
      │       └── video_analyser.py# Audio/video delivery scoring
      │
      └── frontend/                # React + Vite application
          ├── index.html           # HTML entry point
          ├── package.json         # npm dependencies and scripts
          ├── vite.config.ts       # Build config, chunk splitting, dev proxy
          ├── tailwind.config.js   # Design token config
          ├── tsconfig.json        # TypeScript project config
          ├── .env                 # VITE_API_URL (never commit!)
          │
          ├── src/
          │   ├── main.tsx         # React DOM entry point
          │   ├── App.tsx          # Root component + client-side routing
          │   ├── index.css        # Global styles + Tailwind directives
          │   │
          │   ├── components/
          │   │   ├── LandingPage.tsx          # Homepage + hero section
          │   │   ├── AuthPage.tsx             # Login / Register forms
          │   │   ├── ResumeUpload.tsx         # Drag-and-drop resume uploader
          │   │   ├── PersonalitySelection.tsx # Interview type chooser
          │   │   ├── InterviewSimulation.tsx  # Live interview + recording UI
          │   │   └── PerformanceResults.tsx   # Results dashboard + PDF/email
          │   │
          │   ├── context/
          │   │   └── AuthContext.tsx           # Global auth state (JWT)
          │   │
          │   └── services/
          │       └── api.ts                   # Typed API client (axios-free)
          │
          └── public/              # Static assets served as-is


────────────────────────────────────────────────────────────────────────────────
  5. PREREQUISITES
────────────────────────────────────────────────────────────────────────────────

  Software required before running the project:

  ┌─────────────────────┬───────────────┬──────────────────────────────────────┐
  │ Software            │ Min Version   │ Notes                                │
  ├─────────────────────┼───────────────┼──────────────────────────────────────┤
  │ Python              │ 3.11          │ python.org/downloads                 │
  │ Node.js             │ 18 LTS        │ nodejs.org                           │
  │ npm                 │ 9+            │ Bundled with Node.js                 │
  │ MySQL               │ 8.0           │ dev.mysql.com or xampp               │
  │ Git                 │ 2.x           │ git-scm.com                          │
  └─────────────────────┴───────────────┴──────────────────────────────────────┘

  For audio/video speech-to-text:
    • An active internet connection (Google STT API is used for transcription)
    • A working microphone / webcam


────────────────────────────────────────────────────────────────────────────────
  6. INSTALLATION & SETUP
────────────────────────────────────────────────────────────────────────────────

  Step 1 — Clone / extract the project
  ─────────────────────────────────────
    The project folder should be at:
      C:\Users\<you>\Downloads\InterviewIQ\

  Step 2 — Create the MySQL database
  ─────────────────────────────────────
    Open MySQL Workbench or the mysql CLI:

      CREATE DATABASE interviewiq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

    Then run the schema:
      mysql -u root -p interviewiq < project\backend\schema.sql

    Optionally seed default questions:
      cd project\backend
      python setup_db.py

  Step 3 — Set up the Python virtual environment
  ──────────────────────────────────────────────
    From the InterviewIQ root folder:

      python -m venv .venv-1
      .venv-1\Scripts\Activate.ps1        # PowerShell
      pip install -r project\backend\requirements.txt

  Step 4 — Configure backend environment variables
  ──────────────────────────────────────────────────
    Edit  project\backend\.env  (see Section 7 for all variables).
    At minimum, set:
      DB_USER, DB_PASSWORD, JWT_SECRET

  Step 5 — Install frontend dependencies
  ────────────────────────────────────────
    cd project\frontend
    npm install

  Step 6 — Configure frontend environment variable
  ──────────────────────────────────────────────────
    project\frontend\.env  should contain:
      VITE_API_URL=http://localhost:3001/api

    (This is already set if you are running locally.)


────────────────────────────────────────────────────────────────────────────────
  7. ENVIRONMENT VARIABLES
────────────────────────────────────────────────────────────────────────────────

  Backend  →  project\backend\.env
  ─────────────────────────────────

    # Database
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=root                         # Use a restricted user in production
    DB_PASSWORD=your_db_password
    DB_NAME=interviewiq

    # Server
    PORT=3001
    FRONTEND_URL=http://localhost:5173   # Change to your domain in production

    # Environment: 'development' enables /docs UI; 'production' hides it
    ENVIRONMENT=development

    # JWT — generate a secure random string, keep SECRET
    JWT_SECRET=<64-char random hex string>

    # Email (Gmail SMTP)
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=your@gmail.com
    SMTP_PASS=your_16_char_app_password  # NOT your Gmail login password!
    SMTP_FROM=your@gmail.com
    SMTP_FROM_NAME=InterviewIQ

  Frontend  →  project\frontend\.env
  ────────────────────────────────────

    VITE_API_URL=http://localhost:3001/api

  IMPORTANT: Both .env files are listed in .gitignore and must NEVER be
  committed to version control. They contain secrets.


────────────────────────────────────────────────────────────────────────────────
  8. RUNNING THE APPLICATION
────────────────────────────────────────────────────────────────────────────────

  Option A — One-click (recommended)
  ────────────────────────────────────
    From the InterviewIQ root folder, right-click start.ps1 and choose
    "Run with PowerShell", or from a terminal:

      .\start.ps1

    This opens two separate PowerShell windows:
      • Backend  → http://localhost:3001
      • Frontend → http://localhost:5173

  Option B — Manual (two separate terminals)
  ───────────────────────────────────────────
    Terminal 1 — Backend:
      cd project\backend
      ..\..\.venv-1\Scripts\Activate.ps1
      uvicorn main:app --host 0.0.0.0 --port 3001 --reload

    Terminal 2 — Frontend:
      cd project\frontend
      npm run dev

  Accessing the app
  ──────────────────
    Browser   →  http://localhost:5173
    API Docs  →  http://localhost:3001/docs   (development mode only)

  Stopping
  ─────────
    Press Ctrl+C in each terminal, or close the windows opened by start.ps1.


────────────────────────────────────────────────────────────────────────────────
  9. API ENDPOINTS
────────────────────────────────────────────────────────────────────────────────

  All routes are prefixed with /api

  Authentication
  ───────────────
    POST  /api/auth/register         Register a new user
    POST  /api/auth/login            Login, returns JWT token
    GET   /api/auth/me               Get current user profile (requires JWT)

  Interview Sessions
  ───────────────────
    POST  /api/sessions              Create a new interview session
    GET   /api/sessions              List all sessions for the logged-in user
    GET   /api/sessions/{id}         Get a single session with responses
    PATCH /api/sessions/{id}         Update session status

  Interview Questions
  ────────────────────
    GET   /api/interviews/questions  Get tailored questions for a session

  AI Evaluation
  ──────────────
    POST  /api/ai/evaluate           Evaluate all responses for a session
    POST  /api/ai/transcribe         Convert audio blob → text (STT)

  Reports
  ────────
    POST  /api/reports/generate      Generate a plain-text report
    POST  /api/reports/email         Send the report to a given email address

  Health
  ───────
    GET   /                          Returns {"status": "ok", "service": "InterviewIQ API"}


────────────────────────────────────────────────────────────────────────────────
  10. TESTING
────────────────────────────────────────────────────────────────────────────────

  The backend ships with a comprehensive test suite covering all critical paths.

  Run tests:
    cd project\backend
    python run_tests.py

  Test coverage (112 checks):
    1.  Python import checks          (11 checks)
    2.  Database connectivity         (7 checks)
    3.  Authentication module         (11 checks)
    4.  Resume parsing                (8 checks)
    5.  NLP utilities                 (9 checks)
    6.  Skill extraction              (4 checks)
    7.  AI question generation        (9 checks)
    8.  Text answer scoring           (11 checks)
    9.  Video / audio delivery scoring(12 checks)
    10. Full evaluation pipeline      (13 checks)
    11. Database storage              (8 checks)
    12. Edge cases & robustness       (9 checks)
    13. Cleanup test data             (1 check)

  Expected output:
    Total checks : 112
    Passed       : 112
    Failed       : 0
    ✅ ALL CRITICAL TESTS PASSED (100%) — System is ready!

  Frontend TypeScript check:
    cd project\frontend
    npx tsc --noEmit


────────────────────────────────────────────────────────────────────────────────
  11. PRODUCTION BUILD
────────────────────────────────────────────────────────────────────────────────

  Build the frontend for production:
    cd project\frontend
    npm run build

  Output is placed in  project\frontend\dist\
  Serve the dist\ folder with any static web server (Nginx, Apache, Netlify, etc.)

  Production build chunks:
    dist/assets/index.js           ~18.9 kB gzip   (app code)
    dist/assets/vendor-react.js    ~45.3 kB gzip   (React + ReactDOM)
    dist/assets/vendor-pdf.js      ~184.6 kB gzip  (jsPDF + html2canvas)
    dist/assets/vendor-icons.js    ~3.4 kB gzip    (Lucide icons)

  For production deployment:
    1. Set  ENVIRONMENT=production  in backend/.env
       → Disables /docs and /redoc API explorer
    2. Set  FRONTEND_URL=https://your-domain.com  in backend/.env
       → Restricts CORS to your production domain only
    3. Set  VITE_API_URL=https://your-api-domain.com/api  in frontend/.env
       → Points the frontend to the production API
    4. Run the backend with:
         uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4
    5. Put Nginx or a reverse proxy in front of both servers


────────────────────────────────────────────────────────────────────────────────
  12. EMAIL REPORT SETUP (GMAIL)
────────────────────────────────────────────────────────────────────────────────

  InterviewIQ uses Gmail's SMTP service to send performance reports.
  A regular Gmail password will NOT work — you must use an App Password.

  Steps to generate an App Password:
  ────────────────────────────────────
    1. Sign in to your Google Account at  https://myaccount.google.com
    2. Go to  Security  →  2-Step Verification
       (Enable it if not already on — required for App Passwords)
    3. Scroll down and click  App Passwords
    4. Under "Select app", choose  Mail
    5. Under "Select device", choose  Other  and type  InterviewIQ
    6. Click  Generate
    7. Copy the 16-character password shown (spaces are optional)
    8. Paste it into  SMTP_PASS  in  project\backend\.env

  Example:
    SMTP_PASS=fsyf iwlj tili xwmi

  When SMTP_PASS is not set or still contains the placeholder text, the app
  gracefully falls back to offering a local PDF download instead.

  The email includes:
    • Overall score with color rating
    • Interview type, question count, and date
    • Colored progress bars for all 5 performance metrics
    • Per-question feedback (score badge, strength, improvement)
    • Numbered AI recommendations list
    • Summary assessment paragraph
    • Plain-text report attached as a .txt file


────────────────────────────────────────────────────────────────────────────────
  13. DATABASE SCHEMA
────────────────────────────────────────────────────────────────────────────────

  Table: users
  ─────────────
    id            VARCHAR(36)  PRIMARY KEY  (UUID)
    name          VARCHAR(100) NOT NULL
    email         VARCHAR(255) UNIQUE NOT NULL
    password_hash VARCHAR(255) NOT NULL
    created_at    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP

  Table: interview_sessions
  ──────────────────────────
    id            VARCHAR(36)  PRIMARY KEY  (UUID)
    user_id       VARCHAR(36)  FK → users.id
    personality   VARCHAR(50)  (friendly / technical / stress / panel)
    resume_text   TEXT
    status        VARCHAR(20)  (active / completed)
    created_at    TIMESTAMP
    completed_at  TIMESTAMP    NULL

  Table: interview_responses
  ───────────────────────────
    id                VARCHAR(36)   PRIMARY KEY  (UUID)
    session_id        VARCHAR(36)   FK → interview_sessions.id
    question_index    INT
    question          TEXT
    answer            TEXT
    input_mode        VARCHAR(20)   (text / audio / video)
    recording_duration FLOAT        NULL
    created_at        TIMESTAMP

  Table: performance_results
  ───────────────────────────
    id                  VARCHAR(36) PRIMARY KEY  (UUID)
    session_id          VARCHAR(36) FK → interview_sessions.id (UNIQUE)
    overall_score       FLOAT
    technical_accuracy  FLOAT
    language_proficiency FLOAT
    confidence_level    FLOAT
    sentiment_score     FLOAT
    emotional_stability FLOAT
    feedback            TEXT
    created_at          TIMESTAMP

  Table: questions_bank
  ──────────────────────
    id          VARCHAR(36)  PRIMARY KEY
    category    VARCHAR(50)
    difficulty  VARCHAR(20)  (easy / medium / hard)
    question    TEXT
    keywords    TEXT         (comma-separated)


────────────────────────────────────────────────────────────────────────────────
  14. KNOWN LIMITATIONS
────────────────────────────────────────────────────────────────────────────────

  • Speech-to-text requires an active internet connection (uses Google STT).
    If offline, audio answers are recorded but not transcribed — the answer
    is saved as a placeholder and scores 0 for all dimensions.

  • The NLP evaluation engine is custom-built (no LLM/GPT calls).
    It uses keyword matching, sentiment lexicons, and heuristic scoring.
    Results are indicative, not a guaranteed measure of professional ability.

  • Video facial sentiment detection is delivery-based (speaking pace, filler
    words, utilisation ratio). It does not use computer vision or facial
    recognition.

  • Gmail SMTP requires 2-Step Verification to be enabled to generate an
    App Password. Free Gmail accounts have a daily send limit of 500 emails.

  • The application is designed for single-user local development. For
    multi-user production deployment, use a connection pool, a managed
    database, and a production WSGI server (Gunicorn + Uvicorn workers).


────────────────────────────────────────────────────────────────────────────────
  15. TROUBLESHOOTING
────────────────────────────────────────────────────────────────────────────────

  Problem:  "MySQL connection refused"
  Solution: Make sure MySQL is running. Check DB_HOST, DB_PORT, DB_USER,
            DB_PASSWORD in backend/.env. Verify the database exists:
              mysql -u root -p -e "SHOW DATABASES;"

  Problem:  "No module named 'fastapi'"
  Solution: Activate the virtual environment first:
              .venv-1\Scripts\Activate.ps1
            Then reinstall:
              pip install -r project\backend\requirements.txt

  Problem:  "CORS policy" error in browser
  Solution: Make sure FRONTEND_URL in backend/.env exactly matches the
            URL shown in your browser (http://localhost:5173, no trailing slash).

  Problem:  Email not sending / "App Password" error
  Solution: See Section 12. Use an App Password, not your regular Gmail
            password. Also ensure 2-Step Verification is enabled on your
            Google account.

  Problem:  "Speech recognition could not understand audio"
  Solution: Check microphone permissions in your browser settings. Ensure
            the backend server is reachable at localhost:3001. Check that
            SpeechRecognition is installed: pip install SpeechRecognition

  Problem:  Port 3001 already in use
  Solution: Kill the process using port 3001:
              netstat -ano | findstr :3001
              taskkill /PID <PID> /F
            Or change PORT in backend/.env and update VITE_API_URL accordingly.

  Problem:  Frontend shows blank page after npm run dev
  Solution: Check that the backend is running on port 3001. Open the browser
            console for errors. Verify VITE_API_URL in frontend/.env.

  Problem:  "VITE_API_URL is not defined"
  Solution: Ensure frontend/.env exists and contains:
              VITE_API_URL=http://localhost:3001/api
            Restart the Vite dev server after editing .env.


────────────────────────────────────────────────────────────────────────────────
  END OF README
  InterviewIQ v1.0.0  |  Built with FastAPI + React + MySQL
================================================================================
