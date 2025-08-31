#!/usr/bin/env python3
"""
Douglas Database Nuke Script

WARNING: This will permanently delete all Douglas databases!
Only use this for development/testing purposes.
"""
import sys
import yaml
from pathlib import Path


def get_douglas_root():
    """Get the root directory where Douglas is installed"""
    # This script is in scripts/, go up one level to find the root
    return Path(__file__).parent.parent


def get_douglas_data_dir():
    """Get the platform-specific Douglas data directory"""
    import os
    home = Path.home()

    # Use platform-specific data directory conventions
    if os.name == 'nt':  # Windows
        data_dir = home / "AppData" / "Local" / "douglas"
    else:  # macOS and Linux
        data_dir = home / ".douglas"

    return data_dir


def find_databases_to_nuke():
    """Find all galaxies that have databases defined"""
    douglas_root = get_douglas_root()
    apps_dir = douglas_root / "apps"

    if not apps_dir.exists():
        print(f"📁 No apps directory found at {apps_dir}")
        return []

    databases_to_nuke = []
    galaxy_files = list(apps_dir.glob("*.yaml"))

    print(f"🔍 Scanning {len(galaxy_files)} galaxy files...")

    for galaxy_file in galaxy_files:
        galaxy_name = galaxy_file.stem

        try:
            with open(galaxy_file, 'r') as f:
                galaxy_config = yaml.safe_load(f)

            # Check if galaxy defines a database
            if 'database' in galaxy_config and 'models' in galaxy_config.get('database', {}):
                models = galaxy_config['database']['models']
                model_names = [model.get('name', 'Unknown') for model in models]

                databases_to_nuke.append({
                    'galaxy_name': galaxy_name,
                    'yaml_file': galaxy_file.name,
                    'models': model_names
                })

        except Exception as e:
            print(f"⚠️  Error reading {galaxy_file.name}: {e}")

    return databases_to_nuke


def show_nuke_preview(databases_to_nuke):
    """Show what will be deleted"""
    data_dir = get_douglas_data_dir()
    db_dir = data_dir / "databases"

    print()
    print("💥 NUCLEAR WARNING 💥")
    print("=" * 50)
    print("This will PERMANENTLY DELETE the following databases:")
    print()

    for db_info in databases_to_nuke:
        galaxy_name = db_info['galaxy_name']
        models = db_info['models']
        db_path = db_dir / f"{galaxy_name}.db"

        exists = "✅ EXISTS" if db_path.exists() else "❌ NOT FOUND"

        print(f"🗂️  {galaxy_name}.db ({exists})")
        print(f"   📄 From: {db_info['yaml_file']}")
        print(f"   📊 Tables: {', '.join(models)}")
        if db_path.exists():
            print(f"   📍 Path: {db_path}")
        print()

    print(f"📂 Database directory: {db_dir}")
    print()
    print("⚠️  This action CANNOT be undone!")
    print("⚠️  All your data will be lost!")
    print("⚠️  Douglas will recreate empty databases on next startup.")


def confirm_nuke():
    """Get user confirmation for the nuke operation"""
    print()
    print("🤔 Are you absolutely sure you want to nuke all databases?")
    print()

    while True:
        response = input("Type 'y' to DESTROY all data, or 'n' to cancel [N]: ").strip().lower()

        if response == '' or response == 'n' or response == 'no':
            print("✅ Operation cancelled. Your data is safe.")
            return False
        elif response == 'y' or response == 'yes':
            print("💥 Confirmed. Preparing for nuclear launch...")
            return True
        else:
            print("Please type 'y' for yes or 'n' for no (or press Enter for no)")


def execute_nuke(databases_to_nuke):
    """Execute the nuclear option"""
    data_dir = get_douglas_data_dir()
    db_dir = data_dir / "databases"

    nuked_count = 0

    print()
    print("💥 LAUNCHING NUKES...")
    print()

    for db_info in databases_to_nuke:
        galaxy_name = db_info['galaxy_name']
        db_path = db_dir / f"{galaxy_name}.db"

        if db_path.exists():
            try:
                db_path.unlink()  # Delete the file
                print(f"💥 NUKED: {galaxy_name}.db")
                nuked_count += 1
            except Exception as e:
                print(f"❌ FAILED to nuke {galaxy_name}.db: {e}")
        else:
            print(f"⚪ SKIP: {galaxy_name}.db (doesn't exist)")

    print()
    print("🌆 AFTERMATH:")
    print(f"💥 Databases nuked: {nuked_count}")
    print("🔄 Run 'douglas' to recreate empty databases")
    print("🌌 Don't panic - Douglas will rebuild everything!")


def main():
    """Main nuke script"""
    print("🚀 Douglas Database Nuke Script")
    print("⚠️  For development and testing only!")
    print()

    # Find all databases that would be nuked
    databases_to_nuke = find_databases_to_nuke()

    if not databases_to_nuke:
        print("📭 No databases found to nuke.")
        print("No galaxies have database configurations in their YAML files.")
        return

    # Show preview of what will be destroyed
    show_nuke_preview(databases_to_nuke)

    # Get confirmation
    if not confirm_nuke():
        return

    # Execute the nuke
    execute_nuke(databases_to_nuke)


if __name__ == "__main__":
    main()
