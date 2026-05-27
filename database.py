import sqlite3
import pathlib

DB_PATH = str(pathlib.Path(__file__).parent / "favorites.db")


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db():
    """Create the favorites table if it doesn't exist yet."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT    NOT NULL,
            lat  REAL    NOT NULL,
            lon  REAL    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def create_favorite(name: str, lat: float, lon: float):
    """Insert a new favourite location."""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO favorites (name, lat, lon) VALUES (?, ?, ?)",
        (name, lat, lon),
    )
    conn.commit()
    conn.close()


def read_favorites() -> list[dict]:
    """Return all saved favourites as a list of dicts."""
    conn = _get_connection()
    rows = conn.execute("SELECT * FROM favorites").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_favorite(id: int, new_name: str):
    """Rename a saved favourite."""
    conn = _get_connection()
    conn.execute("UPDATE favorites SET name = ? WHERE id = ?", (new_name, id))
    conn.commit()
    conn.close()


def delete_favorite(id: int):
    """Delete a saved favourite by its id."""
    conn = _get_connection()
    conn.execute("DELETE FROM favorites WHERE id = ?", (id,))
    conn.commit()
    conn.close()
