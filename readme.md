# 🌌 Douglas - An AI-First App Runner & Builder

*Don't Panic - Your digital towel is ready.*

Douglas makes it easy to build and chain AI-powered workflows using your own
OpenAI API key.

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- OpenAI API key

### Installation

1. **Clone or download Douglas to your desired location:**
   ```bash
   mkdir -p ~/dev/douglas
   cd ~/dev/douglas
   # Add your douglas files here
   ```

2. **Set up your environment:**
   ```bash
   # Create .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "MODEL=gpt-4o" >> .env
   ```

3. **Install Douglas:**
   ```bash
   ./install.sh
   ```

4. **Start Douglas:**
   ```bash
   douglas
   ```

## 🌟 What are Galaxies?

**Galaxies** are self-contained AI applications defined by `.yaml` files. Each Galaxy can have:

- **🤖 One LLM**: Currently supports OpenAI's GPT-4o
- **🗄️ One Database**: JSON-based storage for custom data models
- **📝 A Prompt**: Core instructions for the AI
- **🔗 Chainability**: Output from one Galaxy can feed into another

## 📁 Project Structure

```
douglas/
├── douglas.py          # Main executable
├── install.sh         # Installation script
├── requirements.txt   # Python dependencies
├── .env              # Your API keys (create this)
└── apps/             # Galaxy definitions
    ├── hello-world.yaml
    ├── food-logger.yaml
    └── (your custom galaxies...)
```

## 🎮 Using Douglas

### Basic Commands

```bash
douglas> help              # Show available commands
douglas> list              # List all available galaxies  
douglas> run <galaxy>      # Execute a galaxy
douglas> env               # Check environment variables
douglas> exit              # Exit Douglas
```

### Running Galaxies

```bash
# Simple galaxy
douglas> run hello-world

# Galaxy with input
douglas> run food-logger "I ate a turkey sandwich for lunch"
```

## 📝 Creating Your Own Galaxies

### Simple Galaxy (Shell Command)

```yaml
# apps/my-galaxy.yaml
name: "My Custom Galaxy"
description: "Does something amazing"
action: "echo Hello from my galaxy!"
```

### AI-Powered Galaxy (LLM + Database)

```yaml
# apps/smart-galaxy.yaml
name: "Smart Galaxy"
description: "Uses AI to process data"

database:
  models:
    - name: "Entry"
      type: "json"

llm:
  useLLM: true
  provider: "openai"
  model: "gpt-4o"
  prompt: |
    You are a helpful assistant.
    Process this input: {{user_input}}

io:
  accepts: text
  returns: csv
```

## 🔧 Development Status

Douglas is currently in active development. Current features:

- ✅ Basic Galaxy system
- ✅ Shell command execution
- ✅ Environment variable loading
- ✅ YAML configuration parsing
- 🚧 LLM integration (in progress)
- 🚧 Database layer (in progress)
- 🚧 Galaxy chaining (planned)

## 🛠️ Development

### Adding Dependencies

Add to `requirements.txt`, then reinstall:

```bash
./install.sh
```

### Updating Douglas

After modifying `douglas.py`:

```bash
./install.sh  # Redeploy the updated version
```

### Uninstalling

```bash
sudo rm /usr/local/bin/douglas
```

## 📖 Examples

### Food Logger Galaxy

The included `food-logger` Galaxy demonstrates the full AI + Database workflow:

```bash
douglas> run food-logger "I had oatmeal with berries for breakfast"
# -> Processes with AI, stores in database, can generate CSV reports
```

## 🤝 Contributing

Douglas follows a step-by-step development approach:

1. Plan the feature
2. Implement max 2 files at a time
3. Test thoroughly
4. Move to next step

## 📚 Philosophy

Douglas embodies the principle that AI applications should be:

- **Composable**: Chain simple tools into complex workflows
- **Declarative**: Define what you want, not how to build it
- **Accessible**: Work from any terminal, anywhere
- **Fun**: Don't Panic - building AI tools should be enjoyable!

## 🌌 Hitchhiker's References

Douglas is named after Douglas Adams, creator of The Hitchhiker's Guide to the Galaxy. Throughout the codebase you'll
find references to towels, the number 42, and the phrase "Don't Panic" - because building AI applications shouldn't be
scary!

---

*Remember: The answer to life, the universe, and everything might be 42, but the answer to your AI automation needs is
Douglas.* 🌌