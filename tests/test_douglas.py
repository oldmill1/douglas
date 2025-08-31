#!/usr/bin/env python3
"""
Integration tests for Douglas
"""
import subprocess
import unittest
import json
import re
from pathlib import Path


# Press `command + r` to run these tests in WebStorm

class TestDouglasIntegration(unittest.TestCase):
    """Test the complete Douglas user workflow"""

    def setUp(self):
        """Set up test environment"""
        self.douglas_root = Path(__file__).parent.parent
        self.timeout = 10

    def test_full_workflow_with_llm(self):
        """Test Douglas with LLM-based food-logger"""

        # Use a food description that should get a JSON response
        input_commands = "run food-logger\n1 cup of milk with three cookies\nexit\nexit\n"

        # Run Douglas with input (using --quiet flag)
        result = subprocess.run(
            ['python3', str(self.douglas_root / 'douglas.py'), '--quiet'],
            input=input_commands,
            capture_output=True,
            text=True,
            timeout=20  # Increased timeout for API calls
        )

        output = result.stdout

        # Test basic Douglas functionality (in quiet mode, many startup messages are suppressed)
        self.assertIn("douglas>", output)  # Should have the prompt
        self.assertIn("Launching Galaxy: food-logger", output)
        self.assertIn("Entering Food Logger interactive mode", output)
        self.assertIn("🤖 Using gpt-4o for responses", output)
        self.assertIn("Hello! How can I help you?", output)

        # Test that we got a non-empty LLM response (not an error)
        # Look for the food-logger response line
        food_logger_responses = [line for line in output.split('\n')
                                 if line.startswith('food-logger:') and len(line.strip()) > len('food-logger:')]

        self.assertGreater(len(food_logger_responses), 0, "Should have at least one food-logger response")

        # Get the actual response content (everything after "food-logger: ")
        response_content = food_logger_responses[0][len('food-logger: '):].strip()

        # Check that it's not an error message
        self.assertNotIn("❌", response_content, "Should not have error messages")
        self.assertNotIn("Error", response_content, "Should not have error messages")

        # Check that we got some substantive response (more than 10 characters)
        self.assertGreater(len(response_content), 10,
                           f"Response should be substantive, got: '{response_content}'")

        # If it looks like JSON, try to parse it
        if response_content.startswith('{') and response_content.endswith('}'):
            try:
                parsed_json = json.loads(response_content)
                # Check that it has expected macro fields
                expected_fields = ['calories', 'protein', 'carbs', 'fats']
                for field in expected_fields:
                    self.assertIn(field, parsed_json, f"JSON should contain {field}")
                print("✅ Valid JSON response with expected macro fields!")
            except json.JSONDecodeError:
                # If JSON parsing fails, just check it's a reasonable response
                print("⚠️ Response wasn't valid JSON, but checking for reasonable content")

        # Test clean exit
        self.assertIn("Exiting food-logger", output)
        # Note: In quiet mode, the final "Thanks for using Douglas" message is suppressed

        print("✅ LLM workflow test completed!")

    def test_startup_only(self):
        """Test just the startup sequence"""

        # Just start and immediately exit (using --quiet flag)
        result = subprocess.run(
            ['python3', str(self.douglas_root / 'douglas.py'), '--quiet'],
            input="exit\n",
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout

        # Verify startup works (in quiet mode, most startup messages are suppressed)
        self.assertIn("douglas>", output)  # Should at least have the prompt
        # Note: SBS and Welcome messages are suppressed in quiet mode

        print("✅ Startup sequence verified!")

    def test_non_llm_galaxy(self):
        """Test that non-LLM galaxies still work (hello-world)"""

        input_commands = "run hello-world\nexit\n"

        result = subprocess.run(
            ['python3', str(self.douglas_root / 'douglas.py'), '--quiet'],
            input=input_commands,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout

        # Test that hello-world still works (in quiet mode)
        self.assertIn("douglas>", output)  # Should have the prompt
        self.assertIn("Launching Galaxy: hello-world", output)
        self.assertIn("Hello, World!", output)

        print("✅ Non-LLM galaxy test completed!")


if __name__ == "__main__":
    # Run the test
    unittest.main(verbosity=2)
