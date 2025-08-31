"""
List command for Douglas CLI
"""
from ..galaxy import list_galaxies


def handle_list_command(args):
    """Handle list command"""
    galaxies = list_galaxies()
    if galaxies:
        for galaxy in sorted(galaxies):
            print(f"  {galaxy}")
    else:
        print("no galaxies found in apps/ directory")
