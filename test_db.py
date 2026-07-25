"""
Author: Adam Cottam
Purpose: CSE 310 Module 2 - Trail Log Tracker
"""
from pathlib import Path
import sqlite3
import tempfile
import pytest
from pytest import approx
from db import (
    create_database, get_connection, import_trails_from_csv,
    insert_park, insert_trail, insert_hike_log,
    get_all_parks, get_all_trails, get_trails_by_park, get_park_name,
    get_hike_history, get_trail_by_id, get_hike_log_by_id,
    update_trail, update_hike_log,
    delete_trail, delete_hike_log, get_hike_log_count_for_trail,
    get_hikes_per_park, get_hikes_per_trail, get_overall_stats,
)

# Test DB Path
TEST_DB_PATH = Path(__file__).parent / "test_trail_tracker.db"


def setup_module():
    """
    Set up test database with CSV data before tests run.
    Parameters: none
    Return: none
    """
    # Remove existing test DB
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # Create DB and import data
    create_database(TEST_DB_PATH)
    import_trails_from_csv(db_path=TEST_DB_PATH)


def teardown_module():
    """
    Remove test database after all tests complete.
    Parameters: none
    Return: none
    """
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_create_database():
    """
    Test Database Creation
    Parameters: none
    Return: none
    """
    assert TEST_DB_PATH.exists()


def test_foreign_keys_enabled():
    """
    Test that foreign key constraints are enabled.
    Parameters: none
    Return: none
    """
    conn = get_connection(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()[0]
    conn.close()
    assert result == 1


def test_import_trails_from_csv():
    """
    Test CSV Import loads parks and trails.
    Parameters: none
    Return: none
    """
    # DB Connection
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()

    # Check parks loaded
    cur.execute("SELECT COUNT(*) FROM parks")
    park_count = cur.fetchone()[0]

    # Check trails loaded
    cur.execute("SELECT COUNT(*) FROM trails")
    trail_count = cur.fetchone()[0]

    # Close Connection
    conn.close()

    # Verify data loaded
    assert park_count >= 50
    assert trail_count >= 3000


def test_insert_park():
    """
    Test Insert Park
    Parameters: none
    Return: none
    """
    park_id = insert_park("Test National Park", "TestState", "TestRegion", TEST_DB_PATH)
    assert park_id is not None
    assert isinstance(park_id, int)


def test_insert_trail():
    """
    Test Insert Trail
    Parameters: none
    Return: none
    """
    # Get a valid park_id
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]

    # Insert trail
    trail_id = insert_trail("Test Trail", park_id, 3.5, 500, "Moderate", TEST_DB_PATH)
    assert trail_id is not None
    assert isinstance(trail_id, int)


def test_insert_trail_invalid_park():
    """
    Test Insert Trail with invalid park ID fails gracefully.
    Parameters: none
    Return: none
    """
    trail_id = insert_trail("Bad Trail", 99999, 1.0, 100, "Easy", TEST_DB_PATH)
    assert trail_id is None


def test_insert_trail_invalid_difficulty():
    """
    Test Insert Trail with invalid difficulty fails gracefully.
    Parameters: none
    Return: none
    """
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]
    trail_id = insert_trail("Bad Trail", park_id, 1.0, 100, "Impossible", TEST_DB_PATH)
    assert trail_id is None


def test_insert_hike_log():
    """
    Test Insert Hike Log
    Parameters: none
    Return: none
    """
    # Get a valid trail_id
    trails = get_all_trails(TEST_DB_PATH)
    trail_id = trails[0]["trail_id"]

    # Insert hike log
    log_id = insert_hike_log(trail_id, "2026-07-24", 2.5, 4, "Great hike!", TEST_DB_PATH)
    assert log_id is not None
    assert isinstance(log_id, int)


def test_insert_hike_log_invalid_trail():
    """
    Test Insert Hike Log with invalid trail ID fails gracefully.
    Parameters: none
    Return: none
    """
    log_id = insert_hike_log(99999, "2026-07-24", 1.0, 3, "Bad", TEST_DB_PATH)
    assert log_id is None


def test_insert_hike_log_invalid_rating():
    """
    Test Insert Hike Log with invalid rating fails gracefully.
    Parameters: none
    Return: none
    """
    trails = get_all_trails(TEST_DB_PATH)
    trail_id = trails[0]["trail_id"]
    log_id = insert_hike_log(trail_id, "2026-07-24", 1.0, 6, "Bad rating", TEST_DB_PATH)
    assert log_id is None


def test_get_all_parks():
    """
    Test Get All Parks
    Parameters: none
    Return: none
    """
    parks = get_all_parks(TEST_DB_PATH)
    assert len(parks) >= 50
    assert "park_id" in parks[0]
    assert "park_name" in parks[0]
    assert "state" in parks[0]
    assert "region" in parks[0]


def test_get_all_trails():
    """
    Test Get All Trails (JOIN with parks)
    Parameters: none
    Return: none
    """
    trails = get_all_trails(TEST_DB_PATH)
    assert len(trails) >= 3000
    assert "trail_id" in trails[0]
    assert "trail_name" in trails[0]
    assert "park_name" in trails[0]  # Verifies JOIN


def test_get_trails_by_park():
    """
    Test Get Trails filtered by Park
    Parameters: none
    Return: none
    """
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]
    trails = get_trails_by_park(park_id, TEST_DB_PATH)
    assert len(trails) > 0
    assert "trail_name" in trails[0]


def test_get_park_name():
    """
    Test Get Park Name by ID
    Parameters: none
    Return: none
    """
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]
    name = get_park_name(park_id, TEST_DB_PATH)
    assert name is not None
    assert isinstance(name, str)


def test_get_park_name_invalid():
    """
    Test Get Park Name with invalid ID returns None.
    Parameters: none
    Return: none
    """
    name = get_park_name(99999, TEST_DB_PATH)
    assert name is None


def test_get_hike_history():
    """
    Test Get Hike History (JOIN across 3 tables)
    Parameters: none
    Return: none
    """
    hikes = get_hike_history(TEST_DB_PATH)
    assert len(hikes) >= 1
    assert "trail_name" in hikes[0]  # Verifies JOIN with trails
    assert "park_name" in hikes[0]   # Verifies JOIN with parks


def test_get_trail_by_id():
    """
    Test Get Trail by ID
    Parameters: none
    Return: none
    """
    trails = get_all_trails(TEST_DB_PATH)
    trail_id = trails[0]["trail_id"]
    trail = get_trail_by_id(trail_id, TEST_DB_PATH)
    assert trail is not None
    assert trail["trail_id"] == trail_id


def test_get_hike_log_by_id():
    """
    Test Get Hike Log by ID
    Parameters: none
    Return: none
    """
    hikes = get_hike_history(TEST_DB_PATH)
    log_id = hikes[0]["log_id"]
    log = get_hike_log_by_id(log_id, TEST_DB_PATH)
    assert log is not None
    assert log["log_id"] == log_id


def test_update_trail():
    """
    Test Update Trail
    Parameters: none
    Return: none
    """
    # Insert a trail to update
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]
    trail_id = insert_trail("Update Me Trail", park_id, 2.0, 300, "Easy", TEST_DB_PATH)

    # Update it
    result = update_trail(trail_id, "Updated Trail", 3.0, 400, "Moderate", TEST_DB_PATH)
    assert result is True

    # Verify update
    trail = get_trail_by_id(trail_id, TEST_DB_PATH)
    assert trail["trail_name"] == "Updated Trail"
    assert trail["distance_miles"] == 3.0
    assert trail["elevation_gain_ft"] == 400
    assert trail["difficulty"] == "Moderate"


def test_update_hike_log():
    """
    Test Update Hike Log
    Parameters: none
    Return: none
    """
    # Get an existing hike log
    hikes = get_hike_history(TEST_DB_PATH)
    log_id = hikes[0]["log_id"]

    # Update it
    result = update_hike_log(log_id, "2026-08-01", 3.0, 5, "Updated notes", TEST_DB_PATH)
    assert result is True

    # Verify update
    log = get_hike_log_by_id(log_id, TEST_DB_PATH)
    assert log["hike_date"] == "2026-08-01"
    assert log["duration_hours"] == 3.0
    assert log["rating"] == 5
    assert log["notes"] == "Updated notes"


def test_delete_hike_log():
    """
    Test Delete Hike Log
    Parameters: none
    Return: none
    """
    # Insert a hike log to delete
    trails = get_all_trails(TEST_DB_PATH)
    trail_id = trails[0]["trail_id"]
    log_id = insert_hike_log(trail_id, "2026-12-25", 1.0, 3, "Delete me", TEST_DB_PATH)

    # Delete it
    result = delete_hike_log(log_id, TEST_DB_PATH)
    assert result is True

    # Verify deletion
    log = get_hike_log_by_id(log_id, TEST_DB_PATH)
    assert log is None


def test_delete_trail():
    """
    Test Delete Trail (cascades hike logs)
    Parameters: none
    Return: none
    """
    # Insert a trail and hike log
    parks = get_all_parks(TEST_DB_PATH)
    park_id = parks[0]["park_id"]
    trail_id = insert_trail("Delete Me Trail", park_id, 1.0, 100, "Easy", TEST_DB_PATH)
    insert_hike_log(trail_id, "2026-12-25", 1.0, 3, "Will be deleted", TEST_DB_PATH)

    # Verify hike log exists
    count = get_hike_log_count_for_trail(trail_id, TEST_DB_PATH)
    assert count == 1

    # Delete trail (should cascade)
    result = delete_trail(trail_id, TEST_DB_PATH)
    assert result is True

    # Verify trail is gone
    trail = get_trail_by_id(trail_id, TEST_DB_PATH)
    assert trail is None

    # Verify hike log is also gone
    count = get_hike_log_count_for_trail(trail_id, TEST_DB_PATH)
    assert count == 0


def test_get_hikes_per_park():
    """
    Test Summary: Hikes per Park (JOIN + GROUP BY + COUNT + AVG)
    Parameters: none
    Return: none
    """
    stats = get_hikes_per_park(TEST_DB_PATH)
    assert len(stats) > 0
    assert "park_name" in stats[0]
    assert "total_hikes" in stats[0]
    assert "avg_rating" in stats[0]


def test_get_hikes_per_trail():
    """
    Test Summary: Hikes per Trail (JOIN + GROUP BY + HAVING)
    Parameters: none
    Return: none
    """
    stats = get_hikes_per_trail(TEST_DB_PATH)
    assert len(stats) > 0
    assert "trail_name" in stats[0]
    assert "park_name" in stats[0]
    assert "total_hikes" in stats[0]
    assert "avg_rating" in stats[0]
    assert "avg_duration" in stats[0]


def test_get_overall_stats():
    """
    Test Summary: Overall Statistics
    Parameters: none
    Return: none
    """
    stats = get_overall_stats(TEST_DB_PATH)
    assert stats["total_parks"] >= 50
    assert stats["total_trails"] >= 3000
    assert "total_hikes" in stats
    assert "total_hours" in stats


# Call the main function that is part of pytest so that the
# computer will execute the test functions in this file.
pytest.main(["-v", "--tb=line", "-rN", __file__])
