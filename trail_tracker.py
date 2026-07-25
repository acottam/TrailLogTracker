"""
Trail Log Tracker
A command-line application for logging family hikes and adventures
across national parks and trails.

CSE 310 - Module 2: SQL Relational Databases
Author: Adam Cottam
Date: July 2026
"""

import sqlite3
import os
from datetime import date


# --- Database Connection ---

DB_FILE = "trail_tracker.db"


def get_connection():
    """Create and return a database connection with foreign key enforcement."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --- Table Creation ---

def create_tables(conn):
    """Create the parks, trails, and hike_logs tables if they don't exist."""
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parks (
            park_id INTEGER PRIMARY KEY AUTOINCREMENT,
            park_name TEXT NOT NULL,
            state TEXT NOT NULL,
            region TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trails (
            trail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trail_name TEXT NOT NULL,
            park_id INTEGER NOT NULL,
            distance_miles REAL NOT NULL,
            elevation_gain_ft INTEGER NOT NULL,
            difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy', 'Moderate', 'Hard', 'Expert')),
            FOREIGN KEY (park_id) REFERENCES parks(park_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hike_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            trail_id INTEGER NOT NULL,
            hike_date TEXT NOT NULL,
            duration_hours REAL NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            notes TEXT,
            FOREIGN KEY (trail_id) REFERENCES trails(trail_id)
        )
    """)

    conn.commit()
    print("Database tables created successfully.")


# --- Seed Data ---

def seed_data(conn):
    """Insert sample parks, trails, and hike logs if tables are empty."""
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM parks")
    if cursor.fetchone()[0] > 0:
        print("Database already contains data. Skipping seed.")
        return

    # Sample parks
    parks = [
        ("Zion National Park", "Utah", "Southwest"),
        ("Yellowstone National Park", "Wyoming", "Northwest"),
        ("Grand Canyon National Park", "Arizona", "Southwest"),
        ("Glacier National Park", "Montana", "Northwest"),
        ("Bryce Canyon National Park", "Utah", "Southwest"),
    ]
    cursor.executemany(
        "INSERT INTO parks (park_name, state, region) VALUES (?, ?, ?)",
        parks
    )

    # Sample trails
    trails = [
        ("Angels Landing", 1, 5.4, 1488, "Hard"),
        ("The Narrows", 1, 9.4, 334, "Moderate"),
        ("Emerald Pools", 1, 3.0, 350, "Easy"),
        ("Old Faithful Geyser Trail", 2, 1.5, 50, "Easy"),
        ("Grand Prismatic Overlook", 2, 1.6, 180, "Easy"),
        ("Bright Angel Trail", 3, 12.0, 4380, "Expert"),
        ("South Kaibab Trail", 3, 6.3, 2040, "Hard"),
        ("Highline Trail", 4, 11.8, 890, "Moderate"),
        ("Grinnell Glacier Trail", 4, 10.6, 1840, "Hard"),
        ("Navajo Loop Trail", 5, 1.3, 550, "Moderate"),
    ]
    cursor.executemany(
        "INSERT INTO trails (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty) VALUES (?, ?, ?, ?, ?)",
        trails
    )

    # Sample hike logs
    hike_logs = [
        (1, "2026-03-15", 4.5, 5, "Incredible views from the top. Chains were intense!"),
        (2, "2026-03-16", 6.0, 4, "Water was cold but beautiful canyon walls."),
        (3, "2026-03-16", 1.5, 3, "Nice short hike, good for the kids."),
        (4, "2026-06-10", 0.5, 4, "Old Faithful erupted right on time."),
        (5, "2026-06-10", 0.75, 5, "The colors were unbelievable from above."),
        (6, "2026-04-20", 8.0, 5, "Made it to Indian Garden. Tough but rewarding."),
        (8, "2026-07-01", 5.5, 4, "Wildflowers everywhere. Some snow on trail."),
        (9, "2026-07-02", 6.0, 5, "Glacier views were stunning. Long but worth it."),
        (10, "2026-05-18", 1.0, 4, "Hoodoos are amazing. Short but steep."),
        (1, "2026-06-20", 5.0, 5, "Second time up. Less scary, still amazing."),
    ]
    cursor.executemany(
        "INSERT INTO hike_logs (trail_id, hike_date, duration_hours, rating, notes) VALUES (?, ?, ?, ?, ?)",
        hike_logs
    )

    conn.commit()
    print("Sample data seeded successfully.")


# --- INSERT Functions ---

def add_park(conn):
    """Add a new park to the database."""
    print("\n--- Add New Park ---")
    park_name = input("Park name: ").strip()
    state = input("State: ").strip()
    region = input("Region (e.g., Southwest, Northwest, Southeast): ").strip()

    if not park_name or not state or not region:
        print("Error: All fields are required.")
        return

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO parks (park_name, state, region) VALUES (?, ?, ?)",
        (park_name, state, region)
    )
    conn.commit()
    print(f"Park '{park_name}' added successfully (ID: {cursor.lastrowid}).")


def add_trail(conn):
    """Add a new trail to the database."""
    print("\n--- Add New Trail ---")

    # Show available parks
    list_parks(conn)

    try:
        park_id = int(input("\nPark ID to add trail to: "))
    except ValueError:
        print("Error: Invalid park ID.")
        return

    trail_name = input("Trail name: ").strip()

    try:
        distance = float(input("Distance (miles): "))
        elevation = int(input("Elevation gain (ft): "))
    except ValueError:
        print("Error: Distance must be a number, elevation must be an integer.")
        return

    print("Difficulty options: Easy, Moderate, Hard, Expert")
    difficulty = input("Difficulty: ").strip().capitalize()
    if difficulty not in ("Easy", "Moderate", "Hard", "Expert"):
        print("Error: Invalid difficulty level.")
        return

    if not trail_name:
        print("Error: Trail name is required.")
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO trails (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty) VALUES (?, ?, ?, ?, ?)",
            (trail_name, park_id, distance, elevation, difficulty)
        )
        conn.commit()
        print(f"Trail '{trail_name}' added successfully (ID: {cursor.lastrowid}).")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}. Make sure the park ID exists.")


def add_hike_log(conn):
    """Add a new hike log entry."""
    print("\n--- Log a Hike ---")

    # Show available trails
    list_all_trails(conn)

    try:
        trail_id = int(input("\nTrail ID: "))
    except ValueError:
        print("Error: Invalid trail ID.")
        return

    hike_date = input(f"Date (YYYY-MM-DD) [default: {date.today()}]: ").strip()
    if not hike_date:
        hike_date = str(date.today())

    try:
        duration = float(input("Duration (hours): "))
        rating = int(input("Rating (1-5): "))
    except ValueError:
        print("Error: Duration must be a number, rating must be 1-5.")
        return

    if rating < 1 or rating > 5:
        print("Error: Rating must be between 1 and 5.")
        return

    notes = input("Notes (optional): ").strip()

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO hike_logs (trail_id, hike_date, duration_hours, rating, notes) VALUES (?, ?, ?, ?, ?)",
            (trail_id, hike_date, duration, rating, notes)
        )
        conn.commit()
        print(f"Hike log added successfully (ID: {cursor.lastrowid}).")
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}. Make sure the trail ID exists.")


# --- SELECT/Query Functions ---

def list_parks(conn):
    """Display all parks in a formatted table."""
    cursor = conn.cursor()
    cursor.execute("SELECT park_id, park_name, state, region FROM parks ORDER BY park_name")
    rows = cursor.fetchall()

    if not rows:
        print("No parks found.")
        return

    print(f"\n{'ID':<4} {'Park Name':<35} {'State':<12} {'Region':<15}")
    print("-" * 66)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<35} {row[2]:<12} {row[3]:<15}")


def list_all_trails(conn):
    """Display all trails with their park names (JOIN)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.trail_id, t.trail_name, p.park_name, t.distance_miles,
               t.elevation_gain_ft, t.difficulty
        FROM trails t
        JOIN parks p ON t.park_id = p.park_id
        ORDER BY p.park_name, t.trail_name
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No trails found.")
        return

    print(f"\n{'ID':<4} {'Trail Name':<25} {'Park':<30} {'Miles':<7} {'Elev':<7} {'Diff':<10}")
    print("-" * 83)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<25} {row[2]:<30} {row[3]:<7.1f} {row[4]:<7} {row[5]:<10}")


def list_trails_by_park(conn):
    """List trails filtered by a specific park."""
    list_parks(conn)

    try:
        park_id = int(input("\nEnter Park ID to view trails: "))
    except ValueError:
        print("Error: Invalid park ID.")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.trail_id, t.trail_name, t.distance_miles, t.elevation_gain_ft, t.difficulty
        FROM trails t
        WHERE t.park_id = ?
        ORDER BY t.trail_name
    """, (park_id,))
    rows = cursor.fetchall()

    if not rows:
        print("No trails found for that park.")
        return

    # Get park name
    cursor.execute("SELECT park_name FROM parks WHERE park_id = ?", (park_id,))
    park_name = cursor.fetchone()
    if park_name:
        print(f"\nTrails in {park_name[0]}:")

    print(f"{'ID':<4} {'Trail Name':<25} {'Miles':<7} {'Elev (ft)':<10} {'Difficulty':<10}")
    print("-" * 56)
    for row in rows:
        print(f"{row[0]:<4} {row[1]:<25} {row[2]:<7.1f} {row[3]:<10} {row[4]:<10}")


def view_hike_history(conn):
    """Display hike log history with trail and park names (JOIN across 3 tables)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.log_id, t.trail_name, p.park_name, h.hike_date,
               h.duration_hours, h.rating, h.notes
        FROM hike_logs h
        JOIN trails t ON h.trail_id = t.trail_id
        JOIN parks p ON t.park_id = p.park_id
        ORDER BY h.hike_date DESC
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No hike logs found.")
        return

    print(f"\n{'ID':<4} {'Trail':<22} {'Park':<25} {'Date':<12} {'Hours':<6} {'Rating':<7} {'Notes'}")
    print("-" * 100)
    for row in rows:
        notes = (row[6][:30] + "...") if row[6] and len(row[6]) > 30 else (row[6] or "")
        print(f"{row[0]:<4} {row[1]:<22} {row[2]:<25} {row[3]:<12} {row[4]:<6.1f} {row[5]:<7} {notes}")


# --- UPDATE Functions ---

def update_trail(conn):
    """Update an existing trail's information."""
    print("\n--- Update Trail ---")
    list_all_trails(conn)

    try:
        trail_id = int(input("\nTrail ID to update: "))
    except ValueError:
        print("Error: Invalid trail ID.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT trail_name, distance_miles, elevation_gain_ft, difficulty FROM trails WHERE trail_id = ?", (trail_id,))
    trail = cursor.fetchone()

    if not trail:
        print("Error: Trail not found.")
        return

    print(f"\nCurrent values: {trail[0]} | {trail[1]} mi | {trail[2]} ft | {trail[3]}")
    print("Press Enter to keep current value.\n")

    trail_name = input(f"Trail name [{trail[0]}]: ").strip() or trail[0]
    distance_input = input(f"Distance miles [{trail[1]}]: ").strip()
    elevation_input = input(f"Elevation gain ft [{trail[2]}]: ").strip()

    print("Difficulty options: Easy, Moderate, Hard, Expert")
    difficulty = input(f"Difficulty [{trail[3]}]: ").strip().capitalize() or trail[3]

    try:
        distance = float(distance_input) if distance_input else trail[1]
        elevation = int(elevation_input) if elevation_input else trail[2]
    except ValueError:
        print("Error: Invalid number entered.")
        return

    if difficulty not in ("Easy", "Moderate", "Hard", "Expert"):
        print("Error: Invalid difficulty level.")
        return

    cursor.execute("""
        UPDATE trails
        SET trail_name = ?, distance_miles = ?, elevation_gain_ft = ?, difficulty = ?
        WHERE trail_id = ?
    """, (trail_name, distance, elevation, difficulty, trail_id))
    conn.commit()
    print(f"Trail '{trail_name}' updated successfully.")


def update_hike_log(conn):
    """Update an existing hike log entry."""
    print("\n--- Update Hike Log ---")
    view_hike_history(conn)

    try:
        log_id = int(input("\nLog ID to update: "))
    except ValueError:
        print("Error: Invalid log ID.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT hike_date, duration_hours, rating, notes FROM hike_logs WHERE log_id = ?", (log_id,))
    log = cursor.fetchone()

    if not log:
        print("Error: Hike log not found.")
        return

    print(f"\nCurrent: Date={log[0]} | Duration={log[1]}h | Rating={log[2]} | Notes={log[3]}")
    print("Press Enter to keep current value.\n")

    hike_date = input(f"Date [{log[0]}]: ").strip() or log[0]
    duration_input = input(f"Duration hours [{log[1]}]: ").strip()
    rating_input = input(f"Rating 1-5 [{log[2]}]: ").strip()
    notes = input(f"Notes [{log[3]}]: ").strip()
    if not notes:
        notes = log[3]

    try:
        duration = float(duration_input) if duration_input else log[1]
        rating = int(rating_input) if rating_input else log[2]
    except ValueError:
        print("Error: Invalid number entered.")
        return

    if rating < 1 or rating > 5:
        print("Error: Rating must be between 1 and 5.")
        return

    cursor.execute("""
        UPDATE hike_logs
        SET hike_date = ?, duration_hours = ?, rating = ?, notes = ?
        WHERE log_id = ?
    """, (hike_date, duration, rating, notes, log_id))
    conn.commit()
    print("Hike log updated successfully.")


# --- DELETE Functions ---

def delete_trail(conn):
    """Delete a trail from the database."""
    print("\n--- Delete Trail ---")
    list_all_trails(conn)

    try:
        trail_id = int(input("\nTrail ID to delete: "))
    except ValueError:
        print("Error: Invalid trail ID.")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT trail_name FROM trails WHERE trail_id = ?", (trail_id,))
    trail = cursor.fetchone()

    if not trail:
        print("Error: Trail not found.")
        return

    # Check for existing hike logs
    cursor.execute("SELECT COUNT(*) FROM hike_logs WHERE trail_id = ?", (trail_id,))
    log_count = cursor.fetchone()[0]

    if log_count > 0:
        confirm = input(f"Warning: '{trail[0]}' has {log_count} hike log(s). Delete trail AND logs? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Delete cancelled.")
            return
        cursor.execute("DELETE FROM hike_logs WHERE trail_id = ?", (trail_id,))

    cursor.execute("DELETE FROM trails WHERE trail_id = ?", (trail_id,))
    conn.commit()
    print(f"Trail '{trail[0]}' deleted successfully.")


def delete_hike_log(conn):
    """Delete a hike log entry."""
    print("\n--- Delete Hike Log ---")
    view_hike_history(conn)

    try:
        log_id = int(input("\nLog ID to delete: "))
    except ValueError:
        print("Error: Invalid log ID.")
        return

    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.log_id, t.trail_name, h.hike_date
        FROM hike_logs h JOIN trails t ON h.trail_id = t.trail_id
        WHERE h.log_id = ?
    """, (log_id,))
    log = cursor.fetchone()

    if not log:
        print("Error: Hike log not found.")
        return

    confirm = input(f"Delete log for '{log[1]}' on {log[2]}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    cursor.execute("DELETE FROM hike_logs WHERE log_id = ?", (log_id,))
    conn.commit()
    print("Hike log deleted successfully.")


# --- JOIN/Summary Reports ---

def summary_report(conn):
    """Display summary statistics using JOINs and aggregate functions."""
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("           TRAIL LOG TRACKER - SUMMARY REPORT")
    print("=" * 60)

    # Total hikes per park (JOIN + GROUP BY + COUNT)
    print("\n--- Hikes Per Park ---")
    cursor.execute("""
        SELECT p.park_name, COUNT(h.log_id) AS total_hikes,
               ROUND(AVG(h.rating), 1) AS avg_rating
        FROM parks p
        LEFT JOIN trails t ON p.park_id = t.park_id
        LEFT JOIN hike_logs h ON t.trail_id = h.trail_id
        GROUP BY p.park_id
        ORDER BY total_hikes DESC
    """)
    rows = cursor.fetchall()

    print(f"{'Park':<35} {'Total Hikes':<13} {'Avg Rating':<10}")
    print("-" * 58)
    for row in rows:
        avg = f"{row[2]}" if row[2] else "N/A"
        print(f"{row[0]:<35} {row[1]:<13} {avg:<10}")

    # Total hikes per trail (JOIN + GROUP BY + COUNT)
    print("\n--- Hikes Per Trail ---")
    cursor.execute("""
        SELECT t.trail_name, p.park_name, COUNT(h.log_id) AS total_hikes,
               ROUND(AVG(h.rating), 1) AS avg_rating,
               ROUND(AVG(h.duration_hours), 1) AS avg_duration
        FROM trails t
        JOIN parks p ON t.park_id = p.park_id
        LEFT JOIN hike_logs h ON t.trail_id = h.trail_id
        GROUP BY t.trail_id
        HAVING COUNT(h.log_id) > 0
        ORDER BY total_hikes DESC
    """)
    rows = cursor.fetchall()

    print(f"{'Trail':<22} {'Park':<25} {'Hikes':<7} {'Avg Rate':<9} {'Avg Hrs':<8}")
    print("-" * 71)
    for row in rows:
        print(f"{row[0]:<22} {row[1]:<25} {row[2]:<7} {row[3]:<9} {row[4]:<8}")

    # Overall stats
    print("\n--- Overall Statistics ---")
    cursor.execute("SELECT COUNT(*) FROM hike_logs")
    total_hikes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM parks")
    total_parks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM trails")
    total_trails = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(SUM(duration_hours), 1) FROM hike_logs")
    total_hours = cursor.fetchone()[0] or 0

    print(f"Total parks:  {total_parks}")
    print(f"Total trails: {total_trails}")
    print(f"Total hikes:  {total_hikes}")
    print(f"Total hours:  {total_hours}")
    print("=" * 60)


# --- Menu System ---

def main_menu():
    """Display the main menu and return user choice."""
    print("\n" + "=" * 40)
    print("       TRAIL LOG TRACKER")
    print("=" * 40)
    print("  1. View Parks")
    print("  2. View All Trails")
    print("  3. View Trails by Park")
    print("  4. View Hike History")
    print("  5. Add Park")
    print("  6. Add Trail")
    print("  7. Log a Hike")
    print("  8. Update Trail")
    print("  9. Update Hike Log")
    print(" 10. Delete Trail")
    print(" 11. Delete Hike Log")
    print(" 12. Summary Report")
    print("  0. Exit")
    print("-" * 40)
    return input("Choose an option: ").strip()


def main():
    """Main application entry point."""
    # Create database and tables
    conn = get_connection()
    create_tables(conn)
    seed_data(conn)

    # Main loop
    while True:
        choice = main_menu()

        if choice == "1":
            list_parks(conn)
        elif choice == "2":
            list_all_trails(conn)
        elif choice == "3":
            list_trails_by_park(conn)
        elif choice == "4":
            view_hike_history(conn)
        elif choice == "5":
            add_park(conn)
        elif choice == "6":
            add_trail(conn)
        elif choice == "7":
            add_hike_log(conn)
        elif choice == "8":
            update_trail(conn)
        elif choice == "9":
            update_hike_log(conn)
        elif choice == "10":
            delete_trail(conn)
        elif choice == "11":
            delete_hike_log(conn)
        elif choice == "12":
            summary_report(conn)
        elif choice == "0":
            print("\nHappy trails! Goodbye.")
            break
        else:
            print("Invalid option. Please try again.")

    conn.close()


if __name__ == "__main__":
    main()
