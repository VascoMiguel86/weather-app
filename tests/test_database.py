import pytest
import database
from database import init_db, create_favorite, read_favorites, update_favorite, delete_favorite


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    """
    Each test runs against a fresh temporary database.
    monkeypatch replaces database.DB_PATH with a temp file path.
    """
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    init_db()


def test_read_favorites_returns_empty_list_initially():
    assert read_favorites() == []


def test_create_and_read_favorite():
    create_favorite("Amsterdam", 52.37, 4.89)
    favorites = read_favorites()
    assert len(favorites) == 1
    assert favorites[0]["name"] == "Amsterdam"
    assert favorites[0]["lat"] == 52.37
    assert favorites[0]["lon"] == 4.89


def test_create_multiple_favorites():
    create_favorite("Amsterdam", 52.37, 4.89)
    create_favorite("Rotterdam", 51.92, 4.48)
    assert len(read_favorites()) == 2


def test_update_favorite_changes_name():
    create_favorite("Rotterdam", 51.92, 4.48)
    fav_id = read_favorites()[0]["id"]
    update_favorite(fav_id, "Rotterdam Central")
    assert read_favorites()[0]["name"] == "Rotterdam Central"


def test_delete_favorite_removes_entry():
    create_favorite("Utrecht", 52.09, 5.12)
    fav_id = read_favorites()[0]["id"]
    delete_favorite(fav_id)
    assert read_favorites() == []


def test_delete_only_removes_target_favorite():
    create_favorite("Amsterdam", 52.37, 4.89)
    create_favorite("Utrecht", 52.09, 5.12)
    fav_id = read_favorites()[0]["id"]
    delete_favorite(fav_id)
    remaining = read_favorites()
    assert len(remaining) == 1
    assert remaining[0]["name"] == "Utrecht"
