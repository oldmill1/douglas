#!/bin/bash
# Install script for Douglas

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "🌌 Setting up Douglas..."

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

# Activate virtual environment and install dependencies
echo "📥 Installing dependencies..."
source "$SCRIPT_DIR/.venv/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"

# Create a wrapper script that activates the venv
WRAPPER_SCRIPT="$SCRIPT_DIR/douglas_wrapper.sh"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Douglas wrapper script - activates venv and runs douglas.py
DOUGLAS_DIR="$SCRIPT_DIR"
source "\$DOUGLAS_DIR/.venv/bin/activate"
python3 "\$DOUGLAS_DIR/douglas.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create symlink to the wrapper script
INSTALL_DIR="/usr/local/bin"
echo "🔗 Creating global command..."

# Check if /usr/local/bin exists, create if it doesn't
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating $INSTALL_DIR directory..."
    sudo mkdir -p "$INSTALL_DIR"
fi

# Remove existing symlink if it exists
if [ -L "$INSTALL_DIR/douglas" ]; then
    echo "Removing existing douglas command..."
    sudo rm "$INSTALL_DIR/douglas"
fi

# Create the symlink to the wrapper
sudo ln -s "$WRAPPER_SCRIPT" "$INSTALL_DIR/douglas"

echo "✅ Douglas installation complete!"
echo "🚀 You can now run 'douglas' from anywhere in your terminal."
echo ""
echo "To uninstall: sudo rm $INSTALL_DIR/douglas"