"""Tests for tennisages.career_data.

These tests never contact tennisabstract.com: they use the mock career
files in tests/data/ (FemalePlayerCareer.js and MalePlayerCareer.js).
"""

from pathlib import Path

import pytest

from tennisages import career_data

MOCK_DIR = Path(__file__).parent / "data"


@pytest.fixture
def female_js():
    """Mock career file of a female player (opponents' birth dates)."""
    return (MOCK_DIR / "FemalePlayerCareer.js").read_text()


@pytest.fixture
def male_js():
    """Mock career file of a male player (opponents' ages)."""
    return (MOCK_DIR / "MalePlayerCareer.js").read_text()


@pytest.mark.parametrize(
    "player_name",
    ["serena williams", "Serena Williams", "SerenaWilliams", "  SERENA   WILLIAMS "],
)
def test_format_player_name_accepts_common_spellings(player_name):
    assert career_data._format_player_name(player_name) == "SerenaWilliams"


def test_format_player_name_keeps_inner_capitals():
    assert career_data._format_player_name("john McEnroe") == "JohnMcEnroe"


def test_format_player_name_rejects_empty_name():
    with pytest.raises(ValueError, match="empty"):
        career_data._format_player_name("   ")


def test_format_player_name_rejects_non_string():
    with pytest.raises(TypeError, match="string"):
        career_data._format_player_name(42)


def test_extract_match_rows_female(female_js):
    rows = career_data._extract_match_rows(female_js)
    assert len(rows) == 3
    assert rows[0][0] == "19951030"
    assert rows[0][11] == "Anne Miller"


def test_extract_match_rows_male(male_js):
    rows = career_data._extract_match_rows(male_js)
    assert len(rows) == 3
    assert rows[2][11] == "Israel Matos Gil"


def test_extract_match_rows_handles_trailing_comma_and_semicolon():
    js_text = 'var morematchmx = [["20200101", "A"], ["20200102", "B"],\n];'
    assert career_data._extract_match_rows(js_text) == [["20200101", "A"], ["20200102", "B"]]


def test_extract_match_rows_without_array_raises_error():
    with pytest.raises(ValueError, match="No match array"):
        career_data._extract_match_rows("<html>Not Found</html>")
