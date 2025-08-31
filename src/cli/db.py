"""
Database command for Douglas CLI
"""
from pathlib import Path
from ..database import get_douglas_data_dir


def handle_db_command(args):
    """Handle database-related commands"""
    if not args or args[0] == "list":
        # List all databases
        data_dir = get_douglas_data_dir()
        db_dir = data_dir / "databases"

        if not db_dir.exists():
            print("no databases directory")
            return

        # Find all .db files
        db_files = list(db_dir.glob("*.db"))

        if not db_files:
            print("no databases found")
            return

        for db_file in sorted(db_files):
            galaxy_name = db_file.stem
            file_size = db_file.stat().st_size

            # Format file size nicely
            if file_size < 1024:
                size_str = f"{file_size}b"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.0f}k"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f}m"

            print(f"{galaxy_name:<20} {size_str:>8}")

    else:
        print(f"unknown db command: {args[0]}")
        print("try: db")
