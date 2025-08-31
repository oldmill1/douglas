"""
Environment command for Douglas CLI
"""
import os


def handle_env_command(args):
    """Handle environment command"""
    api_key = os.environ.get('OPENAI_API_KEY', 'Not set')
    model = os.environ.get('MODEL', 'Not set')

    print(f"openai_api_key: {'set' if api_key != 'Not set' else 'not set'}")
    print(f"model: {model}")

    if api_key != 'Not set':
        print(f"key preview: {api_key[:10]}...{api_key[-4:]}")
