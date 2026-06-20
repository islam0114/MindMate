# auth.py - MindMate User Authentication
import sqlite3
import hashlib
import secrets
import datetime

DB_NAME = "mindmate.db"

# ==========================================
# initialize users table
# ==========================================
def init_users_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at   TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token      TEXT PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# ==========================================
# Hash passwords securely
# ==========================================
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# ==========================================
# Register New User
# ==========================================
def register_user(username: str, email: str, password: str):
    """
    Returns: (True, user_id) or (False, error_message)
    """
    if len(username) < 3:
        return False, "الاسم لازم يكون 3 حروف على الأقل"
    if len(password) < 6:
        return False, "الباسورد لازم يكون 6 حروف على الأقل"
    if "@" not in email:
        return False, "الإيميل مش صح"

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username.strip(), email.strip().lower(),
             _hash_password(password),
             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        user_id = c.lastrowid
        return True, user_id
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "الاسم ده موجود بالفعل، جرب اسم تاني"
        if "email" in str(e):
            return False, "الإيميل ده مسجّل بالفعل"
        return False, "حصل خطأ، جرب تاني"
    finally:
        conn.close()

# ==========================================
# Login User
# ==========================================
def login_user(username: str, password: str):
    """
    Returns: (True, user_id, username) or (False, error_message, None)
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username.strip(),)
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return False, "الاسم أو الباسورد غلط", None

    user_id, uname, stored_hash = row
    if stored_hash != _hash_password(password):
        return False, "الاسم أو الباسورد غلط", None

    return True, user_id, uname

# ==========================================
# Extract User by ID
# ==========================================
def get_user_by_id(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None