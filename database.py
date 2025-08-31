"""
Database operations for Douglas
"""
import os
import sqlite3
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
