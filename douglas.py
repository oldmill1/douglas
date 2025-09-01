#!/usr/bin/env python3
"""
Douglas - An AI-First App Runner & Builder
"""
import sys
import signal
import os
import yaml
import time
import threading
from pathlib import Path
from src.database import get_douglas_data_dir, initialize_database
from src.cli import handle_command

# Import readline for command history and line editing
try:
    import readline

    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


def setup_readline():
    """Setup readline for command history and line editing"""
    if not READLINE_AVAILABLE:
        return

    # Set up history file
    douglas_data_dir = get_douglas_data_dir()
    history_file = douglas_data_dir / "command_history"

    # Create data directory if it doesn't exist
    douglas_data_dir.mkdir(parents=True, exist_ok=True)

    # Load existing history
    if history_file.exists():
        try:
            readline.read_history_file(str(history_file))
        except Exception:
            pass  # Ignore errors loading history

    # Set history length
    readline.set_history_length(1000)

    # Set up tab completion for Douglas commands
    def douglas_completer(text, state):
        """Tab completion for Douglas commands"""
        commands = ['run', 'browse', 'list', 'db', 'env', 'help', 'exit']
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        try:
            return matches[state]
        except IndexError:
            return None

    readline.set_completer(douglas_completer)
    readline.parse_and_bind('tab: complete')

    return history_file


def save_readline_history(history_file):
    """Save command history when exiting"""
    if READLINE_AVAILABLE and history_file:
        try:
            readline.write_history_file(str(history_file))
        except Exception:
            pass  # Ignore errors saving history


class SaucerAnimation:
    """Terminal animation for database initialization"""

    def __init__(self):
        self.running = False
        self.thread = None
        self.databases_to_init = []
        self.databases_completed = 0

    def start(self, database_count):
        """Start the saucer animation"""
        if database_count == 0:
            return

        self.databases_to_init = ['🛸', '🛸'] if database_count >= 2 else ['🛸']
        self.databases_completed = 0
        self.running = True

        # Hide cursor and display initial saucers
        print('\033[?25l', end='', flush=True)  # Hide cursor
        print(' '.join(self.databases_to_init), end='', flush=True)

        # Start animation thread
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def _animate(self):
        """Animation loop - alternates between saucer and alien"""
        animation_cycle = 0
        while self.running:
            time.sleep(0.5)
            if not self.running:
                break

            # Move cursor back to start of line
            print(f'\r', end='', flush=True)

            # Create animated display
            display = []
            for i in range(len(self.databases_to_init)):
                if i < self.databases_completed:
                    display.append('  ')  # Completed databases are invisible
                else:
                    # Animate between saucer and alien
                    if animation_cycle % 2 == 0:
                        display.append('🛸')
                    else:
                        display.append('👽')

            print(' '.join(display), end='', flush=True)
            animation_cycle += 1

    def complete_database(self):
        """Mark one database as completed"""
        self.databases_completed += 1
        if self.databases_completed >= len(self.databases_to_init):
            self.stop()

    def stop(self):
        """Stop the animation and clear the display"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

        # Clear the line and show cursor
        print(f'\r{" " * 10}\r', end='', flush=True)  # Clear the line
        print('\033[?25h', end='', flush=True)  # Show cursor


def startup_boot_sequence():
    """Startup Boot Sequence - Initialize databases for all galaxies with animation"""

    # Get apps directory
    douglas_root = get_douglas_root()
    apps_dir = douglas_root / "apps"

    if not apps_dir.exists():
        return

    # Process each Galaxy YAML file to count databases needed
    galaxy_files = list(apps_dir.glob("*.yaml"))
    databases_needed = []

    for galaxy_file in galaxy_files:
        galaxy_name = galaxy_file.stem
        try:
            with open(galaxy_file, 'r') as f:
                galaxy_config = yaml.safe_load(f)

            # Check if galaxy defines a database
            if 'database' in galaxy_config and 'models' in galaxy_config['database']:
                models = galaxy_config['database']['models']
                databases_needed.append((galaxy_name, models))
        except Exception:
            continue  # Silently skip problematic files

    if not databases_needed:
        return

    # Start saucer animation
    animation = SaucerAnimation()
    animation.start(len(databases_needed))

    # Initialize databases
    for galaxy_name, models in databases_needed:
        try:
            if initialize_database(galaxy_name, models):
                animation.complete_database()
                time.sleep(0.3)  # Brief pause between completions
        except Exception:
            animation.complete_database()  # Complete even on error

    # Ensure animation is stopped
    animation.stop()


def load_env_file():
    """Load environment variables from .env file"""
    douglas_root = get_douglas_root()
    env_file = douglas_root / ".env"

    if not env_file.exists():
        return

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except Exception:
        pass  # Silently handle env file errors


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🌌 Douglas signing off. Don't panic!")
    sys.exit(0)


def get_douglas_root():
    """Get the root directory where Douglas is installed"""
    # Get the directory where this script is located
    return Path(__file__).parent


def main():
    """Main Douglas application loop"""

    # ANSI color code for pastel purple (#BB7CD8)
    PASTEL_PURPLE = '\033[38;2;187;124;216m'
    RESET_COLOR = '\033[0m'

    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Load environment variables
    load_env_file()

    # Set up readline for command history and tab completion
    history_file = setup_readline()

    # Run Startup Boot Sequence with animation
    startup_boot_sequence()

    try:
        while True:
            try:
                user_input = input(f"{PASTEL_PURPLE}$d>{RESET_COLOR} ").strip()
            except EOFError:
                # Handle Ctrl+D - exit silently
                break

            if user_input.lower() == "exit":
                # Exit silently without message
                break
            elif user_input == "":
                continue
            else:
                handle_command(user_input)

    except KeyboardInterrupt:
        # Handle Ctrl+C
        print("\n🌌 Douglas signing off. Don't panic!")
    finally:
        # Save command history
        save_readline_history(history_file)


if __name__ == "__main__":
    main()
