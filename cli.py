"""
CLI operations for Douglas
"""
import os
from galaxy import list_galaxies, run_galaxy


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
