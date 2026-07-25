"""
Trail Log Tracker
A command-line application for logging family hikes and adventures
across national parks and trails.

CSE 310 - Module 2: SQL Relational Databases
Author: Adam Cottam
Date: July 2026
"""

# Imports
from datetime import date
import db
from weather import get_weather, PARK_COORDS


# --- Display Functions ---

def display_parks(parks: list[dict]):
    """Display parks in a formatted table."""
    if not parks:
        print("No parks found.")
        return

    print(f"\n{'ID':<4} {'Park Name':<35} {'State':<12} {'Region':<15}")
    print("-" * 66)
    for p in parks:
        print(f"{p['park_id']:<4} {p['park_name']:<35} {p['state']:<12} {p['region']:<15}")


def display_trails(trails: list[dict]):
    """Display trails in a formatted table."""
    if not trails:
        print("No trails found.")
        return

    # Check if park_name is in the data
    if "park_name" in trails[0]:
        print(f"\n{'ID':<4} {'Trail Name':<25} {'Park':<30} {'Miles':<7} {'Elev':<7} {'Diff':<10}")
        print("-" * 83)
        for t in trails:
            print(f"{t['trail_id']:<4} {t['trail_name']:<25} {t['park_name']:<30} {t['distance_miles']:<7.1f} {t['elevation_gain_ft']:<7} {t['difficulty']:<10}")
    else:
        print(f"\n{'ID':<4} {'Trail Name':<25} {'Miles':<7} {'Elev (ft)':<10} {'Difficulty':<10}")
        print("-" * 56)
        for t in trails:
            print(f"{t['trail_id']:<4} {t['trail_name']:<25} {t['distance_miles']:<7.1f} {t['elevation_gain_ft']:<10} {t['difficulty']:<10}")


def display_hike_history(hikes: list[dict]):
    """Display hike logs in a formatted table."""
    if not hikes:
        print("No hike logs found.")
        return

    print(f"\n{'ID':<4} {'Trail':<22} {'Park':<25} {'Date':<12} {'Hours':<6} {'Rating':<7} {'Notes'}")
    print("-" * 100)
    for h in hikes:
        notes = (h['notes'][:30] + "...") if h['notes'] and len(h['notes']) > 30 else (h['notes'] or "")
        print(f"{h['log_id']:<4} {h['trail_name']:<22} {h['park_name']:<25} {h['hike_date']:<12} {h['duration_hours']:<6.1f} {h['rating']:<7} {notes}")


def display_summary_report():
    """Display summary statistics using JOINs and aggregate functions."""
    print("\n" + "=" * 60)
    print("           TRAIL LOG TRACKER - SUMMARY REPORT")
    print("=" * 60)

    # Hikes Per Park
    print("\n--- Hikes Per Park ---")
    park_stats = db.get_hikes_per_park()
    print(f"{'Park':<35} {'Total Hikes':<13} {'Avg Rating':<10}")
    print("-" * 58)
    for row in park_stats:
        avg = f"{row['avg_rating']}" if row['avg_rating'] else "N/A"
        print(f"{row['park_name']:<35} {row['total_hikes']:<13} {avg:<10}")

    # Hikes Per Trail
    print("\n--- Hikes Per Trail ---")
    trail_stats = db.get_hikes_per_trail()
    print(f"{'Trail':<22} {'Park':<25} {'Hikes':<7} {'Avg Rate':<9} {'Avg Hrs':<8}")
    print("-" * 71)
    for row in trail_stats:
        print(f"{row['trail_name']:<22} {row['park_name']:<25} {row['total_hikes']:<7} {row['avg_rating']:<9} {row['avg_duration']:<8}")

    # Overall Stats
    print("\n--- Overall Statistics ---")
    stats = db.get_overall_stats()
    print(f"Total parks:  {stats['total_parks']}")
    print(f"Total trails: {stats['total_trails']}")
    print(f"Total hikes:  {stats['total_hikes']}")
    print(f"Total hours:  {stats['total_hours']}")
    print("=" * 60)


# --- Input/Action Functions ---

def add_park():
    """Prompt user to add a new park."""
    print("\n--- Add New Park ---")
    park_name = input("Park name: ").strip()
    state = input("State: ").strip()
    region = input("Region (e.g., Southwest, Northwest, Southeast): ").strip()

    # Validation
    if not park_name or not state or not region:
        print("Error: All fields are required.")
        return

    # Insert
    park_id = db.insert_park(park_name, state, region)
    if park_id:
        print(f"Park '{park_name}' added successfully (ID: {park_id}).")


def add_trail():
    """Prompt user to add a new trail."""
    print("\n--- Add New Trail ---")

    # Show available parks
    display_parks(db.get_all_parks())

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

    # Insert
    trail_id = db.insert_trail(trail_name, park_id, distance, elevation, difficulty)
    if trail_id:
        print(f"Trail '{trail_name}' added successfully (ID: {trail_id}).")


def add_hike_log():
    """Prompt user to log a new hike."""
    print("\n--- Log a Hike ---")

    # Show available trails
    display_trails(db.get_all_trails())

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

    # Insert
    log_id = db.insert_hike_log(trail_id, hike_date, duration, rating, notes)
    if log_id:
        print(f"Hike log added successfully (ID: {log_id}).")


def edit_trail():
    """Prompt user to update an existing trail."""
    print("\n--- Update Trail ---")
    display_trails(db.get_all_trails())

    try:
        trail_id = int(input("\nTrail ID to update: "))
    except ValueError:
        print("Error: Invalid trail ID.")
        return

    # Get current trail data
    trail = db.get_trail_by_id(trail_id)
    if not trail:
        print("Error: Trail not found.")
        return

    print(f"\nCurrent values: {trail['trail_name']} | {trail['distance_miles']} mi | {trail['elevation_gain_ft']} ft | {trail['difficulty']}")
    print("Press Enter to keep current value.\n")

    trail_name = input(f"Trail name [{trail['trail_name']}]: ").strip() or trail['trail_name']
    distance_input = input(f"Distance miles [{trail['distance_miles']}]: ").strip()
    elevation_input = input(f"Elevation gain ft [{trail['elevation_gain_ft']}]: ").strip()

    print("Difficulty options: Easy, Moderate, Hard, Expert")
    difficulty = input(f"Difficulty [{trail['difficulty']}]: ").strip().capitalize() or trail['difficulty']

    try:
        distance = float(distance_input) if distance_input else trail['distance_miles']
        elevation = int(elevation_input) if elevation_input else trail['elevation_gain_ft']
    except ValueError:
        print("Error: Invalid number entered.")
        return

    if difficulty not in ("Easy", "Moderate", "Hard", "Expert"):
        print("Error: Invalid difficulty level.")
        return

    # Update
    if db.update_trail(trail_id, trail_name, distance, elevation, difficulty):
        print(f"Trail '{trail_name}' updated successfully.")
    else:
        print("Error: Failed to update trail.")


def edit_hike_log():
    """Prompt user to update an existing hike log."""
    print("\n--- Update Hike Log ---")
    display_hike_history(db.get_hike_history())

    try:
        log_id = int(input("\nLog ID to update: "))
    except ValueError:
        print("Error: Invalid log ID.")
        return

    # Get current log data
    log = db.get_hike_log_by_id(log_id)
    if not log:
        print("Error: Hike log not found.")
        return

    print(f"\nCurrent: Date={log['hike_date']} | Duration={log['duration_hours']}h | Rating={log['rating']} | Notes={log['notes']}")
    print("Press Enter to keep current value.\n")

    hike_date = input(f"Date [{log['hike_date']}]: ").strip() or log['hike_date']
    duration_input = input(f"Duration hours [{log['duration_hours']}]: ").strip()
    rating_input = input(f"Rating 1-5 [{log['rating']}]: ").strip()
    notes = input(f"Notes [{log['notes']}]: ").strip()
    if not notes:
        notes = log['notes']

    try:
        duration = float(duration_input) if duration_input else log['duration_hours']
        rating = int(rating_input) if rating_input else log['rating']
    except ValueError:
        print("Error: Invalid number entered.")
        return

    if rating < 1 or rating > 5:
        print("Error: Rating must be between 1 and 5.")
        return

    # Update
    if db.update_hike_log(log_id, hike_date, duration, rating, notes):
        print("Hike log updated successfully.")
    else:
        print("Error: Failed to update hike log.")


def remove_trail():
    """Prompt user to delete a trail."""
    print("\n--- Delete Trail ---")
    display_trails(db.get_all_trails())

    try:
        trail_id = int(input("\nTrail ID to delete: "))
    except ValueError:
        print("Error: Invalid trail ID.")
        return

    # Get trail info
    trail = db.get_trail_by_id(trail_id)
    if not trail:
        print("Error: Trail not found.")
        return

    # Check for existing hike logs
    log_count = db.get_hike_log_count_for_trail(trail_id)
    if log_count > 0:
        confirm = input(f"Warning: '{trail['trail_name']}' has {log_count} hike log(s). Delete trail AND logs? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Delete cancelled.")
            return
    else:
        confirm = input(f"Delete trail '{trail['trail_name']}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Delete cancelled.")
            return

    # Delete
    if db.delete_trail(trail_id):
        print(f"Trail '{trail['trail_name']}' deleted successfully.")
    else:
        print("Error: Failed to delete trail.")


def remove_hike_log():
    """Prompt user to delete a hike log."""
    print("\n--- Delete Hike Log ---")
    hikes = db.get_hike_history()
    display_hike_history(hikes)

    try:
        log_id = int(input("\nLog ID to delete: "))
    except ValueError:
        print("Error: Invalid log ID.")
        return

    # Find the log in our results for display
    log = next((h for h in hikes if h['log_id'] == log_id), None)
    if not log:
        print("Error: Hike log not found.")
        return

    confirm = input(f"Delete log for '{log['trail_name']}' on {log['hike_date']}? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    # Delete
    if db.delete_hike_log(log_id):
        print("Hike log deleted successfully.")
    else:
        print("Error: Failed to delete hike log.")


def view_trails_by_park():
    """Prompt user to select a park, then display its trails."""
    display_parks(db.get_all_parks())

    try:
        park_id = int(input("\nEnter Park ID to view trails: "))
    except ValueError:
        print("Error: Invalid park ID.")
        return

    # Get park name
    park_name = db.get_park_name(park_id)
    if park_name:
        print(f"\nTrails in {park_name}:")

    # Get and display trails
    trails = db.get_trails_by_park(park_id)
    display_trails(trails)


# --- Weather Functions ---

def show_weather():
    """Prompt user to select a park and display current weather."""
    print("\n--- Park Weather Lookup ---")

    # Show available parks
    parks = db.get_all_parks()
    display_parks(parks)

    try:
        park_id = int(input("\nEnter Park ID for weather: "))
    except ValueError:
        print("Error: Invalid park ID.")
        return

    # Get park name
    park_name = db.get_park_name(park_id)
    if not park_name:
        print("Error: Park not found.")
        return

    # Check if coordinates are available
    if park_name not in PARK_COORDS:
        print(f"Error: No coordinates available for '{park_name}'.")
        print("Add coordinates to PARK_COORDS in weather.py.")
        return

    # Fetch weather
    try:
        weather = get_weather(park_name)
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return

    # Display weather
    print(f"\n{'=' * 50}")
    print(f"  Weather for {weather['park_name']}")
    print(f"{'=' * 50}")
    print(f"  Conditions:   {weather['description']}")
    print(f"  Temperature:  {weather['temp_f']:.1f}°F")
    print(f"  Humidity:     {weather['humidity']:.0f}%")
    print(f"  Wind Speed:   {weather['wind_mph']:.1f} mph")

    # Wind Chill (if applicable)
    if weather['wind_chill_f'] is not None:
        print(f"  Wind Chill:   {weather['wind_chill_f']:.1f}°F")

    # Heat Index (if applicable)
    if weather['heat_index_f'] is not None:
        print(f"  Heat Index:   {weather['heat_index_f']:.1f}°F")

    print(f"  Coordinates:  {weather['lat']}, {weather['lon']}")
    print(f"  Retrieved:    {weather['timestamp_utc']} UTC")
    print(f"{'=' * 50}")


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
    print(" 13. Park Weather")
    print("  0. Exit")
    print("-" * 40)
    return input("Choose an option: ").strip()


def main():
    """Main application entry point."""
    # Initialize database and load data from CSV
    db.create_database()
    db.import_trails_from_csv()

    # Main loop
    while True:
        choice = main_menu()

        if choice == "1":
            display_parks(db.get_all_parks())
        elif choice == "2":
            display_trails(db.get_all_trails())
        elif choice == "3":
            view_trails_by_park()
        elif choice == "4":
            display_hike_history(db.get_hike_history())
        elif choice == "5":
            add_park()
        elif choice == "6":
            add_trail()
        elif choice == "7":
            add_hike_log()
        elif choice == "8":
            edit_trail()
        elif choice == "9":
            edit_hike_log()
        elif choice == "10":
            remove_trail()
        elif choice == "11":
            remove_hike_log()
        elif choice == "12":
            display_summary_report()
        elif choice == "13":
            show_weather()
        elif choice == "0":
            print("\nHappy trails! Goodbye.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
