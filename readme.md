# Douglas - AI App Runner

Build AI applications with YAML files. Each app gets its own database and can use GPT-4o.

## Quick Start

```bash
git clone <repo>
cd douglas
echo "OPENAI_API_KEY=your_key_here" > .env
./scripts/install.sh
douglas
```

## What It Does

Douglas runs "Galaxies" - AI applications defined in YAML files. Each galaxy can:

- Execute shell commands
- Call OpenAI GPT-4o
- Store data in SQLite
- Run interactively

## Example: Food Tracker

Create `apps/food-tracker.yaml`:

```yaml
name: "Food Tracker"
description: "Track calories and macros"
interactive: true

database:
  models:
    - name: "Entry"
      type: "json"

llm:
  useLLM: true
  provider: "openai"
  model: "gpt-4o"
  prompt: |
    Break down this food into calories, protein, carbs, and fats.
    Return JSON: {"calories": 450, "protein": 35, "carbs": 25, "fats": 18}

    Food: {{user_input}}
```

Run it:

```bash
douglas> run food-tracker
food-tracker> chicken breast 200g
food-tracker: {"calories": 330, "protein": 62, "carbs": 0, "fats": 7}
✅ Entry saved to database (ID: 1)
```

## Database Integration

Douglas automatically saves JSON responses to SQLite:

```bash
# Check your data
sqlite3 ~/.douglas/databases/food-tracker.db
sqlite> SELECT * FROM entry ORDER BY created_at DESC LIMIT 3;

id|created_at|content
3|2025-01-15 10:30:45|{"calories": 330, "protein": 62, "carbs": 0, "fats": 7}
2|2025-01-15 09:15:22|{"calories": 520, "protein": 45, "carbs": 35, "fats": 18}
1|2025-01-15 08:45:10|{"calories": 280, "protein": 25, "carbs": 40, "fats": 8}
```

Query your data:

```sql
-- Total calories today
SELECT SUM(json_extract(content, '$.calories')) as total_calories
FROM entry
WHERE date (created_at) = date ('now');

-- High protein meals
SELECT json_extract(content, '$.protein') as protein,
       datetime(created_at) as time
FROM entry
WHERE json_extract(content, '$.protein') > 40;
```

## Simple Galaxy (No AI)

```yaml
name: "System Info"
description: "Show system information"
action: "uname -a && df -h"
```

```bash
douglas> run system-info
Linux hostname 5.4.0 x86_64
Filesystem  Size  Used Avail Use% Mounted on
/dev/sda1   20G   8.5G  11G  45% /
```

## Commands

```bash
douglas> list          # Show all galaxies
douglas> run <galaxy>  # Execute a galaxy
douglas> env           # Check API keys
douglas> help          # Show commands
douglas> exit          # Exit
```

## File Structure

```
douglas/
├── apps/              # Your galaxy definitions
│   ├── food-tracker.yaml
│   └── system-info.yaml
├── ~/.douglas/databases/  # SQLite databases (auto-created)
├── douglas.py         # Main program
└── .env              # Your API keys
```

## Requirements

- Python 3.6+
- OpenAI API key (for LLM galaxies)

## Architecture

Each galaxy with a database gets:

- SQLite database at `~/.douglas/databases/galaxy-name.db`
- Auto-created tables based on YAML models
- JSON responses automatically saved
- Full SQL query access to your data

No configuration needed. Define your app in YAML, Douglas handles the rest.

## Development

```bash
# Reset all databases
python3 scripts/nuke_databases.py

# Run tests
python3 tests/test_douglas.py
python3 tests/test_database.py
```

---

Simple. Powerful. Works.