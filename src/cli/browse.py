"""
Browse command for Douglas CLI - Interactive database browser
"""
import sys
import termios
import tty

from ..database import get_all_entries_from_database, delete_multiple_entries_from_database
from ..galaxy import load_galaxy


def handle_browse_command(args):
    """Handle browse command - interactive database browser"""
    if len(args) < 1:
        print("usage: browse <galaxy-name>")
        return

    galaxy_name = args[0]

    # Check if galaxy exists and has a database
    galaxy_config = load_galaxy(galaxy_name)
    if not galaxy_config:
        print(f"❌ Galaxy '{galaxy_name}' not found")
        return

    if 'database' not in galaxy_config or 'models' not in galaxy_config.get('database', {}):
        print(f"❌ Galaxy '{galaxy_name}' has no database configured")
        return

    # Launch the interactive browser
    launch_database_browser(galaxy_name)


def launch_database_browser(galaxy_name):
    """Launch interactive database browser interface"""
    print(f"🗄️  Browsing {galaxy_name} database")
    print("🔍 Loading entries...")

    # Get all entries
    entries = get_all_entries_from_database(galaxy_name)

    if not entries:
        print("📭 No entries found in database")
        return

    print(f"📊 Found {len(entries)} entries")
    print()
    print("🎯 Interactive Database Browser")
    print("   Use ↑/↓ arrows to navigate")
    print("   Press SPACE to select/deselect entries")
    print("   Press 'd' to delete selected entries")
    print("   Press 'q' to quit")
    print()
    input("Press Enter to start...")

    # Launch cursor-based browser
    run_cursor_browser(galaxy_name, entries)


def run_cursor_browser(galaxy_name, entries):
    """Cursor-based browser interface with arrow key navigation"""
    cursor_pos = 0
    selected_indices = set()
    page_size = 10
    current_page = 0

    def get_current_entries():
        start = current_page * page_size
        end = start + page_size
        return entries[start:end], start

    def draw_interface():
        """Draw the current state of the interface"""
        print("\033[2J\033[H")  # Clear screen and move cursor to top

        current_entries, offset = get_current_entries()

        print(f"◆ {galaxy_name} Database Browser")
        print(f"│ Page {current_page + 1} of {(len(entries) - 1) // page_size + 1} | {len(selected_indices)} selected")
        print("│")

        for i, entry in enumerate(current_entries):
            actual_index = offset + i
            is_cursor = (i == cursor_pos)
            is_selected = actual_index in selected_indices

            # Choose markers
            if is_selected:
                marker = "●"
            else:
                marker = "○"

            # Choose prefix
            if is_cursor:
                prefix = "│ >"
            else:
                prefix = "│  "

            display_name = get_entry_display_name(entry)

            if is_cursor:
                # Highlight current line
                print(f"{prefix} {marker} {display_name}")
            else:
                print(f"{prefix} {marker} {display_name}")

        print("│")
        if len(selected_indices) > 0:
            print(f"│ Press 'd' to delete {len(selected_indices)} selected entries")
        print("│ Press 'q' to quit")

    def getch():
        """Get a single character from stdin"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC sequence
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # Main interaction loop
    try:
        while True:
            current_entries, offset = get_current_entries()
            draw_interface()

            key = getch()

            if key == 'q':
                break
            elif key == '\x1b[A':  # Up arrow
                cursor_pos = max(0, cursor_pos - 1)
                if cursor_pos < 0 and current_page > 0:
                    current_page -= 1
                    cursor_pos = min(page_size - 1, len(entries) - current_page * page_size - 1)
            elif key == '\x1b[B':  # Down arrow
                cursor_pos = min(len(current_entries) - 1, cursor_pos + 1)
                if cursor_pos >= len(current_entries) and (current_page + 1) * page_size < len(entries):
                    current_page += 1
                    cursor_pos = 0
            elif key == ' ':  # Space - toggle selection
                actual_index = offset + cursor_pos
                if actual_index in selected_indices:
                    selected_indices.remove(actual_index)
                else:
                    selected_indices.add(actual_index)
            elif key == 'd':  # Delete selected
                if selected_indices:
                    # Clear screen for confirmation
                    print("\033[2J\033[H")
                    confirm_and_delete(galaxy_name, entries, selected_indices)
                    # Refresh entries after deletion
                    entries = get_all_entries_from_database(galaxy_name)
                    selected_indices.clear()
                    cursor_pos = 0
                    current_page = 0
                    if not entries:
                        print("📭 All entries deleted!")
                        input("Press Enter to continue...")
                        break
                    input("Press Enter to continue...")

    except KeyboardInterrupt:
        print("\n👋 Exiting database browser")
    finally:
        print("\033[2J\033[H")  # Clear screen when exiting


def confirm_and_delete(galaxy_name, entries, selected_indices):
    """Show confirmation dialog and delete selected entries"""
    selected_entries = [entries[i] for i in selected_indices if i < len(entries)]

    print(f"🗑️  Delete {len(selected_entries)} entries?")
    print()
    for entry in selected_entries:
        display_name = get_entry_display_name(entry)
        print(f"  • {display_name}")

    print()
    confirm = input("Are you sure? [y/N]: ").strip().lower()

    if confirm in ['y', 'yes']:
        entry_ids = [entry['id'] for entry in selected_entries]
        deleted_count = delete_multiple_entries_from_database(galaxy_name, entry_ids)
        print(f"✅ Deleted {deleted_count} entries")
    else:
        print("❌ Deletion cancelled")


def get_entry_display_name(entry):
    """Extract a display name from a database entry"""
    if entry['parsed_content']:
        # For food-logger, use meal_name
        if 'meal_name' in entry['parsed_content']:
            calories = entry['parsed_content'].get('calories', '?')
            return f'"{entry["parsed_content"]["meal_name"]}" ({calories} cal)'

        # Generic fallback - try common name fields
        for name_field in ['name', 'title', 'description']:
            if name_field in entry['parsed_content']:
                return f'"{entry["parsed_content"][name_field]}"'

    # Ultimate fallback - show entry ID and date
    created_date = entry['created_at'][:10] if entry['created_at'] else 'unknown'
    return f"Entry #{entry['id']} ({created_date})"


def delete_selected_entries(galaxy_name, entries, selected_indices):
    """Delete the selected entries with confirmation (deprecated - use confirm_and_delete)"""
    selected_entries = [entries[i] for i in selected_indices if i < len(entries)]

    print(f"\n🗑️  About to delete {len(selected_entries)} entries:")
    for entry in selected_entries:
        display_name = get_entry_display_name(entry)
        print(f"   • {display_name}")

    print()
    confirm = input("Are you sure? [y/N]: ").strip().lower()

    if confirm in ['y', 'yes']:
        entry_ids = [entry['id'] for entry in selected_entries]
        deleted_count = delete_multiple_entries_from_database(galaxy_name, entry_ids)
        print(f"✅ Deleted {deleted_count} entries")
    else:
        print("❌ Deletion cancelled")

    input("Press Enter to continue...")
