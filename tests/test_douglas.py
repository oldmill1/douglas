#!/usr/bin/env python3
"""
Integration tests for Douglas
"""
import unittest
import subprocess
import time
import threading
from pathlib import Path


class TestDouglasIntegration(unittest.TestCase):
    """Test the complete Douglas user workflow"""

    def setUp(self):
        """Set up test environment"""
        self.douglas_root = Path(__file__).parent.parent
        self.timeout = 10

    def test_full_workflow_simple(self):
        """Test Douglas with a simpler approach - script all commands at once"""

        # Create input script
        input_commands = "run food-logger\nhello test\nexit\nexit\n"

        # Run Douglas with input
        result = subprocess.run(
            ['python3', str(self.douglas_root / 'douglas.py')],
            input=input_commands,
            capture_output=True,
            text=True,
            timeout=15
        )

        output = result.stdout
        print("=== FULL OUTPUT ===")
        print(output)
        print("=== END OUTPUT ===")

        # Test all the key checkpoints
        self.assertIn("SBS Complete: 1 database(s) ready", output)
        self.assertIn("Welcome to Douglas!", output)
        self.assertIn("Launching Galaxy: food-logger", output)
        self.assertIn("Entering Food Logger interactive mode", output)
        self.assertIn("Hello! How can I help you?", output)
        self.assertIn("food-logger: hello test", output)
        self.assertIn("Exiting food-logger", output)
        self.assertIn("Thanks for using Douglas", output)

        print("✅ All workflow steps verified!")

    def test_startup_only(self):
        """Test just the startup sequence"""

        # Just start and immediately exit
        result = subprocess.run(
            ['python3', str(self.douglas_root / 'douglas.py')],
            input="exit\n",
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout
        print("=== STARTUP OUTPUT ===")
        print(output)
        print("=== END STARTUP ===")

        # Verify startup works
        self.assertIn("SBS Complete: 1 database(s) ready", output)
        self.assertIn("Welcome to Douglas!", output)
        self.assertIn("Thanks for using Douglas", output)

        print("✅ Startup sequence verified!")


if __name__ == "__main__":
    # Run the test
    unittest.main(verbosity=2)
