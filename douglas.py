#!/usr/bin/env python3
"""
Douglas - An AI-First App Runner & Builder
"""
import sys
import signal
import os
import yaml
from pathlib import Path
from database import get_douglas_data_dir, initialize_database
from galaxy import list_galaxies, load_galaxy, run_galaxy


def startup_boot_sequence():
    """Startup Boot Sequence - Initialize databases for all galaxies"""
    print("🚀 Running Startup Boot Sequence...")

    # Get apps directory
    douglas_root = get_douglas_root()
    apps_dir = douglas_root / "apps"

    if not apps_dir.exists():
        print(f"📁 No apps directory found at {apps_dir}")
        return

    # Process each Galaxy YAML file
    galaxy_files = list(apps_dir.glob("*.yaml"))
    databases_initialized = 0

    for galaxy_file in galaxy_files:
        galaxy_name = galaxy_file.stem

        try:
            with open(galaxy_file, 'r') as f:
                galaxy_config = yaml.safe_load(f)

            # Check if galaxy defines a database
            if 'database' in galaxy_config and 'models' in galaxy_config['database']:
                models = galaxy_config['database']['models']
                if initialize_database(galaxy_name, models):
                    databases_initialized += 1

        except Exception as e:
            print(f"⚠️  Error processing {galaxy_file.name}: {e}")

    if databases_initialized > 0:
        print(f"✅ SBS Complete: {databases_initialized} database(s) ready")
        data_dir = get_douglas_data_dir()
        print(f"📂 Database location: {data_dir / 'databases'}")
    else:
        print("✅ SBS Complete: No databases required")


def load_env_file():
    """Load environment variables from .env file"""
    douglas_root = get_douglas_root()
    env_file = douglas_root / ".env"

    if not env_file.exists():
        print("⚠️  No .env file found. Create one with your OPENAI_API_KEY")
        return

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🌌 Douglas signing off. Don't panic!")
    sys.exit(0)


def get_douglas_root():
    """Get the root directory where Douglas is installed"""
    # Get the directory where this script is located
    return Path(__file__).parent


def handle_command(command):
    """Process a Douglas command"""
    parts = command.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "run":
        if len(parts) < 2:
            print("❌ Usage: run <galaxy-name> [arguments...]")
            return
        galaxy_name = parts[1]
        # Join remaining parts as arguments for the galaxy
        galaxy_args = " ".join(parts[2:]) if len(parts) > 2 else ""
        run_galaxy(galaxy_name, galaxy_args)

    elif cmd == "list" or cmd == "ls":
        galaxies = list_galaxies()
        if galaxies:
            print("🌌 Available Galaxies:")
            for galaxy in sorted(galaxies):
                print(f"  • {galaxy}")
        else:
            print("📭 No galaxies found in apps/ directory")

    elif cmd == "env":
        # Debug command to check environment variables
        api_key = os.environ.get('OPENAI_API_KEY', 'Not set')
        model = os.environ.get('MODEL', 'Not set')
        print(f"🔑 OPENAI_API_KEY: {'✅ Set' if api_key != 'Not set' else '❌ Not set'}")
        print(f"🤖 MODEL: {model}")
        if api_key != 'Not set':
            print(f"🔍 Key preview: {api_key[:10]}...{api_key[-4:]}")

    elif cmd == "help":
        print("🤖 Douglas Commands:")
        print("  run <galaxy>  - Launch a galaxy")
        print("  list / ls     - List available galaxies")
        print("  help          - Show this help")
        print("  exit          - Exit Douglas")

    else:
        print(f"❓ Unknown command: {cmd}")
        print("💡 Type 'help' for available commands")


def main():
    """Main Douglas application loop"""
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Load environment variables
    load_env_file()

    # Run Startup Boot Sequence
    startup_boot_sequence()

    print()
    print("🌌 Welcome to Douglas!")
    print("   The AI-First App Runner & Builder")
    print("   Don't Panic - Your digital towel is ready.")
    print()
    print("💡 Type 'help' for commands or 'exit' to quit")

    try:
        while True:
            user_input = input("douglas> ").strip()

            if user_input.lower() == "exit":
                print("🌌 Thanks for using Douglas. Don't forget your towel!")
                break
            elif user_input == "":
                continue
            else:
                handle_command(user_input)

    except EOFError:
        # Handle Ctrl+D
        print("\n🌌 Douglas signing off. Don't panic!")


if __name__ == "__main__":
    main()
