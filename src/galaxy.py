"""
Galaxy operations for Douglas
"""
import yaml
import subprocess
from pathlib import Path


def get_douglas_root():
    """Get the root directory where Douglas is installed"""
    # Get the directory where this script is located, then go up one level to find douglas.py
    current_dir = Path(__file__).parent  # This is src/
    return current_dir.parent  # This goes back to the Douglas root


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


def run_interactive_galaxy(galaxy_name, galaxy_config, initial_input=""):
    """Run a galaxy in interactive mode"""
    print(f"🌌 Entering {galaxy_config.get('name', galaxy_name)} interactive mode")
    print(f"💡 Type 'exit' to return to Douglas")
    print()

    # Display welcome message
    print(f"{galaxy_name}: Hello! How can I help you?")

    # If there was initial input, process it first
    if initial_input:
        print(f"{galaxy_name}> {initial_input}")
        print(f"{galaxy_name}: {initial_input}")  # Echo for now

    try:
        while True:
            user_input = input(f"{galaxy_name}> ").strip()

            if user_input.lower() == "exit":
                print(f"👋 Exiting {galaxy_name}")
                break
            elif user_input == "":
                continue
            else:
                # For now, just echo back the input
                # TODO: This is where we'll implement LLM processing
                print(f"{galaxy_name}: {user_input}")

    except EOFError:
        # Handle Ctrl+D
        print(f"\n👋 Exiting {galaxy_name}")
    except KeyboardInterrupt:
        # Handle Ctrl+C within the galaxy
        print(f"\n👋 Exiting {galaxy_name}")


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

    # Check if this is an interactive galaxy
    if galaxy_config.get('interactive', False):
        run_interactive_galaxy(galaxy_name, galaxy_config, galaxy_args)
        return

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
