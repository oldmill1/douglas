"""
Database operations for Douglas
"""
import os
import sqlite3
import json
import yaml
from pathlib import Path


def get_douglas_data_dir():
    """Get the platform-specific Douglas data directory"""
    home = Path.home()

    # Use platform-specific data directory conventions
    if os.name == 'nt':  # Windows
        data_dir = home / "AppData" / "Local" / "douglas"
    else:  # macOS and Linux
        data_dir = home / ".douglas"

    return data_dir


def get_database_dir():
    """Get the databases directory, creating it if needed"""
    db_dir = get_douglas_data_dir() / "databases"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir


def get_database_path(galaxy_name):
    """Get the database file path for a specific galaxy"""
    db_dir = get_database_dir()
    return db_dir / f"{galaxy_name}.db"


def initialize_database(galaxy_name, models):
    """Initialize SQLite database for a galaxy with its models"""
    db_path = get_database_path(galaxy_name)

    try:
        # Connect to SQLite database (creates file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Initialize each model as a table
        for model in models:
            model_name = model.get('name', '').lower()
            model_type = model.get('type', 'json')

            if not model_name:
                continue

            # Check if table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (model_name,))

            if cursor.fetchone() is None:
                # Table doesn't exist, create it
                if model_type == 'json':
                    create_sql = f"""
                    CREATE TABLE {model_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        content TEXT NOT NULL
                    )
                    """
                else:
                    # Future: handle other model types
                    create_sql = f"""
                    CREATE TABLE {model_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        data TEXT NOT NULL
                    )
                    """

                cursor.execute(create_sql)
                print(f"📊 Created table '{model_name}' in {galaxy_name}.db")

        # Commit and close
        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Database initialization error for {galaxy_name}: {e}")
        return False


def get_douglas_root():
    """Get the root directory where Douglas is installed"""
    # Go up from src/ to find the root directory
    return Path(__file__).parent.parent


def get_first_model_name(galaxy_name):
    """Get the first (and assumed only) model name from galaxy YAML"""
    douglas_root = get_douglas_root()
    galaxy_path = douglas_root / "apps" / f"{galaxy_name}.yaml"

    if not galaxy_path.exists():
        return None

    try:
        with open(galaxy_path, 'r') as f:
            galaxy_config = yaml.safe_load(f)

        models = galaxy_config.get('database', {}).get('models', [])
        if models:
            return models[0].get('name', '').lower()
        return None

    except Exception as e:
        print(f"❌ Error reading galaxy config: {e}")
        return None


def save_entry_to_database(galaxy_name, content):
    """Save JSON content to the first model in the galaxy's database"""
    # Auto-detect the first (and assumed only) model table
    table_name = get_first_model_name(galaxy_name)
    if not table_name:
        print(f"❌ No database models found for galaxy {galaxy_name}")
        return False

    db_path = get_database_path(galaxy_name)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Insert the JSON content
        cursor.execute(f"""
            INSERT INTO {table_name} (content) VALUES (?)
        """, (content,))

        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()

        return entry_id

    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return False


def get_all_entries_from_database(galaxy_name):
    """Retrieve all entries from the galaxy's database"""
    table_name = get_first_model_name(galaxy_name)
    if not table_name:
        print(f"❌ No database models found for galaxy {galaxy_name}")
        return []

    db_path = get_database_path(galaxy_name)

    if not db_path.exists():
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, created_at, content FROM {table_name} 
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        # Convert to list of dictionaries
        entries = []
        for row in rows:
            entry = {
                'id': row[0],
                'created_at': row[1],
                'content': row[2]
            }

            # Try to parse JSON content for easier access
            try:
                entry['parsed_content'] = json.loads(row[2])
            except json.JSONDecodeError:
                entry['parsed_content'] = None

            entries.append(entry)

        return entries

    except Exception as e:
        print(f"❌ Error retrieving from database: {e}")
        return []


def count_entries_in_database(galaxy_name):
    """Count total entries in the galaxy's database"""
    table_name = get_first_model_name(galaxy_name)
    if not table_name:
        return 0

    db_path = get_database_path(galaxy_name)

    if not db_path.exists():
        return 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        conn.close()

        return count

    except Exception as e:
        print(f"❌ Error counting entries: {e}")
        return 0


def delete_entry_from_database(galaxy_name, entry_id):
    """Delete a specific entry from the galaxy's database"""
    table_name = get_first_model_name(galaxy_name)
    if not table_name:
        print(f"❌ No database models found for galaxy {galaxy_name}")
        return False

    db_path = get_database_path(galaxy_name)

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Delete the specific entry
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (entry_id,))

        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_deleted > 0

    except Exception as e:
        print(f"❌ Error deleting entry: {e}")
        return False


def delete_multiple_entries_from_database(galaxy_name, entry_ids):
    """Delete multiple entries from the galaxy's database"""
    table_name = get_first_model_name(galaxy_name)
    if not table_name:
        print(f"❌ No database models found for galaxy {galaxy_name}")
        return 0

    db_path = get_database_path(galaxy_name)

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 0

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Delete multiple entries using IN clause
        placeholders = ','.join('?' * len(entry_ids))
        cursor.execute(f"DELETE FROM {table_name} WHERE id IN ({placeholders})", entry_ids)

        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_deleted

    except Exception as e:
        print(f"❌ Error deleting entries: {e}")
        return 0
