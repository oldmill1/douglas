"""
CLI operations for Douglas - Main handler
"""
import os
from .db import handle_db_command
from .run import handle_run_command
from .list import handle_list_command
from .env import handle_env_command
from .help import handle_help_command


def handle_command(command):
    """Process a Douglas command"""
    parts = command.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []

    if cmd == "run":
        handle_run_command(args)
    elif cmd == "list" or cmd == "ls":
        handle_list_command(args)
    elif cmd == "db":
        handle_db_command(args)
    elif cmd == "env":
        handle_env_command(args)
    elif cmd == "help":
        handle_help_command(args)
    else:
        print(f"unknown command: {cmd}")
        print("type 'help' for available commands")
