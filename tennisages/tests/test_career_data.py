"""Tests for tennisages.career_data.

These tests never contact tennisabstract.com: they use the mock career
files in tests/data/ (FemalePlayerCareer.js and MalePlayerCareer.js).
"""

import pytest

from tennisages import career_data


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
