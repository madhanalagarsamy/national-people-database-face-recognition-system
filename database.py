import sqlite3
import hashlib
from datetime import datetime
import os
import config

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hashes a password string using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initializes database tables and pre-populates default admin account if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table: citizens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citizens (
            citizen_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            dob TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            national_id TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            photo_path TEXT NOT NULL,
            criminal_record TEXT,
            document_path TEXT,
            document_description TEXT,
            created_at TEXT NOT NULL
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_citizens_name ON citizens(name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_citizens_national_id ON citizens(national_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_citizens_id ON citizens(citizen_id);")

    # Migrate existing database files if columns are missing
    cursor.execute("PRAGMA table_info(citizens);")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if "criminal_record" not in existing_columns:
        cursor.execute("ALTER TABLE citizens ADD COLUMN criminal_record TEXT;")
    if "document_path" not in existing_columns:
        cursor.execute("ALTER TABLE citizens ADD COLUMN document_path TEXT;")
    if "document_description" not in existing_columns:
        cursor.execute("ALTER TABLE citizens ADD COLUMN document_description TEXT;")

    # Table: users (Authentication)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

    # Table: recognition_logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recognition_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            citizen_id INTEGER,
            citizen_name TEXT NOT NULL,
            confidence REAL NOT NULL,
            status TEXT NOT NULL
        );
    """)

    # Seed default admin account if no users exist
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        admin_pass_hash = hash_password(config.DEFAULT_ADMIN_PASS)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?);",
            (config.DEFAULT_ADMIN_USER, admin_pass_hash, now_str)
        )

    conn.commit()
    conn.close()

def login(username, password):
    """Verifies username and password against users table."""
    conn = get_connection()
    cursor = conn.cursor()
    pass_hash = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?;", (username, pass_hash))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_citizen(citizen_id, name, age, gender, dob, address, phone, national_id, email, photo_path, criminal_record=None, document_path=None, document_description=None):
    """Inserts a new citizen record into database, including optional admin fields."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
            INSERT INTO citizens (citizen_id, name, age, gender, dob, address, phone, national_id, email, photo_path, criminal_record, document_path, document_description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (int(citizen_id), name, int(age), gender, dob, address, phone, national_id, email, photo_path, criminal_record, document_path, document_description, now_str))
        conn.commit()
        return True, "Citizen record registered successfully."
    except sqlite3.IntegrityError as e:
        err_msg = str(e)
        if "PRIMARY KEY" in err_msg or "citizens.citizen_id" in err_msg:
            return False, f"Citizen ID {citizen_id} already exists in the system."
        elif "national_id" in err_msg:
            return False, f"National ID {national_id} is already registered."
        else:
            return False, f"Database Integrity Error: {err_msg}"
    except Exception as e:
        return False, f"Error adding citizen: {str(e)}"
    finally:
        conn.close()

def update_citizen(citizen_id, name, address, phone, email, photo_path=None, criminal_record=None, document_path=None, document_description=None):
    """Updates editable details of an existing citizen record, including optional admin fields."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        fields = []
        params = []
        if name is not None:
            fields.append("name = ?")
            params.append(name)
        if address is not None:
            fields.append("address = ?")
            params.append(address)
        if phone is not None:
            fields.append("phone = ?")
            params.append(phone)
        if email is not None:
            fields.append("email = ?")
            params.append(email)
        if photo_path is not None:
            fields.append("photo_path = ?")
            params.append(photo_path)
        if criminal_record is not None:
            fields.append("criminal_record = ?")
            params.append(criminal_record)
        if document_path is not None:
            fields.append("document_path = ?")
            params.append(document_path)
        if document_description is not None:
            fields.append("document_description = ?")
            params.append(document_description)
        if not fields:
            return False, "No fields provided for update."
        set_clause = ", ".join(fields)
        params.append(int(citizen_id))
        cursor.execute(f"""
            UPDATE citizens
            SET {set_clause}
            WHERE citizen_id = ?;
        """, params)
        conn.commit()
        return True, "Citizen details updated successfully."
    except Exception as e:
        return False, f"Error updating citizen: {str(e)}"
    finally:
        conn.close()

def delete_citizen(citizen_id):
    """Deletes a citizen record and returns their photo path for disk cleanup."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT photo_path FROM citizens WHERE citizen_id = ?;", (int(citizen_id),))
        row = cursor.fetchone()
        if not row:
            return False, "Citizen ID not found.", None

        photo_path = row['photo_path']
        cursor.execute("DELETE FROM citizens WHERE citizen_id = ?;", (int(citizen_id),))
        conn.commit()
        return True, "Citizen record deleted successfully.", photo_path
    except Exception as e:
        return False, f"Error deleting citizen: {str(e)}", None
    finally:
        conn.close()

def search_citizen(query):
    """Searches citizens by Citizen ID or Name."""
    conn = get_connection()
    cursor = conn.cursor()
    query_str = f"%{query}%"
    cursor.execute("""
        SELECT * FROM citizens
        WHERE CAST(citizen_id AS TEXT) LIKE ? OR LOWER(name) LIKE LOWER(?) OR national_id LIKE ?
        ORDER BY citizen_id ASC;
    """, (query_str, query_str, query_str))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_citizen_by_id(citizen_id):
    """Fetches a single citizen by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citizens WHERE citizen_id = ?;", (int(citizen_id),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_citizens():
    """Returns all citizen records sorted by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citizens ORDER BY citizen_id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_recognition(citizen_id, citizen_name, confidence, status):
    """Logs a face recognition attempt into database."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c_id = int(citizen_id) if citizen_id else None
    cursor.execute("""
        INSERT INTO recognition_logs (timestamp, citizen_id, citizen_name, confidence, status)
        VALUES (?, ?, ?, ?, ?);
    """, (now_str, c_id, citizen_name, round(confidence, 2), status))
    conn.commit()
    conn.close()

def get_report_stats():
    """Retrieves aggregated statistics for the Reports module."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total Citizens
    cursor.execute("SELECT COUNT(*) FROM citizens;")
    total_citizens = cursor.fetchone()[0]

    # Gender Breakdown
    cursor.execute("SELECT COUNT(*) FROM citizens WHERE LOWER(gender) = 'male';")
    male_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM citizens WHERE LOWER(gender) = 'female';")
    female_count = cursor.fetchone()[0]

    other_gender_count = total_citizens - (male_count + female_count)

    # Recognition Logs Metrics
    cursor.execute("SELECT COUNT(*) FROM recognition_logs;")
    total_attempts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM recognition_logs WHERE UPPER(status) = 'SUCCESS';")
    successful_recognitions = cursor.fetchone()[0]

    # Recent Logs
    cursor.execute("SELECT * FROM recognition_logs ORDER BY id DESC LIMIT 20;")
    recent_logs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_citizens": total_citizens,
        "male_count": male_count,
        "female_count": female_count,
        "other_gender_count": other_gender_count,
        "total_attempts": total_attempts,
        "successful_recognitions": successful_recognitions,
        "recent_logs": recent_logs
    }
