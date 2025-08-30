#!/bin/bash
# Install script for Douglas

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create a symlink to make douglas globally accessible
# We'll put it in /usr/local/bin (which should be in your PATH)
INSTALL_DIR="/usr/local/bin"
DOUGLAS_SCRIPT="$SCRIPT_DIR/douglas.py"

echo "Installing Douglas..."
echo "Script location: $DOUGLAS_SCRIPT"
echo "Installing to: $INSTALL_DIR/douglas"

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

# Create the symlink
echo "Creating symlink..."
sudo ln -s "$DOUGLAS_SCRIPT" "$INSTALL_DIR/douglas"

# Make sure the script is executable
chmod +x "$DOUGLAS_SCRIPT"

echo "Installation complete!"
echo "You can now run 'douglas' from anywhere in your terminal."
echo ""
echo "To uninstall, run: sudo rm $INSTALL_DIR/douglas"