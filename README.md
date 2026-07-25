# Overview

As a software engineer expanding my skills in database design and SQL, I built a command-line application that integrates Python with SQLite to manage and query relational data. This project gave me hands-on experience with schema design, foreign key relationships, CRUD operations, JOIN queries, and aggregate functions — all fundamental skills for backend development and data engineering.

The **Trail Log Tracker** is a Python CLI application for logging family hikes and adventures across U.S. national parks. It uses a SQLite relational database to store parks, trails, and hike log entries. The application loads an initial dataset of 59 national parks and 3,310 trails from CSV on first run, then persists any user-added data across sessions.

To use the program, run `python3 trail_tracker.py` from the project directory. The interactive menu allows you to:
- Browse parks and trails using fuzzy autocomplete search
- Log hikes with date, duration, rating, and notes
- Update or delete parks, trails, and hike logs
- View summary reports with aggregate statistics (total hikes per park, average ratings)
- Check current weather conditions for any national park

My purpose for writing this software is to deepen my understanding of relational database design, SQL query construction, and how to build a complete application that programmatically creates, reads, updates, and deletes data through a well-structured database layer.

[Software Demo Video](http://youtube.link.goes.here)

# Relational Database

I am using **SQLite** (v3.51.0) as the relational database, accessed through Python's built-in `sqlite3` module. SQLite is a serverless, file-based database engine that stores the entire database in a single file (`trail_tracker.db`). Foreign key enforcement is enabled explicitly with `PRAGMA foreign_keys = ON`.

The database consists of three related tables:

**parks**
| Column | Type | Constraints |
|--------|------|-------------|
| park_id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| park_name | TEXT | NOT NULL |
| state | TEXT | NOT NULL |
| region | TEXT | NOT NULL |
| latitude | REAL | |
| longitude | REAL | |

**trails**
| Column | Type | Constraints |
|--------|------|-------------|
| trail_id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| trail_name | TEXT | NOT NULL |
| park_id | INTEGER | NOT NULL, FOREIGN KEY → parks(park_id) |
| distance_miles | REAL | NOT NULL |
| elevation_gain_ft | INTEGER | NOT NULL |
| difficulty | TEXT | NOT NULL, CHECK IN ('Easy', 'Moderate', 'Hard', 'Expert') |

**hike_logs**
| Column | Type | Constraints |
|--------|------|-------------|
| log_id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| trail_id | INTEGER | NOT NULL, FOREIGN KEY → trails(trail_id) |
| hike_date | TEXT | NOT NULL |
| duration_hours | REAL | NOT NULL |
| rating | INTEGER | NOT NULL, CHECK BETWEEN 1 AND 5 |
| notes | TEXT | |

Relationships:
- A **park** has many **trails** (one-to-many)
- A **trail** has many **hike_logs** (one-to-many)
- Deleting a park cascades to delete its trails and associated hike logs

# Development Environment

I developed this software using Visual Studio Code on macOS, with Git (v2.50.1) for version control and GitHub for remote hosting.

The programming language is **Python (v3.13.5)** with the following libraries:
- **sqlite3** (built-in) — database connection, SQL execution, parameterized queries
- **requests (v2.32.5)** — HTTP requests to the Open-Meteo weather API
- **prompt_toolkit (v3.0.52)** — interactive fuzzy autocomplete search in the terminal
- **pytest (v8.4.2)** — unit testing framework (37 tests covering db and weather modules)
- **csv** (built-in) — reading park and trail data from CSV files
- **pathlib** (built-in) — cross-platform file path handling

# Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Documentation — SQL Syntax](https://www.sqlite.org/lang.html)
- [SQLite Tutorial — Joins](https://www.sqlitetutorial.net/sqlite-join/)
- [Open-Meteo Weather API](https://open-meteo.com/en/docs)
- [prompt_toolkit Documentation](https://python-prompt-toolkit.readthedocs.io/en/stable/)
- [Python Unit Testing with pytest](https://docs.pytest.org/en/stable/getting-started.html)

# Future Work

- Add date range filtering for hike history (e.g., "show hikes from June 2026")
- Implement a "favorites" feature to bookmark frequently hiked trails
- Add elevation profile visualization using matplotlib
- Export hike log data to CSV for sharing or backup
- Add multi-user support with a hikers table and login system
- Integrate trail condition reports or alerts from the NPS API
