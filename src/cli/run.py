"""
Run command for Douglas CLI
"""
from ..galaxy import run_galaxy


def handle_run_command(args):
    """Handle run command"""
    if len(args) < 1:
        print("usage: run <galaxy-name> [arguments...]")
        return

    galaxy_name = args[0]
    # Join remaining args as arguments for the galaxy
    galaxy_args = " ".join(args[1:]) if len(args) > 1 else ""
    run_galaxy(galaxy_name, galaxy_args)
