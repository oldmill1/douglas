"""
Galaxy operations for Douglas
"""
import os
import yaml
import json
import subprocess
from pathlib import Path

# Import OpenAI - we'll handle import errors gracefully
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Import our database functions
from src.database import save_entry_to_database


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


def call_openai_api(prompt, user_input, model="gpt-4o"):
    """Make a call to OpenAI API"""
    if OpenAI is None:
        return "❌ OpenAI library not installed. Run: pip install openai"

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return "❌ OPENAI_API_KEY not set in environment variables"

    try:
        client = OpenAI(api_key=api_key)

        # Replace {{user_input}} placeholder in the prompt
        formatted_prompt = prompt.replace('{{user_input}}', user_input)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": formatted_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ OpenAI API error: {str(e)}"


def should_save_to_database(galaxy_config):
    """Check if this galaxy should save LLM responses to database"""
    # Convention: if galaxy has LLM + database, auto-save responses
    has_llm = galaxy_config.get('llm', {}).get('useLLM', False)
    has_database = 'database' in galaxy_config and 'models' in galaxy_config.get('database', {})

    return has_llm and has_database


def try_save_response_to_database(galaxy_name, response_text):
    """Try to save LLM response to database if it's valid JSON"""
    try:
        # Try to parse as JSON first
        json.loads(response_text)  # This will raise JSONDecodeError if invalid

        # If we get here, it's valid JSON - save it
        entry_id = save_entry_to_database(galaxy_name, response_text)

        if entry_id and entry_id != False:
            print(f"✅ Entry saved to database (ID: {entry_id})")
            return True
        else:
            print("⚠️  Failed to save entry to database")
            return False

    except json.JSONDecodeError:
        # Not valid JSON, don't save (this is fine - not all responses need saving)
        return False
    except Exception as e:
        print(f"⚠️  Error saving to database: {e}")
        return False


def run_interactive_galaxy(galaxy_name, galaxy_config, initial_input=""):
    """Run a galaxy in interactive mode"""
    print(f"🌌 Entering {galaxy_config.get('name', galaxy_name)} interactive mode")
    print(f"💡 Type 'exit' to return to Douglas")
    print()

    # Check if this galaxy uses LLM
    use_llm = galaxy_config.get('llm', {}).get('useLLM', False)
    llm_prompt = galaxy_config.get('llm', {}).get('prompt', '')
    llm_model = galaxy_config.get('llm', {}).get('model', 'gpt-4o')

    # Check if we should auto-save responses to database
    auto_save = should_save_to_database(galaxy_config)

    if use_llm:
        if not llm_prompt:
            print(f"❌ Galaxy {galaxy_name} has useLLM=true but no prompt defined")
            return
        print(f"🤖 Using {llm_model} for responses")
        if auto_save:
            print(f"💾 Auto-saving responses to database")

    # Display welcome message
    print(f"{galaxy_name}: Hello! How can I help you?")

    # If there was initial input, process it first
    if initial_input:
        print(f"{galaxy_name}> {initial_input}")
        if use_llm:
            response = call_openai_api(llm_prompt, initial_input, llm_model)
            print(f"{galaxy_name}: {response}")

            # Try to save to database if configured
            if auto_save:
                try_save_response_to_database(galaxy_name, response)
        else:
            print(f"{galaxy_name}: {initial_input}")  # Echo for non-LLM galaxies

    try:
        while True:
            user_input = input(f"{galaxy_name}> ").strip()

            if user_input.lower() == "exit":
                print(f"👋 Exiting {galaxy_name}")
                break
            elif user_input == "":
                continue
            else:
                if use_llm:
                    response = call_openai_api(llm_prompt, user_input, llm_model)
                    print(f"{galaxy_name}: {response}")

                    # Try to save to database if configured
                    if auto_save:
                        try_save_response_to_database(galaxy_name, response)
                else:
                    # For non-LLM galaxies, just echo back the input
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
