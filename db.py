"""
Author: Adam Cottam
Purpose: CSE 310 Module 2 - Trail Log Tracker
Description: Database operations for the Trail Log Tracker application.
"""

# Imports
import sqlite3
from pathlib import Path
import csv

# Constants
DB_PATH = Path(__file__).parent / "trail_tracker.db"
CSV_PATH = Path(__file__).parent / "trails.csv"

# Create `parks` Table
CREATE_PARKS_SQL = """
    CREATE TABLE IF NOT EXISTS parks (
        park_id INTEGER PRIMARY KEY AUTOINCREMENT,
        park_name TEXT NOT NULL,
        state TEXT NOT NULL,
        region TEXT NOT NULL,
        latitude REAL,
        longitude REAL
    )
"""

# Create `trails` Table
CREATE_TRAILS_SQL = """
    CREATE TABLE IF NOT EXISTS trails (
        trail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_name TEXT NOT NULL,
        park_id INTEGER NOT NULL,
        distance_miles REAL NOT NULL,
        elevation_gain_ft INTEGER NOT NULL,
        difficulty TEXT NOT NULL CHECK(difficulty IN ('Easy', 'Moderate', 'Hard', 'Expert')),
        FOREIGN KEY (park_id) REFERENCES parks(park_id)
    )
"""

# Create `hike_logs` Table
CREATE_HIKE_LOGS_SQL = """
    CREATE TABLE IF NOT EXISTS hike_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        trail_id INTEGER NOT NULL,
        hike_date TEXT NOT NULL,
        duration_hours REAL NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        notes TEXT,
        FOREIGN KEY (trail_id) REFERENCES trails(trail_id)
    )
"""


def get_connection(db_path: Path = DB_PATH):
    """
    Create and return a database connection with foreign key enforcement.
    Parameters: db_path
    Return: sqlite3.Connection
    """
    # DB Connection
    conn = sqlite3.connect(db_path)

    # Enable Foreign Keys
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def create_database(db_path: Path = DB_PATH):
    """
    Create SQLite DB and tables if they don't exist.
    Parameters: db_path
    Return: none
    """
    # DB Connection
    conn = get_connection(db_path)

    # Execute SQL
    with conn:
        conn.execute(CREATE_PARKS_SQL)
        conn.execute(CREATE_TRAILS_SQL)
        conn.execute(CREATE_HIKE_LOGS_SQL)

    # Close DB Connection
    conn.close()


def seed_data(db_path: Path = DB_PATH):
    """
    Insert sample parks, trails, and hike logs if tables are empty.
    Parameters: db_path
    Return: none
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        # Check if data already exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parks")
        if cursor.fetchone()[0] > 0:
            return

        # Sample Parks
        parks = [
            ("Zion National Park", "Utah", "Southwest"),
            ("Yellowstone National Park", "Wyoming", "Northwest"),
            ("Grand Canyon National Park", "Arizona", "Southwest"),
            ("Glacier National Park", "Montana", "Northwest"),
            ("Bryce Canyon National Park", "Utah", "Southwest"),
        ]

        # Sample Trails
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

        # Sample Hike Logs
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

        # Insert Data
        with conn:
            conn.executemany(
                "INSERT INTO parks (park_name, state, region) VALUES (?, ?, ?)",
                parks
            )
            conn.executemany(
                "INSERT INTO trails (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty) VALUES (?, ?, ?, ?, ?)",
                trails
            )
            conn.executemany(
                "INSERT INTO hike_logs (trail_id, hike_date, duration_hours, rating, notes) VALUES (?, ?, ?, ?, ?)",
                hike_logs
            )

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error seeding data: {e}")

    # Close DB Connection
    finally:
        conn.close()


def import_trails_from_csv(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH, truncate=False):
    """
    Import parks and trails from CSV into DB.
    Parameters: csv_path, db_path, truncate
    Return: none
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        # Verifies tables are created
        with conn:
            conn.execute(CREATE_PARKS_SQL)
            conn.execute(CREATE_TRAILS_SQL)
            conn.execute(CREATE_HIKE_LOGS_SQL)

        # Truncate Tables if True
        if truncate:
            with conn:
                conn.execute("DELETE FROM hike_logs")
                conn.execute("DELETE FROM trails")
                conn.execute("DELETE FROM parks")

        # Check if data already exists
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM parks")
        if cursor.fetchone()[0] > 0 and not truncate:
            return

        # Read File
        with conn, open(csv_path, newline="", encoding="utf-8") as f:

            # CSV Reader
            reader = csv.DictReader(f)

            # Track parks to avoid duplicates
            parks_added = {}

            # Track coordinates per park for averaging
            park_coords = {}

            # Build trail rows
            trail_rows = []

            for row in reader:
                park_name = row["park_name"].strip()
                state = row["state"].strip()
                region = row["region"].strip()
                lat = float(row["latitude"])
                lon = float(row["longitude"])

                # Collect coordinates for averaging
                if park_name not in park_coords:
                    park_coords[park_name] = {"lats": [], "lons": [], "state": state, "region": region}
                park_coords[park_name]["lats"].append(lat)
                park_coords[park_name]["lons"].append(lon)

                # Add trail row (park_id will be set after parks are inserted)
                trail_rows.append((
                    row["trail_name"].strip(),
                    park_name,
                    float(row["distance_miles"]),
                    int(row["elevation_gain_ft"]),
                    row["difficulty"].strip(),
                ))

            # Insert parks with average coordinates
            for park_name, data in park_coords.items():
                avg_lat = sum(data["lats"]) / len(data["lats"])
                avg_lon = sum(data["lons"]) / len(data["lons"])
                cursor.execute(
                    "INSERT INTO parks (park_name, state, region, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                    (park_name, data["state"], data["region"], round(avg_lat, 5), round(avg_lon, 5))
                )
                parks_added[park_name] = cursor.lastrowid

            # Insert all trails with park_id lookup
            trail_inserts = []
            for trail_name, park_name, distance, elevation, difficulty in trail_rows:
                park_id = parks_added[park_name]
                trail_inserts.append((trail_name, park_id, distance, elevation, difficulty))

            conn.executemany(
                "INSERT INTO trails (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty) VALUES (?, ?, ?, ?, ?)",
                trail_inserts
            )

        print(f"Imported {len(parks_added)} parks and {len(trail_rows)} trails from CSV.")

    # File Not Found Error
    except FileNotFoundError as e:
        print(f"Error: CSV file not found: {csv_path}")

    # SQLite Integrity Error
    except sqlite3.IntegrityError as e:
        print(f"Error: Integrity error while importing trails: {e}")

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error: SQLite error while importing trails: {e}")

    # CSV Error
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")

    # Value Error - If issue converting into float/int
    except ValueError as e:
        print(f"Error converting value: {e}")

    # General Error
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

    # Final items
    finally:
        # Close DB Connection
        conn.close()


# --- INSERT Functions ---

def insert_park(park_name: str, state: str, region: str,
                latitude: float = None, longitude: float = None, db_path: Path = DB_PATH) -> int | None:
    """
    Insert a new park into the database.
    Parameters: park_name, state, region, latitude, longitude, db_path
    Return: park_id or None
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO parks (park_name, state, region, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
                (park_name, state, region, latitude, longitude)
            )
            return cursor.lastrowid

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error inserting park: {e}")
        return None

    # Close DB Connection
    finally:
        conn.close()


def insert_trail(trail_name: str, park_id: int, distance_miles: float,
                 elevation_gain_ft: int, difficulty: str, db_path: Path = DB_PATH) -> int | None:
    """
    Insert a new trail into the database.
    Parameters: trail_name, park_id, distance_miles, elevation_gain_ft, difficulty, db_path
    Return: trail_id or None
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO trails (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty) VALUES (?, ?, ?, ?, ?)",
                (trail_name, park_id, distance_miles, elevation_gain_ft, difficulty)
            )
            return cursor.lastrowid

    # Integrity Error (bad FK or CHECK)
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return None

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error inserting trail: {e}")
        return None

    # Close DB Connection
    finally:
        conn.close()


def insert_hike_log(trail_id: int, hike_date: str, duration_hours: float,
                    rating: int, notes: str = "", db_path: Path = DB_PATH) -> int | None:
    """
    Insert a new hike log entry.
    Parameters: trail_id, hike_date, duration_hours, rating, notes, db_path
    Return: log_id or None
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO hike_logs (trail_id, hike_date, duration_hours, rating, notes) VALUES (?, ?, ?, ?, ?)",
                (trail_id, hike_date, duration_hours, rating, notes)
            )
            return cursor.lastrowid

    # Integrity Error (bad FK or CHECK)
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return None

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error inserting hike log: {e}")
        return None

    # Close DB Connection
    finally:
        conn.close()


# --- SELECT/Query Functions ---

def get_all_parks(db_path: Path = DB_PATH) -> list[dict]:
    """
    Retrieve all parks from the database.
    Parameters: db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    rows = conn.execute(
        "SELECT park_id, park_name, state, region FROM parks ORDER BY park_name"
    ).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_all_trails(db_path: Path = DB_PATH) -> list[dict]:
    """
    Retrieve all trails with park names (JOIN).
    Parameters: db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL (JOIN trails + parks)
    rows = conn.execute("""
        SELECT t.trail_id, t.trail_name, p.park_name, t.distance_miles,
               t.elevation_gain_ft, t.difficulty
        FROM trails t
        JOIN parks p ON t.park_id = p.park_id
        ORDER BY p.park_name, t.trail_name
    """).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_trails_by_park(park_id: int, db_path: Path = DB_PATH) -> list[dict]:
    """
    Retrieve trails filtered by park ID.
    Parameters: park_id, db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    rows = conn.execute("""
        SELECT t.trail_id, t.trail_name, t.distance_miles,
               t.elevation_gain_ft, t.difficulty
        FROM trails t
        WHERE t.park_id = ?
        ORDER BY t.trail_name
    """, (park_id,)).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_park_name(park_id: int, db_path: Path = DB_PATH) -> str | None:
    """
    Get a park's name by ID.
    Parameters: park_id, db_path
    Return: park_name or None
    """
    # DB Connection
    conn = get_connection(db_path)

    # Execute SQL
    row = conn.execute(
        "SELECT park_name FROM parks WHERE park_id = ?", (park_id,)
    ).fetchone()

    # Close DB Connection
    conn.close()

    # Return
    return row[0] if row else None


def get_park_coordinates(park_name: str, db_path: Path = DB_PATH) -> tuple[float, float] | None:
    """
    Get coordinates of a park by name.
    Parameters: park_name, db_path
    Return: (latitude, longitude) or None
    """
    # Check if DB exists
    if not db_path.exists():
        return None

    # DB Connection
    conn = get_connection(db_path)

    try:
        # Execute SQL
        row = conn.execute(
            "SELECT latitude, longitude FROM parks WHERE park_name = ?",
            (park_name,)
        ).fetchone()

        # Return lat and longitude
        if row and row[0] is not None and row[1] is not None:
            return (row[0], row[1])
        return None

    # Handle case where table doesn't exist
    except sqlite3.OperationalError:
        return None

    # Close DB Connection
    finally:
        conn.close()


def get_hike_history(db_path: Path = DB_PATH) -> list[dict]:
    """
    Retrieve hike log history with trail and park names (JOIN across 3 tables).
    Parameters: db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL (JOIN hike_logs + trails + parks)
    rows = conn.execute("""
        SELECT h.log_id, t.trail_name, p.park_name, h.hike_date,
               h.duration_hours, h.rating, h.notes
        FROM hike_logs h
        JOIN trails t ON h.trail_id = t.trail_id
        JOIN parks p ON t.park_id = p.park_id
        ORDER BY h.hike_date DESC
    """).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_trail_by_id(trail_id: int, db_path: Path = DB_PATH) -> dict | None:
    """
    Get a trail by its ID.
    Parameters: trail_id, db_path
    Return: dict or None
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    row = conn.execute(
        "SELECT trail_id, trail_name, distance_miles, elevation_gain_ft, difficulty FROM trails WHERE trail_id = ?",
        (trail_id,)
    ).fetchone()

    # Close DB Connection
    conn.close()

    # Return
    return dict(row) if row else None


def get_hike_log_by_id(log_id: int, db_path: Path = DB_PATH) -> dict | None:
    """
    Get a hike log by its ID.
    Parameters: log_id, db_path
    Return: dict or None
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    row = conn.execute(
        "SELECT log_id, trail_id, hike_date, duration_hours, rating, notes FROM hike_logs WHERE log_id = ?",
        (log_id,)
    ).fetchone()

    # Close DB Connection
    conn.close()

    # Return
    return dict(row) if row else None


# --- UPDATE Functions ---

def update_trail(trail_id: int, trail_name: str, distance_miles: float,
                 elevation_gain_ft: int, difficulty: str, db_path: Path = DB_PATH) -> bool:
    """
    Update an existing trail.
    Parameters: trail_id, trail_name, distance_miles, elevation_gain_ft, difficulty, db_path
    Return: True if updated, False otherwise
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute("""
                UPDATE trails
                SET trail_name = ?, distance_miles = ?, elevation_gain_ft = ?, difficulty = ?
                WHERE trail_id = ?
            """, (trail_name, distance_miles, elevation_gain_ft, difficulty, trail_id))
            return cursor.rowcount > 0

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error updating trail: {e}")
        return False

    # Close DB Connection
    finally:
        conn.close()


def update_hike_log(log_id: int, hike_date: str, duration_hours: float,
                    rating: int, notes: str, db_path: Path = DB_PATH) -> bool:
    """
    Update an existing hike log entry.
    Parameters: log_id, hike_date, duration_hours, rating, notes, db_path
    Return: True if updated, False otherwise
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute("""
                UPDATE hike_logs
                SET hike_date = ?, duration_hours = ?, rating = ?, notes = ?
                WHERE log_id = ?
            """, (hike_date, duration_hours, rating, notes, log_id))
            return cursor.rowcount > 0

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error updating hike log: {e}")
        return False

    # Close DB Connection
    finally:
        conn.close()


# --- DELETE Functions ---

def delete_trail(trail_id: int, db_path: Path = DB_PATH) -> bool:
    """
    Delete a trail and its associated hike logs.
    Parameters: trail_id, db_path
    Return: True if deleted, False otherwise
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            # Delete associated hike logs first
            conn.execute("DELETE FROM hike_logs WHERE trail_id = ?", (trail_id,))

            # Delete the trail
            cursor = conn.execute("DELETE FROM trails WHERE trail_id = ?", (trail_id,))
            return cursor.rowcount > 0

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error deleting trail: {e}")
        return False

    # Close DB Connection
    finally:
        conn.close()


def delete_hike_log(log_id: int, db_path: Path = DB_PATH) -> bool:
    """
    Delete a hike log entry.
    Parameters: log_id, db_path
    Return: True if deleted, False otherwise
    """
    # DB Connection
    conn = get_connection(db_path)

    try:
        with conn:
            cursor = conn.execute("DELETE FROM hike_logs WHERE log_id = ?", (log_id,))
            return cursor.rowcount > 0

    # SQLite Error
    except sqlite3.Error as e:
        print(f"Error deleting hike log: {e}")
        return False

    # Close DB Connection
    finally:
        conn.close()


def get_hike_log_count_for_trail(trail_id: int, db_path: Path = DB_PATH) -> int:
    """
    Get the number of hike logs for a trail.
    Parameters: trail_id, db_path
    Return: int
    """
    # DB Connection
    conn = get_connection(db_path)

    # Execute SQL
    row = conn.execute(
        "SELECT COUNT(*) FROM hike_logs WHERE trail_id = ?", (trail_id,)
    ).fetchone()

    # Close DB Connection
    conn.close()

    # Return
    return row[0] if row else 0


# --- Summary/Report Functions (JOINs with Aggregates) ---

def get_hikes_per_park(db_path: Path = DB_PATH) -> list[dict]:
    """
    Get total hikes and average rating per park (JOIN + GROUP BY + COUNT + AVG).
    Parameters: db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    rows = conn.execute("""
        SELECT p.park_name, COUNT(h.log_id) AS total_hikes,
               ROUND(AVG(h.rating), 1) AS avg_rating
        FROM parks p
        LEFT JOIN trails t ON p.park_id = t.park_id
        LEFT JOIN hike_logs h ON t.trail_id = h.trail_id
        GROUP BY p.park_id
        ORDER BY total_hikes DESC
    """).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_hikes_per_trail(db_path: Path = DB_PATH) -> list[dict]:
    """
    Get total hikes, avg rating, and avg duration per trail (JOIN + GROUP BY + HAVING).
    Parameters: db_path
    Return: list[dict]
    """
    # DB Connection
    conn = get_connection(db_path)
    conn.row_factory = sqlite3.Row

    # Execute SQL
    rows = conn.execute("""
        SELECT t.trail_name, p.park_name, COUNT(h.log_id) AS total_hikes,
               ROUND(AVG(h.rating), 1) AS avg_rating,
               ROUND(AVG(h.duration_hours), 1) AS avg_duration
        FROM trails t
        JOIN parks p ON t.park_id = p.park_id
        LEFT JOIN hike_logs h ON t.trail_id = h.trail_id
        GROUP BY t.trail_id
        HAVING COUNT(h.log_id) > 0
        ORDER BY total_hikes DESC
    """).fetchall()

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return [dict(r) for r in rows]


def get_overall_stats(db_path: Path = DB_PATH) -> dict:
    """
    Get overall statistics (total parks, trails, hikes, hours).
    Parameters: db_path
    Return: dict
    """
    # DB Connection
    conn = get_connection(db_path)

    # Execute SQL
    total_parks = conn.execute("SELECT COUNT(*) FROM parks").fetchone()[0]
    total_trails = conn.execute("SELECT COUNT(*) FROM trails").fetchone()[0]
    total_hikes = conn.execute("SELECT COUNT(*) FROM hike_logs").fetchone()[0]
    total_hours = conn.execute("SELECT ROUND(SUM(duration_hours), 1) FROM hike_logs").fetchone()[0] or 0

    # Close DB Connection
    conn.close()

    # Return Dictionary
    return {
        "total_parks": total_parks,
        "total_trails": total_trails,
        "total_hikes": total_hikes,
        "total_hours": total_hours,
    }
