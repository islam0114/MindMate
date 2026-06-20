# database.py - MindMate v3.0
import sqlite3
import datetime
import json

DB_NAME = "mindmate.db"

# ==========================================
# Database Initialization & Migrations
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # ===== daily_logs table =====
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_logs (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id          INTEGER DEFAULT 1,
            date_str         TEXT NOT NULL,
            last_updated     TEXT,
            user_text        TEXT,
            ai_response      TEXT,
            sleep_hours      REAL,
            study_hours      REAL,
            screen_hours     REAL,
            social_hours     REAL,
            water_cups       INTEGER,
            meal_count       INTEGER,
            stress_level     INTEGER,
            mood_category    TEXT,
            day_emoji        TEXT,
            color_code       TEXT,
            exercise_minutes REAL,
            crisis_level     TEXT DEFAULT 'none',
            wellness_score   INTEGER DEFAULT NULL,
            chat_history     TEXT,
            UNIQUE(user_id, date_str)
        )
    ''')

    # ===== goals table (Updated with priority) =====
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER DEFAULT 1,
            metric     TEXT NOT NULL,
            target     REAL NOT NULL,
            priority   TEXT DEFAULT 'متوسط',
            created_at TEXT NOT NULL
        )
    ''')

    # ===== Safe Migrations for existing tables =====
    existing_logs = [row[1] for row in c.execute("PRAGMA table_info(daily_logs)").fetchall()]
    new_cols = [
        ("exercise_minutes", "REAL"),
        ("crisis_level",     "TEXT DEFAULT 'none'"),
        ("user_id",          "INTEGER DEFAULT 1"),
        ("wellness_score",   "INTEGER DEFAULT NULL"),
        ("chat_history",     "TEXT"),
    ]
    for col_name, col_type in new_cols:
        if col_name not in existing_logs:
            c.execute(f"ALTER TABLE daily_logs ADD COLUMN {col_name} {col_type}")

    # Add priority column to existing goals if not present
    existing_goals = [row[1] for row in c.execute("PRAGMA table_info(goals)").fetchall()]
    if "priority" not in existing_goals:
        c.execute("ALTER TABLE goals ADD COLUMN priority TEXT DEFAULT 'متوسط'")

    conn.commit()
    conn.close()

# ==========================================
# Wellness Score Calculation
# ==========================================
def calculate_wellness_score(data: dict) -> int:
    score = 40  
    sleep = data.get("sleep_hours")
    stress = data.get("stress_level")
    water = data.get("water_cups")
    exercise = data.get("exercise_minutes")
    meals = data.get("meal_count")
    screen = data.get("screen_hours")

    if sleep is not None:
        if sleep >= 8:   score += 18
        elif sleep >= 7: score += 14
        elif sleep >= 6: score += 8
        else:            score += 2

    if stress is not None:
        if stress <= 2:   score += 15
        elif stress <= 4: score += 12
        elif stress <= 6: score += 7
        elif stress <= 8: score += 3
        else:             score += 0

    if water is not None:
        if water >= 10:  score += 12
        elif water >= 8: score += 10
        elif water >= 5: score += 6
        else:            score += 2

    if exercise is not None:
        if exercise >= 45:  score += 10
        elif exercise >= 30: score += 8
        elif exercise >= 15: score += 5
        else:                score += 2

    if meals is not None:
        if meals >= 3: score += 5
        else:          score += 2

    if screen is not None:
        if screen <= 2:  score += 5
        elif screen <= 4: score += 3
        else:             score += 0

    return min(score, 100)

# ==========================================
# Daily Logs Management
# ==========================================
def save_log(text, response, data_dict, mood_summary, chat_history_list=None, crisis_level="none", user_id=1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    now_time  = datetime.datetime.now().strftime("%H:%M:%S")
    wellness  = calculate_wellness_score(data_dict)
    chat_str  = json.dumps(chat_history_list, ensure_ascii=False) if chat_history_list else None

    c.execute("SELECT id FROM daily_logs WHERE date_str = ? AND user_id = ?", (today_str, user_id))
    existing = c.fetchone()

    if existing is None:
        c.execute('''
            INSERT INTO daily_logs (
                user_id, date_str, last_updated, user_text, ai_response,
                sleep_hours, study_hours, screen_hours, social_hours,
                water_cups, meal_count, stress_level, exercise_minutes,
                mood_category, day_emoji, color_code, crisis_level, wellness_score, chat_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, today_str, now_time, text, response,
            data_dict.get("sleep_hours"), data_dict.get("study_hours"),
            data_dict.get("screen_hours"), data_dict.get("social_hours"),
            data_dict.get("water_cups"), data_dict.get("meal_count"),
            data_dict.get("stress_level"), data_dict.get("exercise_minutes"),
            mood_summary.get("category"), mood_summary.get("emoji"),
            mood_summary.get("color"), crisis_level, wellness, chat_str
        ))
    else:
        c.execute('''
            UPDATE daily_logs SET
                last_updated     = ?,
                user_text        = ?,
                ai_response      = ?,
                sleep_hours      = COALESCE(?, sleep_hours),
                study_hours      = COALESCE(?, study_hours),
                screen_hours     = COALESCE(?, screen_hours),
                social_hours     = COALESCE(?, social_hours),
                water_cups       = COALESCE(?, water_cups),
                meal_count       = COALESCE(?, meal_count),
                stress_level     = COALESCE(?, stress_level),
                exercise_minutes = COALESCE(?, exercise_minutes),
                mood_category    = ?,
                day_emoji        = ?,
                color_code       = ?,
                wellness_score   = ?,
                crisis_level     = CASE WHEN ? IN ('moderate','severe') THEN ? ELSE crisis_level END,
                chat_history     = ?
            WHERE date_str = ? AND user_id = ?
        ''', (
            now_time, text, response,
            data_dict.get("sleep_hours"), data_dict.get("study_hours"),
            data_dict.get("screen_hours"), data_dict.get("social_hours"),
            data_dict.get("water_cups"), data_dict.get("meal_count"),
            data_dict.get("stress_level"), data_dict.get("exercise_minutes"),
            mood_summary.get("category"), mood_summary.get("emoji"),
            mood_summary.get("color"), wellness,
            crisis_level, crisis_level, chat_str,
            today_str, user_id
        ))

    conn.commit()
    conn.close()

def update_daily_data(user_id, data_dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    wellness = calculate_wellness_score(data_dict)

    c.execute("SELECT id FROM daily_logs WHERE date_str = ? AND user_id = ?", (today_str, user_id))
    existing = c.fetchone()

    if existing is None:
        c.execute('''
            INSERT INTO daily_logs (
                user_id, date_str, sleep_hours, study_hours, screen_hours, social_hours,
                water_cups, meal_count, stress_level, exercise_minutes, wellness_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, today_str,
            data_dict.get("sleep_hours"), data_dict.get("study_hours"),
            data_dict.get("screen_hours"), data_dict.get("social_hours"),
            data_dict.get("water_cups"), data_dict.get("meal_count"),
            data_dict.get("stress_level"), data_dict.get("exercise_minutes"),
            wellness
        ))
    else:
        c.execute('''
            UPDATE daily_logs SET
                sleep_hours      = ?,
                study_hours      = ?,
                screen_hours     = ?,
                social_hours     = ?,
                water_cups       = ?,
                meal_count       = ?,
                stress_level     = ?,
                exercise_minutes = ?,
                wellness_score   = ?
            WHERE date_str = ? AND user_id = ?
        ''', (
            data_dict.get("sleep_hours"), data_dict.get("study_hours"),
            data_dict.get("screen_hours"), data_dict.get("social_hours"),
            data_dict.get("water_cups"), data_dict.get("meal_count"),
            data_dict.get("stress_level"), data_dict.get("exercise_minutes"),
            wellness, today_str, user_id
        ))

    conn.commit()
    conn.close()

def get_today_log(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM daily_logs WHERE date_str = ? AND user_id = ?", (today_str, user_id))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_logs(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs WHERE user_id = ? ORDER BY date_str ASC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_weekly_logs(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs WHERE user_id = ? ORDER BY date_str DESC LIMIT 7", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

# ==========================================
# Goals Management
# ==========================================
def save_goal(user_id, metric, target, priority="متوسط"):
    """
    Saves a new goal or overwrites an existing one for the same metric (acts as an edit function).
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE user_id = ? AND metric = ?", (user_id, metric))
    c.execute(
        "INSERT INTO goals (user_id, metric, target, priority, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, metric, target, priority, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def delete_goal(user_id, metric):
    """
    Deletes a specific goal for the user based on the metric key.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM goals WHERE user_id = ? AND metric = ?", (user_id, metric))
    conn.commit()
    conn.close()

def get_goals(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ==========================================
# Streak Calculation
# ==========================================
def get_streak(user_id=1):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date_str FROM daily_logs WHERE user_id = ? ORDER BY date_str DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows: return 0
    dates = [datetime.datetime.strptime(r[0], "%Y-%m-%d") for r in rows]
    streak = 1
    for i in range(len(dates) - 1):
        if (dates[i] - dates[i+1]).days == 1:
            streak += 1
        else:
            break
    return streak