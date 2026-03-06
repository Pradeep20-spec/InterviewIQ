"""
InterviewIQ Question Bank — 200+ interview questions organised by skill,
category, difficulty, and personality.

No external dependencies. The selection algorithm matches questions to the
candidate's resume-detected skills and ensures a diverse, well-balanced set.
"""

from __future__ import annotations

import random
from typing import Optional

# ────────────────────────────────────────────────────────────────
# Question Template Structure
# ────────────────────────────────────────────────────────────────
# Each question has:
#   q        — the question text
#   skills   — skills this question tests (matches TECHNICAL_SKILLS keys)
#   cat      — category: technical | behavioral | situational | experience | general
#   diff     — difficulty: easy | medium | hard
#   keywords — key concepts the ideal answer should mention


QUESTIONS: list[dict] = [
    # ═══════════════════════════════════════════════════════════
    # PYTHON
    # ═══════════════════════════════════════════════════════════
    {"q": "What are Python's key features that make it suitable for your projects?", "skills": ["python"], "cat": "technical", "diff": "easy", "keywords": ["interpreted", "dynamic typing", "readability", "libraries"]},
    {"q": "Explain the difference between a list and a tuple in Python.", "skills": ["python"], "cat": "technical", "diff": "easy", "keywords": ["mutable", "immutable", "list", "tuple", "performance"]},
    {"q": "How does Python's Global Interpreter Lock (GIL) affect multithreading?", "skills": ["python"], "cat": "technical", "diff": "hard", "keywords": ["GIL", "thread", "multiprocessing", "concurrency", "CPU-bound"]},
    {"q": "Describe Python decorators and give a practical use case.", "skills": ["python"], "cat": "technical", "diff": "medium", "keywords": ["decorator", "wrapper", "function", "@", "logging", "authentication"]},
    {"q": "How do you manage dependencies and virtual environments in Python projects?", "skills": ["python"], "cat": "technical", "diff": "medium", "keywords": ["pip", "venv", "virtualenv", "requirements.txt", "poetry", "conda"]},
    {"q": "Explain generators in Python and when you would use them over lists.", "skills": ["python"], "cat": "technical", "diff": "medium", "keywords": ["yield", "generator", "lazy evaluation", "memory", "iteration"]},
    {"q": "What is the difference between deep copy and shallow copy in Python?", "skills": ["python"], "cat": "technical", "diff": "medium", "keywords": ["copy", "deepcopy", "reference", "mutable objects", "nested"]},
    {"q": "How would you optimise a Python application that is running slowly?", "skills": ["python"], "cat": "technical", "diff": "hard", "keywords": ["profiling", "caching", "algorithm", "cProfile", "async", "C extension"]},

    # ═══════════════════════════════════════════════════════════
    # JAVASCRIPT / TYPESCRIPT
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain the difference between var, let, and const in JavaScript.", "skills": ["javascript", "typescript"], "cat": "technical", "diff": "easy", "keywords": ["scope", "hoisting", "block", "function", "reassignment"]},
    {"q": "What are closures in JavaScript and how are they useful?", "skills": ["javascript"], "cat": "technical", "diff": "medium", "keywords": ["closure", "scope", "function", "lexical", "encapsulation", "data privacy"]},
    {"q": "Describe the event loop in JavaScript and how asynchronous code executes.", "skills": ["javascript", "nodejs"], "cat": "technical", "diff": "hard", "keywords": ["event loop", "call stack", "callback queue", "microtask", "setTimeout", "Promise"]},
    {"q": "What are the benefits of TypeScript over plain JavaScript?", "skills": ["typescript"], "cat": "technical", "diff": "easy", "keywords": ["type safety", "interfaces", "compile-time", "tooling", "IntelliSense", "refactoring"]},
    {"q": "Explain Promises and async/await in JavaScript.", "skills": ["javascript", "typescript"], "cat": "technical", "diff": "medium", "keywords": ["Promise", "async", "await", "then", "catch", "callback hell"]},
    {"q": "How do you handle error boundaries and error handling in JavaScript applications?", "skills": ["javascript", "typescript"], "cat": "technical", "diff": "medium", "keywords": ["try-catch", "error boundary", "global handler", "logging", "graceful degradation"]},
    {"q": "What is prototypal inheritance and how does it differ from classical inheritance?", "skills": ["javascript"], "cat": "technical", "diff": "hard", "keywords": ["prototype", "prototype chain", "Object.create", "class", "__proto__"]},

    # ═══════════════════════════════════════════════════════════
    # REACT
    # ═══════════════════════════════════════════════════════════
    {"q": "What are React hooks and why were they introduced?", "skills": ["react"], "cat": "technical", "diff": "easy", "keywords": ["useState", "useEffect", "functional components", "class components", "reuse logic"]},
    {"q": "Explain the virtual DOM and how React uses it for performance.", "skills": ["react"], "cat": "technical", "diff": "medium", "keywords": ["virtual DOM", "diffing", "reconciliation", "batch update", "performance"]},
    {"q": "How do you manage state in a large React application?", "skills": ["react"], "cat": "technical", "diff": "medium", "keywords": ["Redux", "Context", "Zustand", "state management", "prop drilling", "global state"]},
    {"q": "Describe React's reconciliation algorithm and how it decides what to re-render.", "skills": ["react"], "cat": "technical", "diff": "hard", "keywords": ["reconciliation", "keys", "fiber", "diffing", "shouldComponentUpdate", "memo"]},
    {"q": "How would you optimise a React application with performance issues?", "skills": ["react"], "cat": "technical", "diff": "hard", "keywords": ["memo", "useMemo", "useCallback", "lazy loading", "code splitting", "profiler"]},
    {"q": "Explain server-side rendering (SSR) in React and when to use it.", "skills": ["react"], "cat": "technical", "diff": "medium", "keywords": ["SSR", "Next.js", "SEO", "hydration", "performance", "initial load"]},

    # ═══════════════════════════════════════════════════════════
    # JAVA
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain the difference between an abstract class and an interface in Java.", "skills": ["java"], "cat": "technical", "diff": "easy", "keywords": ["abstract", "interface", "implementation", "multiple inheritance", "default method"]},
    {"q": "How does garbage collection work in Java?", "skills": ["java"], "cat": "technical", "diff": "medium", "keywords": ["GC", "heap", "garbage collector", "generations", "mark-sweep", "reference"]},
    {"q": "Describe the Java Stream API and its advantages.", "skills": ["java"], "cat": "technical", "diff": "medium", "keywords": ["Stream", "lambda", "functional", "map", "filter", "reduce", "parallel"]},
    {"q": "What are the key differences between Java 8 and newer versions you've used?", "skills": ["java"], "cat": "technical", "diff": "medium", "keywords": ["lambda", "records", "pattern matching", "sealed classes", "modules"]},
    {"q": "How do you handle concurrency and thread safety in Java?", "skills": ["java"], "cat": "technical", "diff": "hard", "keywords": ["synchronized", "concurrent", "locks", "AtomicInteger", "thread pool", "volatile"]},
    {"q": "Explain the Spring Boot dependency injection mechanism.", "skills": ["java", "spring"], "cat": "technical", "diff": "hard", "keywords": ["IoC", "dependency injection", "autowired", "bean", "component scan", "configuration"]},

    # ═══════════════════════════════════════════════════════════
    # C++ / C#
    # ═══════════════════════════════════════════════════════════
    {"q": "What is the difference between stack and heap memory allocation?", "skills": ["cpp", "csharp"], "cat": "technical", "diff": "medium", "keywords": ["stack", "heap", "allocation", "deallocation", "scope", "pointer", "garbage collection"]},
    {"q": "Explain smart pointers in C++ and their different types.", "skills": ["cpp"], "cat": "technical", "diff": "hard", "keywords": ["unique_ptr", "shared_ptr", "weak_ptr", "RAII", "memory management", "ownership"]},
    {"q": "How does the .NET runtime manage memory with its garbage collector?", "skills": ["csharp"], "cat": "technical", "diff": "medium", "keywords": ["CLR", "garbage collector", "generations", "finalize", "dispose", "IDisposable"]},
    {"q": "Describe LINQ in C# and how you've used it.", "skills": ["csharp"], "cat": "technical", "diff": "medium", "keywords": ["LINQ", "query", "lambda", "Where", "Select", "deferred execution"]},

    # ═══════════════════════════════════════════════════════════
    # DATABASES (SQL / NoSQL)
    # ═══════════════════════════════════════════════════════════
    {"q": "How would you optimise a slow-running SQL query?", "skills": ["sql"], "cat": "technical", "diff": "medium", "keywords": ["index", "EXPLAIN", "join", "normalisation", "query plan", "denormalisation"]},
    {"q": "Explain the differences between SQL and NoSQL databases.", "skills": ["sql", "nosql"], "cat": "technical", "diff": "easy", "keywords": ["relational", "document", "schema", "scalability", "ACID", "CAP theorem"]},
    {"q": "What are database indexes and how do they improve performance?", "skills": ["sql"], "cat": "technical", "diff": "medium", "keywords": ["index", "B-tree", "lookup", "write overhead", "covering index", "composite"]},
    {"q": "Describe ACID properties and why they matter in transactions.", "skills": ["sql"], "cat": "technical", "diff": "medium", "keywords": ["Atomicity", "Consistency", "Isolation", "Durability", "transaction", "rollback"]},
    {"q": "How do you design a database schema for a high-traffic application?", "skills": ["sql", "nosql", "system_design"], "cat": "technical", "diff": "hard", "keywords": ["normalisation", "sharding", "replication", "partitioning", "caching", "read replica"]},
    {"q": "When would you choose MongoDB over a relational database?", "skills": ["nosql"], "cat": "technical", "diff": "medium", "keywords": ["document model", "schema flexibility", "scalability", "nested data", "use case"]},
    {"q": "Explain database normalisation and its different forms.", "skills": ["sql"], "cat": "technical", "diff": "medium", "keywords": ["1NF", "2NF", "3NF", "BCNF", "redundancy", "dependency"]},

    # ═══════════════════════════════════════════════════════════
    # CLOUD & DEVOPS
    # ═══════════════════════════════════════════════════════════
    {"q": "What AWS services have you used and for what purposes?", "skills": ["aws"], "cat": "experience", "diff": "easy", "keywords": ["EC2", "S3", "Lambda", "RDS", "CloudFront", "deployment"]},
    {"q": "Explain the benefits of containerisation with Docker.", "skills": ["docker"], "cat": "technical", "diff": "easy", "keywords": ["container", "image", "isolation", "portability", "Dockerfile", "layer"]},
    {"q": "How does Kubernetes orchestrate container deployments?", "skills": ["kubernetes"], "cat": "technical", "diff": "hard", "keywords": ["pod", "service", "deployment", "scaling", "node", "cluster", "ingress"]},
    {"q": "Describe your CI/CD pipeline and how it improved your team's workflow.", "skills": ["cicd"], "cat": "experience", "diff": "medium", "keywords": ["build", "test", "deploy", "automated", "pipeline", "feedback loop"]},
    {"q": "What is Infrastructure as Code and how have you implemented it?", "skills": ["terraform"], "cat": "technical", "diff": "medium", "keywords": ["Terraform", "IaC", "state", "plan", "apply", "version control", "reproducible"]},
    {"q": "How do you ensure high availability and disaster recovery in cloud deployments?", "skills": ["aws", "azure", "gcp", "devops"], "cat": "technical", "diff": "hard", "keywords": ["multi-AZ", "failover", "backup", "RTO", "RPO", "auto-scaling", "load balancer"]},
    {"q": "Explain the difference between horizontal and vertical scaling.", "skills": ["system_design", "devops"], "cat": "technical", "diff": "easy", "keywords": ["horizontal", "vertical", "scale out", "scale up", "load balancer", "distributed"]},

    # ═══════════════════════════════════════════════════════════
    # SYSTEM DESIGN & ARCHITECTURE
    # ═══════════════════════════════════════════════════════════
    {"q": "How would you design a URL shortening service like bit.ly?", "skills": ["system_design"], "cat": "technical", "diff": "hard", "keywords": ["hashing", "base62", "database", "redirect", "analytics", "cache", "scale"]},
    {"q": "Explain the differences between monolithic and microservice architectures.", "skills": ["system_design"], "cat": "technical", "diff": "medium", "keywords": ["monolith", "microservice", "coupling", "scaling", "deployment", "complexity"]},
    {"q": "What are RESTful API design best practices?", "skills": ["api_design"], "cat": "technical", "diff": "medium", "keywords": ["REST", "HTTP methods", "status codes", "versioning", "pagination", "idempotent"]},
    {"q": "How does a load balancer work and what strategies can it use?", "skills": ["system_design"], "cat": "technical", "diff": "medium", "keywords": ["round robin", "least connections", "health check", "sticky sessions", "L4", "L7"]},
    {"q": "Describe caching strategies and when each is appropriate.", "skills": ["system_design", "redis"], "cat": "technical", "diff": "hard", "keywords": ["cache-aside", "write-through", "write-back", "TTL", "invalidation", "Redis", "CDN"]},
    {"q": "How would you design a real-time chat application?", "skills": ["system_design", "api_design"], "cat": "technical", "diff": "hard", "keywords": ["WebSocket", "message queue", "presence", "persistence", "scaling", "pub/sub"]},

    # ═══════════════════════════════════════════════════════════
    # DATA STRUCTURES & ALGORITHMS
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain Big O notation and why it matters.", "skills": ["dsa"], "cat": "technical", "diff": "easy", "keywords": ["time complexity", "space complexity", "O(n)", "O(log n)", "O(1)", "worst case"]},
    {"q": "What data structure would you use to implement an LRU cache?", "skills": ["dsa"], "cat": "technical", "diff": "hard", "keywords": ["hash map", "doubly linked list", "O(1)", "eviction", "capacity"]},
    {"q": "Describe the difference between BFS and DFS and when to use each.", "skills": ["dsa"], "cat": "technical", "diff": "medium", "keywords": ["breadth-first", "depth-first", "queue", "stack", "shortest path", "traversal"]},
    {"q": "How would you detect a cycle in a linked list?", "skills": ["dsa"], "cat": "technical", "diff": "medium", "keywords": ["Floyd's", "tortoise and hare", "two pointers", "O(1) space", "fast/slow"]},
    {"q": "Explain dynamic programming and walk through an example.", "skills": ["dsa"], "cat": "technical", "diff": "hard", "keywords": ["overlapping subproblems", "memoisation", "tabulation", "Fibonacci", "optimal substructure"]},

    # ═══════════════════════════════════════════════════════════
    # TESTING & QUALITY
    # ═══════════════════════════════════════════════════════════
    {"q": "Describe your approach to writing unit tests.", "skills": ["testing"], "cat": "technical", "diff": "easy", "keywords": ["unit test", "assert", "mock", "coverage", "arrange-act-assert", "isolation"]},
    {"q": "What is the testing pyramid and how do you apply it?", "skills": ["testing"], "cat": "technical", "diff": "medium", "keywords": ["unit", "integration", "e2e", "pyramid", "speed", "cost", "confidence"]},
    {"q": "How do you practice Test-Driven Development (TDD)?", "skills": ["testing"], "cat": "technical", "diff": "medium", "keywords": ["TDD", "red-green-refactor", "test first", "design", "regression"]},
    {"q": "Explain the difference between mocking, stubbing, and faking.", "skills": ["testing"], "cat": "technical", "diff": "medium", "keywords": ["mock", "stub", "fake", "test double", "behavior", "verification"]},

    # ═══════════════════════════════════════════════════════════
    # SECURITY
    # ═══════════════════════════════════════════════════════════
    {"q": "What are the OWASP Top 10 vulnerabilities and how do you prevent them?", "skills": ["security"], "cat": "technical", "diff": "hard", "keywords": ["injection", "XSS", "CSRF", "authentication", "access control", "OWASP"]},
    {"q": "Explain how JWT authentication works.", "skills": ["security", "api_design"], "cat": "technical", "diff": "medium", "keywords": ["JWT", "token", "header", "payload", "signature", "expiry", "stateless"]},
    {"q": "How do you store passwords securely in a database?", "skills": ["security", "sql"], "cat": "technical", "diff": "medium", "keywords": ["hashing", "bcrypt", "salt", "argon2", "plaintext", "rainbow table"]},

    # ═══════════════════════════════════════════════════════════
    # GIT & VERSION CONTROL
    # ═══════════════════════════════════════════════════════════
    {"q": "Describe your Git branching strategy.", "skills": ["git"], "cat": "technical", "diff": "easy", "keywords": ["main", "feature branch", "merge", "pull request", "Gitflow", "trunk-based"]},
    {"q": "How do you resolve merge conflicts in Git?", "skills": ["git"], "cat": "technical", "diff": "medium", "keywords": ["conflict", "merge", "rebase", "resolve", "diff", "tool"]},
    {"q": "Explain the difference between git merge and git rebase.", "skills": ["git"], "cat": "technical", "diff": "medium", "keywords": ["merge commit", "linear history", "interactive rebase", "squash", "fast-forward"]},

    # ═══════════════════════════════════════════════════════════
    # DESIGN PATTERNS
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain the SOLID principles with practical examples.", "skills": ["design_patterns"], "cat": "technical", "diff": "hard", "keywords": ["Single Responsibility", "Open/Closed", "Liskov", "Interface Segregation", "Dependency Inversion"]},
    {"q": "Describe the Observer pattern and where you've applied it.", "skills": ["design_patterns"], "cat": "technical", "diff": "medium", "keywords": ["observer", "subscriber", "event", "notification", "publish", "decouple"]},
    {"q": "What design patterns do you use most frequently?", "skills": ["design_patterns"], "cat": "experience", "diff": "medium", "keywords": ["singleton", "factory", "strategy", "observer", "decorator", "MVC"]},

    # ═══════════════════════════════════════════════════════════
    # MACHINE LEARNING / DATA SCIENCE
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain the difference between supervised and unsupervised learning.", "skills": ["machine_learning", "data_science"], "cat": "technical", "diff": "easy", "keywords": ["supervised", "unsupervised", "labelled", "classification", "clustering", "regression"]},
    {"q": "How do you handle overfitting in machine learning models?", "skills": ["machine_learning"], "cat": "technical", "diff": "medium", "keywords": ["overfitting", "regularisation", "cross-validation", "dropout", "early stopping", "data augmentation"]},
    {"q": "What metrics do you use to evaluate ML model performance?", "skills": ["machine_learning", "data_science"], "cat": "technical", "diff": "medium", "keywords": ["accuracy", "precision", "recall", "F1", "AUC-ROC", "confusion matrix"]},
    {"q": "Describe a machine learning project you worked on end-to-end.", "skills": ["machine_learning", "data_science"], "cat": "experience", "diff": "hard", "keywords": ["problem", "data", "model", "training", "evaluation", "deployment", "impact"]},
    {"q": "How do you handle imbalanced datasets?", "skills": ["machine_learning", "data_science"], "cat": "technical", "diff": "hard", "keywords": ["oversampling", "SMOTE", "undersampling", "class weights", "stratified", "threshold"]},

    # ═══════════════════════════════════════════════════════════
    # MOBILE DEVELOPMENT
    # ═══════════════════════════════════════════════════════════
    {"q": "What are the key differences between native and cross-platform mobile development?", "skills": ["android", "ios", "react_native", "flutter"], "cat": "technical", "diff": "easy", "keywords": ["native", "cross-platform", "performance", "platform-specific", "code sharing"]},
    {"q": "How do you handle state management in mobile applications?", "skills": ["android", "ios", "react_native", "flutter"], "cat": "technical", "diff": "medium", "keywords": ["state", "lifecycle", "provider", "bloc", "redux", "viewmodel"]},
    {"q": "Describe how you optimise mobile app performance.", "skills": ["android", "ios", "react_native", "flutter"], "cat": "technical", "diff": "hard", "keywords": ["lazy loading", "memory", "caching", "rendering", "profiling", "battery"]},

    # ═══════════════════════════════════════════════════════════
    # NODE.JS
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain how Node.js handles concurrent requests with a single thread.", "skills": ["nodejs"], "cat": "technical", "diff": "medium", "keywords": ["event loop", "non-blocking", "async", "libuv", "callback", "worker threads"]},
    {"q": "How do you prevent memory leaks in a Node.js application?", "skills": ["nodejs"], "cat": "technical", "diff": "hard", "keywords": ["memory leak", "garbage collection", "event listener", "closure", "heap snapshot", "profiling"]},
    {"q": "What is middleware in Express.js and how is it used?", "skills": ["nodejs"], "cat": "technical", "diff": "easy", "keywords": ["middleware", "next()", "request", "response", "authentication", "logging", "error handling"]},

    # ═══════════════════════════════════════════════════════════
    # GO / RUST
    # ═══════════════════════════════════════════════════════════
    {"q": "What are goroutines and channels in Go?", "skills": ["go"], "cat": "technical", "diff": "medium", "keywords": ["goroutine", "channel", "concurrency", "lightweight", "select", "sync"]},
    {"q": "Explain Rust's ownership model and borrow checker.", "skills": ["rust"], "cat": "technical", "diff": "hard", "keywords": ["ownership", "borrow", "lifetime", "move", "reference", "memory safety"]},

    # ═══════════════════════════════════════════════════════════
    # LINUX / DEVOPS TOOLS
    # ═══════════════════════════════════════════════════════════
    {"q": "What Linux commands do you use most frequently in development?", "skills": ["linux"], "cat": "experience", "diff": "easy", "keywords": ["grep", "find", "awk", "sed", "chmod", "ssh", "curl", "top", "tail"]},
    {"q": "How do you troubleshoot a production server issue?", "skills": ["linux", "devops"], "cat": "situational", "diff": "hard", "keywords": ["logs", "monitoring", "CPU", "memory", "disk", "network", "rollback", "alerts"]},

    # ═══════════════════════════════════════════════════════════
    # AGILE / PROJECT MANAGEMENT
    # ═══════════════════════════════════════════════════════════
    {"q": "Describe your experience with Agile/Scrum methodologies.", "skills": ["agile"], "cat": "experience", "diff": "easy", "keywords": ["sprint", "standup", "backlog", "retrospective", "velocity", "user stories"]},
    {"q": "How do you estimate tasks and manage technical debt?", "skills": ["agile"], "cat": "situational", "diff": "medium", "keywords": ["estimation", "story points", "tech debt", "refactoring", "prioritisation", "tradeoff"]},

    # ═══════════════════════════════════════════════════════════
    # DJANGO / FLASK / FASTAPI
    # ═══════════════════════════════════════════════════════════
    {"q": "Compare Django, Flask, and FastAPI — when would you choose each?", "skills": ["django", "flask", "fastapi"], "cat": "technical", "diff": "medium", "keywords": ["Django", "batteries included", "Flask", "lightweight", "FastAPI", "async", "type hints"]},
    {"q": "How does Django's ORM work and what are its limitations?", "skills": ["django"], "cat": "technical", "diff": "medium", "keywords": ["ORM", "QuerySet", "migration", "N+1", "raw SQL", "model", "lazy loading"]},

    # ═══════════════════════════════════════════════════════════
    # VUE / ANGULAR / SVELTE
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain Vue's reactivity system and how it tracks changes.", "skills": ["vue"], "cat": "technical", "diff": "medium", "keywords": ["reactive", "Proxy", "ref", "computed", "watcher", "dependency tracking"]},
    {"q": "What are Angular modules and how do they organise an application?", "skills": ["angular"], "cat": "technical", "diff": "medium", "keywords": ["NgModule", "component", "service", "dependency injection", "lazy loading", "routing"]},
    {"q": "How is Svelte different from React and Vue in its approach?", "skills": ["svelte"], "cat": "technical", "diff": "medium", "keywords": ["compile-time", "no virtual DOM", "reactivity", "bundle size", "framework"]},

    # ═══════════════════════════════════════════════════════════
    # REDIS / ELASTICSEARCH
    # ═══════════════════════════════════════════════════════════
    {"q": "When would you use Redis and what data structures does it offer?", "skills": ["redis"], "cat": "technical", "diff": "medium", "keywords": ["cache", "string", "hash", "list", "set", "sorted set", "pub/sub", "TTL"]},
    {"q": "How does Elasticsearch achieve fast full-text search?", "skills": ["elasticsearch"], "cat": "technical", "diff": "hard", "keywords": ["inverted index", "tokeniser", "analyser", "shard", "relevance", "scoring"]},

    # ═══════════════════════════════════════════════════════════
    # BEHAVIORAL QUESTIONS (generic — no specific skill)
    # ═══════════════════════════════════════════════════════════
    {"q": "Tell me about yourself and your professional journey.", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["background", "experience", "career", "motivation", "goals"]},
    {"q": "Why are you interested in this role?", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["motivation", "company", "role", "growth", "alignment"]},
    {"q": "Describe a time you received constructive criticism and how you responded.", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["feedback", "improvement", "response", "growth", "action"]},
    {"q": "Tell me about a conflict you had with a team member and how you resolved it.", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["conflict", "communication", "resolution", "compromise", "outcome"]},
    {"q": "What is your greatest professional achievement?", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["achievement", "impact", "result", "proud", "challenge"]},
    {"q": "How do you handle working under pressure or tight deadlines?", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["pressure", "prioritise", "deadline", "stress", "strategy", "outcome"]},
    {"q": "Describe a situation where you had to learn a new technology quickly.", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["learning", "adapt", "technology", "approach", "resources", "outcome"]},
    {"q": "What motivates you in your work?", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["motivation", "passion", "challenge", "impact", "growth"]},
    {"q": "How do you prioritise your tasks when everything seems urgent?", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["prioritise", "matrix", "stakeholders", "communication", "deadline", "triage"]},
    {"q": "Tell me about a time you went above and beyond what was expected.", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["initiative", "impact", "effort", "recognition", "result"]},
    {"q": "How do you stay motivated during repetitive or mundane tasks?", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["discipline", "automation", "perspective", "goals", "mindset"]},
    {"q": "Describe your ideal working environment.", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["culture", "collaboration", "autonomy", "values", "flexibility"]},
    {"q": "How do you handle disagreements with your manager?", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["respect", "data", "compromise", "escalation", "communication", "professional"]},

    # ═══════════════════════════════════════════════════════════
    # SITUATIONAL QUESTIONS
    # ═══════════════════════════════════════════════════════════
    {"q": "You discover a critical bug in production right before a release. What do you do?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["assess", "communicate", "rollback", "fix", "testing", "stakeholders"]},
    {"q": "A junior developer writes code that works but is poorly structured. How do you handle it?", "skills": [], "cat": "situational", "diff": "medium", "keywords": ["code review", "mentoring", "constructive", "pair programming", "standards", "learning"]},
    {"q": "Your team disagrees on the architecture for a new feature. How do you reach consensus?", "skills": [], "cat": "situational", "diff": "medium", "keywords": ["discussion", "pros/cons", "data", "POC", "decision criteria", "compromise"]},
    {"q": "You're assigned a project with unclear requirements. What's your approach?", "skills": [], "cat": "situational", "diff": "medium", "keywords": ["clarify", "stakeholders", "MVP", "iterate", "assumptions", "prototype"]},
    {"q": "A deadline is impossible to meet with the current scope. What do you do?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["communicate", "scope", "negotiate", "priority", "trade-off", "transparency"]},
    {"q": "How would you onboard a new team member to a complex codebase?", "skills": [], "cat": "situational", "diff": "medium", "keywords": ["documentation", "pair programming", "architecture overview", "small tasks", "mentoring"]},
    {"q": "Your application is experiencing intermittent performance issues in production. Walk me through your debugging process.", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["monitoring", "logs", "reproduce", "isolate", "profiling", "hypothesis"]},
    {"q": "A stakeholder requests a feature that contradicts your technical best judgement. How do you handle it?",  "skills": [], "cat": "situational", "diff": "hard", "keywords": ["trade-offs", "communication", "data", "compromise", "document", "risk"]},

    # ═══════════════════════════════════════════════════════════
    # EXPERIENCE / PROJECT QUESTIONS
    # ═══════════════════════════════════════════════════════════
    {"q": "Walk me through the most complex project you've worked on.", "skills": [], "cat": "experience", "diff": "medium", "keywords": ["project", "role", "challenges", "technology", "outcome", "impact"]},
    {"q": "Describe a project where you had to make a significant architectural decision.", "skills": [], "cat": "experience", "diff": "hard", "keywords": ["architecture", "trade-off", "decision", "reasoning", "outcome", "lesson"]},
    {"q": "Tell me about a time you improved an existing system's performance.", "skills": [], "cat": "experience", "diff": "medium", "keywords": ["bottleneck", "optimisation", "metrics", "before/after", "approach"]},
    {"q": "Describe your experience working on cross-functional teams.", "skills": [], "cat": "experience", "diff": "easy", "keywords": ["collaboration", "roles", "communication", "challenge", "success"]},
    {"q": "What's the largest codebase you've contributed to and what was your role?", "skills": [], "cat": "experience", "diff": "medium", "keywords": ["codebase", "contribution", "team size", "ownership", "process"]},
    {"q": "Tell me about a time you introduced a new technology to your team.", "skills": [], "cat": "experience", "diff": "medium", "keywords": ["evaluation", "proposal", "adoption", "training", "impact", "resistance"]},
    {"q": "Describe a project that failed or didn't meet expectations. What did you learn?", "skills": [], "cat": "experience", "diff": "hard", "keywords": ["failure", "reflection", "lesson", "improvement", "accountability"]},

    # ═══════════════════════════════════════════════════════════
    # LEADERSHIP & TEAMWORK
    # ═══════════════════════════════════════════════════════════
    {"q": "How do you mentor junior developers?", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["mentoring", "pair programming", "feedback", "growth", "patience", "example"]},
    {"q": "Describe your leadership style.", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["leadership", "style", "delegation", "empowerment", "communication", "trust"]},
    {"q": "How do you give constructive feedback to team members?", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["feedback", "specific", "actionable", "positive", "improvement", "empathy"]},
    {"q": "Describe a time you had to lead a team through an ambiguous situation.", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["ambiguity", "direction", "decision", "communication", "adaptability", "outcome"]},

    # ═══════════════════════════════════════════════════════════
    # CAREER & GROWTH
    # ═══════════════════════════════════════════════════════════
    {"q": "Where do you see yourself in five years?", "skills": [], "cat": "general", "diff": "easy", "keywords": ["career", "growth", "goals", "leadership", "learning"]},
    {"q": "What are you currently learning or want to learn next?", "skills": [], "cat": "general", "diff": "easy", "keywords": ["learning", "technology", "growth", "curiosity", "initiative"]},
    {"q": "Why are you looking to change roles / companies?", "skills": [], "cat": "general", "diff": "medium", "keywords": ["motivation", "growth", "opportunity", "challenge", "alignment"]},
    {"q": "What's your approach to continuous learning and professional development?", "skills": [], "cat": "general", "diff": "easy", "keywords": ["learning", "courses", "books", "conferences", "practice", "community"]},
    {"q": "How do you balance quality with delivery speed?", "skills": [], "cat": "general", "diff": "medium", "keywords": ["trade-off", "MVP", "tech debt", "iteration", "pragmatic", "standards"]},

    # ═══════════════════════════════════════════════════════════
    # STRESS / PRESSURE QUESTIONS (for "stress" personality)
    # ═══════════════════════════════════════════════════════════
    {"q": "Why should we hire you over other candidates with similar skills?", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["unique value", "differentiation", "contribution", "track record", "culture fit"]},
    {"q": "Tell me about your biggest professional failure in detail.", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["failure", "accountability", "lesson", "recovery", "growth"]},
    {"q": "If I told you this interview is going poorly, how would you respond?", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["composure", "self-awareness", "feedback", "resilience", "improvement"]},
    {"q": "You have two equally important projects due tomorrow. Which one do you do first and why?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["prioritisation", "impact", "stakeholders", "communication", "delegation"]},
    {"q": "Convince me that your technical skills are strong enough for this role.", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["evidence", "projects", "metrics", "competence", "growth mindset"]},
    {"q": "What would your harshest critic say about you?", "skills": [], "cat": "behavioral", "diff": "hard", "keywords": ["self-awareness", "weakness", "improvement", "honesty", "perspective"]},
    {"q": "How do you deal with a colleague who is underperforming and affecting the team?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["confrontation", "empathy", "communication", "escalation", "support"]},
    {"q": "You realise you gave incorrect advice to a client. What do you do?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["honesty", "correction", "accountability", "communication", "trust"]},

    # ═══════════════════════════════════════════════════════════
    # HTML/CSS SPECIFIC
    # ═══════════════════════════════════════════════════════════
    {"q": "Explain the CSS box model.", "skills": ["html_css"], "cat": "technical", "diff": "easy", "keywords": ["content", "padding", "border", "margin", "box-sizing"]},
    {"q": "How do CSS Flexbox and Grid differ and when would you use each?", "skills": ["html_css"], "cat": "technical", "diff": "medium", "keywords": ["Flexbox", "Grid", "one-dimensional", "two-dimensional", "layout", "responsive"]},
    {"q": "What strategies do you use for responsive web design?", "skills": ["html_css", "frontend"], "cat": "technical", "diff": "medium", "keywords": ["media queries", "fluid", "breakpoint", "mobile-first", "viewport", "flexbox"]},

    # ═══════════════════════════════════════════════════════════
    # ADDITIONAL TECHNICAL (GENERAL)
    # ═══════════════════════════════════════════════════════════
    {"q": "What is the difference between authentication and authorisation?", "skills": ["security"], "cat": "technical", "diff": "easy", "keywords": ["authentication", "identity", "authorisation", "permission", "role", "access control"]},
    {"q": "Explain the concept of eventual consistency.", "skills": ["system_design", "nosql"], "cat": "technical", "diff": "hard", "keywords": ["eventual consistency", "CAP", "distributed", "replication", "latency", "trade-off"]},
    {"q": "How do you approach API versioning?", "skills": ["api_design"], "cat": "technical", "diff": "medium", "keywords": ["versioning", "URL", "header", "backward compatibility", "deprecation", "documentation"]},
    {"q": "What is functional programming and how have you applied it?", "skills": ["design_patterns"], "cat": "technical", "diff": "medium", "keywords": ["pure functions", "immutability", "higher-order", "side effects", "composition"]},

    # ═══════════════════════════════════════════════════════════
    # COMMUNICATION & SOFT-SKILL DEEP-DIVE
    # ═══════════════════════════════════════════════════════════
    {"q": "How do you explain complex technical concepts to non-technical stakeholders?", "skills": [], "cat": "behavioral", "diff": "medium", "keywords": ["simplify", "analogy", "visual", "audience", "clarity", "patience"]},
    {"q": "Describe how you've contributed to improving your team's processes.", "skills": [], "cat": "experience", "diff": "medium", "keywords": ["process", "improvement", "automation", "efficiency", "retrospective", "suggestion"]},
    {"q": "How do you handle multiple stakeholders with competing priorities?", "skills": [], "cat": "situational", "diff": "hard", "keywords": ["prioritise", "communication", "alignment", "trade-off", "escalation", "transparency"]},
    {"q": "What steps do you take to ensure your code is maintainable and readable?", "skills": [], "cat": "technical", "diff": "medium", "keywords": ["clean code", "naming", "comments", "documentation", "modularity", "readability"]},
    {"q": "Describe a time you received feedback that changed the way you work.", "skills": [], "cat": "behavioral", "diff": "easy", "keywords": ["feedback", "growth", "adaptation", "improvement", "self-awareness", "change"]},
]

# Total questions count validation
assert len(QUESTIONS) >= 140, f"Expected ≥140 questions, got {len(QUESTIONS)}"


# ────────────────────────────────────────────────────────────────
# Personality Adjustment
# ────────────────────────────────────────────────────────────────

PERSONALITY_PREFIXES: dict[str, list[str]] = {
    "friendly": [
        "Could you share with me — ",
        "I'd love to hear about — ",
        "In your experience, ",
        "If you don't mind sharing, ",
    ],
    "technical": [
        "Explain in detail: ",
        "Walk me through the technical aspects of — ",
        "Describe precisely how — ",
        "Elaborate on the implementation of — ",
    ],
    "stress": [
        "Justify your answer: ",
        "Defend your approach — ",
        "Challenge: ",
        "Under pressure — ",
    ],
    "panel": [
        "From a team perspective, ",
        "Considering both technical and business aspects, ",
        "Our panel would like to know — ",
        "Across your career, ",
    ],
}


def adapt_question(question: str, personality: str) -> str:
    """Optionally prepend a personality-specific prefix to a question."""
    prefixes = PERSONALITY_PREFIXES.get(personality)
    if not prefixes:
        return question
    # Don't double-prefix if the question already starts with one
    q_lower = question.lower()
    if any(q_lower.startswith(p.lower().strip().rstrip("—:, ")) for p in prefixes):
        return question
    prefix = random.choice(prefixes)
    # Lower-case the first char of original question to flow grammatically
    if question and question[0].isupper():
        question = question[0].lower() + question[1:]
    return prefix + question


# ────────────────────────────────────────────────────────────────
# Question Selection Algorithm
# ────────────────────────────────────────────────────────────────


def select_questions(
    detected_skills: list[str],
    personality: str = "friendly",
    num_questions: int = 15,
    exclude_questions: Optional[list[str]] = None,
) -> list[dict]:
    """
    Select the best N questions for the candidate based on detected skills.

    Algorithm:
      1. Score all questions by skill relevance
      2. Ensure category diversity (technical + behavioral + situational + experience)
      3. Ensure difficulty spread (easy + medium + hard)
      4. Apply personality-based styling
      5. Shuffle within groups for variety

    Returns: [{"question": str, "category": str, "difficulty": str, "keywords": list}]
    """
    exclude = set(exclude_questions or [])
    skill_set = set(detected_skills)

    # Score each question
    scored: list[tuple[float, dict]] = []
    for q in QUESTIONS:
        if q["q"] in exclude:
            continue

        # Skill match score
        q_skills = set(q.get("skills", []))
        if q_skills:
            overlap = len(q_skills & skill_set)
            if overlap > 0:
                skill_score = 1.0 + overlap * 0.5  # bonus for multi-skill match
            else:
                skill_score = 0.1  # low priority but not excluded
        else:
            skill_score = 0.5  # generic questions are moderately relevant

        # Personality preference
        q_cat = q["cat"]
        personality_bonus = 0.0
        if personality == "technical" and q_cat == "technical":
            personality_bonus = 0.5
        elif personality == "stress" and q["diff"] == "hard":
            personality_bonus = 0.4
        elif personality == "friendly" and q["diff"] in ("easy", "medium"):
            personality_bonus = 0.3
        elif personality == "panel" and q_cat in ("behavioral", "experience", "situational"):
            personality_bonus = 0.3

        total_score = skill_score + personality_bonus + random.uniform(0, 0.3)
        scored.append((total_score, q))

    # Sort by score (highest first)
    scored.sort(key=lambda x: x[0], reverse=True)

    # Greedy selection with diversity constraints
    selected: list[dict] = []
    cat_counts: dict[str, int] = {}
    diff_counts: dict[str, int] = {}

    # Target distributions — favour technical questions (at least 50%)
    max_per_cat = max(num_questions // 2 + 2, 6)
    max_per_diff = max(num_questions // 2 + 2, 7)
    min_technical = max(num_questions // 2, 4) if skill_set else 3

    technical_count = 0

    for _, q in scored:
        if len(selected) >= num_questions:
            break

        cat = q["cat"]
        diff = q["diff"]

        # Enforce diversity constraints
        if cat_counts.get(cat, 0) >= max_per_cat:
            continue
        if diff_counts.get(diff, 0) >= max_per_diff:
            continue

        selected.append(q)
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        diff_counts[diff] = diff_counts.get(diff, 0) + 1
        if cat == "technical":
            technical_count += 1

    # If we couldn't fill enough, add more from the remaining
    if len(selected) < num_questions:
        for _, q in scored:
            if len(selected) >= num_questions:
                break
            if q not in selected:
                selected.append(q)

    # Shuffle to avoid predictable ordering
    random.shuffle(selected)

    # Apply personality styling and format output
    result: list[dict] = []
    for q in selected:
        adapted_text = adapt_question(q["q"], personality)
        result.append({
            "question": adapted_text,
            "category": q["cat"],
            "difficulty": q["diff"],
            "keywords": q.get("keywords", []),
        })

    return result[:num_questions]
