"""
Help command for Douglas CLI
"""


def handle_help_command(args):
    """Handle help command"""
    print("commands:")
    print("  run <galaxy>  - launch a galaxy")
    print("  list          - list available galaxies")
    print("  db            - list databases")
    print("  env           - check environment variables")
    print("  help          - show this help")
    print("  exit          - exit douglas")
