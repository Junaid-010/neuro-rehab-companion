import sqlite3
import hashlib
import os
import datetime

DB_NAME = "rehab_engine.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. IDENTITY & RBAC
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        stroke_type TEXT NOT NULL,
        affected_side TEXT NOT NULL,
        fma_score INTEGER DEFAULT 0,
        role TEXT DEFAULT 'Patient',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. LONGITUDINAL PROGRESS (Stage 6)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        user_id INTEGER PRIMARY KEY,
        total_sessions INTEGER DEFAULT 0,
        total_repetitions INTEGER DEFAULT 0,
        current_streak INTEGER DEFAULT 0,
        best_streak INTEGER DEFAULT 0,
        last_session_date DATE,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    # 3. MACRO-SESSION CONTEXT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercise_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP,
        session_status TEXT DEFAULT 'ACTIVE',
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)
    
    # 4. MICRO-TELEMETRY & ML FEATURE VECTOR (Stage 11 & 16)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kinematic_telemetry (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        exercise_name TEXT NOT NULL,
        joint_angle REAL,
        compensation_metric REAL,
        safety_flag INTEGER NOT NULL,
        movement_stage TEXT NOT NULL,
        delta_time REAL,
        angular_velocity REAL,
        repetition_count INTEGER,
        repetition_duration REAL,
        range_of_motion REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES exercise_sessions (session_id),
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    # 5. NLP CHECK-INS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS psychology_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        user_id INTEGER NOT NULL,
        transcription TEXT,
        sentiment_label TEXT NOT NULL,
        llm_response TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES exercise_sessions (session_id),
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)

    # SECURE MASTER ADMIN INJECTION
    cursor.execute("SELECT * FROM users WHERE username = 'admin_junaid'")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, age, stroke_type, affected_side, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('admin_junaid', hash_password_pbkdf2('admin123'), 'Muhammad Junaid (Lead Clinician)', 23, 'N/A', 'N/A', 'Clinician (Admin)'))
    
    conn.commit()
    conn.close()

# =====================================================================
# CRYPTOGRAPHY: PBKDF2-HMAC-SHA256 (Stage 2 Hardening)
# =====================================================================
def hash_password_pbkdf2(password: str, salt: bytes = None) -> str:
    """Generates a secure PBKDF2 hash using a cryptographically random salt."""
    if salt is None:
        salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ':' + key.hex()

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verifies a password, handling both PBKDF2 and legacy prototype hashes."""
    if ':' in stored_hash:
        salt_hex, key_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        test_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000).hex()
        return test_key == key_hex
    else:
        # Legacy fallback for prototype accounts created prior to Stage 2
        legacy_test = hashlib.sha256(provided_password.encode()).hexdigest()
        return legacy_test == stored_hash

# =====================================================================
# AUTHENTICATION & IDENTITY
# =====================================================================
def authenticate_user(username, password):
    if not username or not password:
        return None
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? LIMIT 1", (username.strip(),))
    user = cursor.fetchone()
    
    if user and verify_password(user['password_hash'], password):
        # MIGRATION TRIGGER: Upgrade legacy hashes to PBKDF2 seamlessly
        if ':' not in user['password_hash']:
            new_hash = hash_password_pbkdf2(password)
            cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hash, user['user_id']))
            conn.commit()
        conn.close()
        return user
        
    conn.close()
    return None

def register_user(username, password, full_name, age, stroke_type, affected_side):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Insert user identity
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, age, stroke_type, affected_side, role)
        VALUES (?, ?, ?, ?, ?, ?, 'Patient')
        """, (username, hash_password_pbkdf2(password), full_name, age, stroke_type, affected_side))
        
        user_id = cursor.lastrowid
        
        # Initialize user progress record
        cursor.execute("INSERT INTO user_progress (user_id) VALUES (?)", (user_id,))
        
        conn.commit()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    finally:
        conn.close()

def sanitize_user_record(user):
    if user is None: return None
    # # Convert the sqlite3.Row to a standard dictionary first
    # user_dict = dict(user)
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "stroke_type": user["stroke_type"]
    }

def get_all_patients():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, full_name, stroke_type FROM users WHERE role = 'Patient'")
    patients = cursor.fetchall()
    conn.close()
    return patients

# =====================================================================
# MACRO-SESSION & MICRO-TELEMETRY LOGGING (Stages 5, 11 & 16)
# =====================================================================
def create_exercise_session(user_id: int) -> int:
    """Initializes a new session and returns the session_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO exercise_sessions (user_id, session_status) VALUES (?, 'ACTIVE')", (user_id,))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def log_kinematic_telemetry(session_id, user_id, exercise_name, features: dict):
    """
    Persists the structured 10-point ML Feature Contract vector.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO kinematic_telemetry (
        session_id, user_id, exercise_name, joint_angle, compensation_metric, 
        safety_flag, movement_stage, delta_time, angular_velocity, 
        repetition_count, repetition_duration, range_of_motion
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id, user_id, exercise_name,
        features.get('joint_angle', 0.0),
        features.get('compensation_metric', 0.0),
        1 if features.get('safety_flag') else 0,
        features.get('movement_stage', 'UNKNOWN'),
        features.get('delta_time', 0.0),
        features.get('angular_velocity', 0.0),
        features.get('repetition_count', 0),
        features.get('repetition_duration', 0.0),
        features.get('range_of_motion', 0.0)
    ))
    conn.commit()
    conn.close()

def log_psychology_sentiment(session_id, user_id, transcription, sentiment, response):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO psychology_logs (session_id, user_id, transcription, sentiment_label, llm_response)
    VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_id, transcription, sentiment, response))
    conn.commit()
    conn.close()

def conclude_exercise_session(session_id: int, completed_reps: int):
    """Marks a session as COMPLETED and updates the user_progress table."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Close the session
    end_time = datetime.datetime.now().isoformat()
    cursor.execute("""
    UPDATE exercise_sessions SET session_status = 'COMPLETED', end_time = ? WHERE session_id = ?
    """, (end_time, session_id))
    
    # 2. Update progress/streaks
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT last_session_date, current_streak, best_streak FROM user_progress WHERE user_id = (SELECT user_id FROM exercise_sessions WHERE session_id = ?)", (session_id,))
    progress = cursor.fetchone()
    
    if progress:
        last_date = progress['last_session_date']
        current_streak = progress['current_streak']
        best_streak = progress['best_streak']
        
        if last_date != today:
            # Simple streak logic: if it's a new day, increment streak. (A true production app checks if delta == 1 day)
            current_streak += 1
            if current_streak > best_streak:
                best_streak = current_streak

        cursor.execute("""
        UPDATE user_progress 
        SET total_sessions = total_sessions + 1,
            total_repetitions = total_repetitions + ?,
            current_streak = ?,
            best_streak = ?,
            last_session_date = ?
        WHERE user_id = (SELECT user_id FROM exercise_sessions WHERE session_id = ?)
        """, (completed_reps, current_streak, best_streak, today, session_id))
        
    conn.commit()
    conn.close()