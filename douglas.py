#!/usr/bin/env python3
"""
Douglas - An AI-First App Runner & Builder
"""
import sys
import signal
import os
import yaml
import subprocess
from pathlib import Path


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


def list_galaxies():
    """List all available Galaxy YAML files"""
    douglas_root = get_douglas_root()
    apps_dir = douglas_root / "apps"

    if not apps_dir.exists():
        print(f"📁 Apps directory not found: {apps_dir}")
        return []

    galaxy_files = list(apps_dir.glob("*.yaml"))
    return [f.stem for f in galaxy_files]  # Return without .yaml extension


def load_galaxy(galaxy_name):
    """Load and parse a Galaxy YAML file"""
    douglas_root = get_douglas_root()
    galaxy_path = douglas_root / "apps" / f"{galaxy_name}.yaml"

    if not galaxy_path.exists():
        return None

    try:
        with open(galaxy_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {galaxy_name}.yaml: {e}")
        return None


def run_galaxy(galaxy_name, galaxy_args=""):
    """Execute a Galaxy"""
    print(f"🚀 Launching Galaxy: {galaxy_name}")
    if galaxy_args:
        print(f"📨 Input: {galaxy_args}")

    galaxy_config = load_galaxy(galaxy_name)
    if not galaxy_config:
        print(f"❌ Galaxy '{galaxy_name}' not found or invalid")
        return

    # Display galaxy info
    if 'description' in galaxy_config:
        print(f"📝 {galaxy_config['description']}")

    # Execute the action (for simple galaxies like hello-world)
    if 'action' in galaxy_config:
        try:
            result = subprocess.run(
                galaxy_config['action'],
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout:
                print(result.stdout.strip())
            if result.stderr:
                print(f"⚠️  {result.stderr.strip()}")

        except Exception as e:
            print(f"❌ Error executing galaxy: {e}")

    # For LLM-based galaxies (like food-logger)
    elif 'llm' in galaxy_config:
        print("🤖 LLM-based galaxy detected (not implemented yet)")
        print(f"📋 Would process: {galaxy_args}")

    else:
        print("❌ No action or LLM configuration found in galaxy")


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
