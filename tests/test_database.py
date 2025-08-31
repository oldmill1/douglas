#!/usr/bin/env python3
"""
Database layer tests for Douglas
"""
import unittest
import json
import shutil
from pathlib import Path
import sys

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import (
    save_entry_to_database,
    get_all_entries_from_database,
    count_entries_in_database,
    delete_entry_from_database,
    delete_multiple_entries_from_database,
    get_database_path,
    get_douglas_data_dir
)


class TestDatabaseLayer(unittest.TestCase):
    """Test database save/retrieve functionality"""

    def setUp(self):
        """Set up test environment"""
        # We'll use the actual food-logger galaxy for testing since it exists
        self.galaxy_name = "food-logger"
        self.test_data_dir = get_douglas_data_dir()

        # Track entries we create so we can clean them up
        self.created_entry_ids = []

        # Sample JSON data that matches food-logger format
        self.sample_entry = {
            "meal_name": "Test chicken and rice",
            "calories": 500,
            "protein": 45,
            "carbs": 30,
            "fats": 15,
            "notes": "Test meal for database"
        }
        self.sample_json = json.dumps(self.sample_entry)

    def tearDown(self):
        """Clean up test entries"""
        if self.created_entry_ids:
            deleted_count = delete_multiple_entries_from_database(self.galaxy_name, self.created_entry_ids)
            print(f"🧹 Cleaned up {deleted_count} test entries")

    def _track_entry(self, entry_id):
        """Helper to track entries for cleanup"""
        if entry_id and entry_id != False:
            self.created_entry_ids.append(entry_id)

    def test_save_and_retrieve_entry(self):
        """Test saving and retrieving a JSON entry"""
        print(f"Testing with galaxy: {self.galaxy_name}")
        print(f"Database path: {get_database_path(self.galaxy_name)}")

        # Save an entry
        entry_id = save_entry_to_database(self.galaxy_name, self.sample_json)
        self._track_entry(entry_id)

        # Should return a valid ID
        self.assertIsNotNone(entry_id, "save_entry_to_database should return an entry ID")
        self.assertNotEqual(entry_id, False, "save_entry_to_database should not return False")

        print(f"✅ Saved entry with ID: {entry_id}")

        # Retrieve all entries
        entries = get_all_entries_from_database(self.galaxy_name)

        # Should have at least our entry
        self.assertGreater(len(entries), 0, "Should have at least one entry")

        # Find our entry
        our_entry = None
        for entry in entries:
            if entry['id'] == entry_id:
                our_entry = entry
                break

        self.assertIsNotNone(our_entry, f"Should find our entry with ID {entry_id}")

        # Check the content matches
        self.assertEqual(our_entry['content'], self.sample_json, "Content should match what we saved")

        # Check parsed content
        self.assertIsNotNone(our_entry['parsed_content'], "Should have parsed JSON content")
        self.assertEqual(our_entry['parsed_content']['meal_name'], "Test chicken and rice")
        self.assertEqual(our_entry['parsed_content']['calories'], 500)

        print(f"✅ Retrieved entry: {our_entry['parsed_content']['meal_name']}")

    def test_count_entries(self):
        """Test counting entries in database"""
        # Get initial count
        initial_count = count_entries_in_database(self.galaxy_name)
        print(f"Initial entry count: {initial_count}")

        # Add an entry
        entry_id = save_entry_to_database(self.galaxy_name, self.sample_json)
        self._track_entry(entry_id)
        self.assertIsNotNone(entry_id, "Should be able to save entry")

        # Count should increase by 1
        new_count = count_entries_in_database(self.galaxy_name)
        self.assertEqual(new_count, initial_count + 1, "Count should increase by 1")

        print(f"✅ Count increased from {initial_count} to {new_count}")

    def test_multiple_entries(self):
        """Test saving multiple entries and retrieving them in order"""
        entries_to_save = [
            {"meal_name": "Test Breakfast", "calories": 300, "protein": 20, "carbs": 30, "fats": 10,
             "notes": "Morning meal"},
            {"meal_name": "Test Lunch", "calories": 600, "protein": 40, "carbs": 50, "fats": 20,
             "notes": "Midday meal"},
            {"meal_name": "Test Dinner", "calories": 800, "protein": 50, "carbs": 60, "fats": 30,
             "notes": "Evening meal"}
        ]

        saved_ids = []
        for entry_data in entries_to_save:
            entry_json = json.dumps(entry_data)
            entry_id = save_entry_to_database(self.galaxy_name, entry_json)
            self._track_entry(entry_id)
            self.assertIsNotNone(entry_id, f"Should save entry: {entry_data['meal_name']}")
            saved_ids.append(entry_id)

        print(f"✅ Saved {len(saved_ids)} entries with IDs: {saved_ids}")

        # Retrieve all entries
        all_entries = get_all_entries_from_database(self.galaxy_name)

        # Should have at least our 3 entries
        self.assertGreaterEqual(len(all_entries), 3, "Should have at least 3 entries")

        # Find our specific entries by ID (more reliable than assuming order)
        found_meals = []
        for entry in all_entries:
            if entry['id'] in saved_ids and entry['parsed_content']:
                found_meals.append(entry['parsed_content']['meal_name'])

        # Should find all our test meals
        self.assertEqual(len(found_meals), 3, f"Should find all 3 test meals, found: {found_meals}")
        self.assertIn("Test Breakfast", found_meals, "Should find Test Breakfast entry")
        self.assertIn("Test Lunch", found_meals, "Should find Test Lunch entry")
        self.assertIn("Test Dinner", found_meals, "Should find Test Dinner entry")

        print(f"✅ Found all test meals: {sorted(found_meals)}")

    def test_delete_functionality(self):
        """Test deleting entries"""
        # Save a test entry
        entry_id = save_entry_to_database(self.galaxy_name, self.sample_json)
        self.assertIsNotNone(entry_id, "Should be able to save entry")

        # Verify it exists
        entries = get_all_entries_from_database(self.galaxy_name)
        entry_exists = any(entry['id'] == entry_id for entry in entries)
        self.assertTrue(entry_exists, "Entry should exist in database")

        # Delete it
        deleted = delete_entry_from_database(self.galaxy_name, entry_id)
        self.assertTrue(deleted, "Should successfully delete entry")

        # Verify it's gone
        entries = get_all_entries_from_database(self.galaxy_name)
        entry_exists = any(entry['id'] == entry_id for entry in entries)
        self.assertFalse(entry_exists, "Entry should be deleted from database")

        print(f"✅ Successfully deleted entry {entry_id}")

        # Don't track this entry for cleanup since we already deleted it


if __name__ == "__main__":
    print("🧪 Testing Douglas Database Layer...")
    print()

    # Note: These tests will actually save to your real database
    # This is intentional so we can test with the real food-logger setup
    print("⚠️  Note: These tests will save entries to your actual food-logger database")
    print("   This is intentional to test with the real setup")
    print()

    unittest.main(verbosity=2)
