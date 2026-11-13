"""Tests for tennisages.career_data.

These tests never contact tennisabstract.com: they use the mock career
files in tests/data/ (FemalePlayerCareer.js and MalePlayerCareer.js).
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd
import pytest

from tennisages import career_data, get_career_data

MOCK_DIR = Path(__file__).parent / "data"
DAYS_PER_YEAR = 365.25
SERENA_BIRTH_DATE = pd.Timestamp("1981-09-26")  # the female mock rows are hers
NADAL_BIRTH_DATE = pd.Timestamp("1986-06-03")   # the male mock rows are his

MOCK_PLAYER_PAGE = """
var nameparam = 'SerenaWilliams';
var fullname = 'Serena Williams';
var dob = 19810926;
var hand = 'R';
"""


def not_found(url):
    """Imitate the 404 error that tennisabstract.com returns for unknown players."""
    raise urllib.error.HTTPError(url, 404, "Not Found", hdrs=None, fp=None)


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


def test_rows_to_frame_keeps_needed_fields(female_js):
    matches = career_data._rows_to_frame(career_data._extract_match_rows(female_js))
    assert list(matches.columns) == list(career_data.MATCH_FIELDS)
    assert matches.shape == (3, len(career_data.MATCH_FIELDS))
    first = matches.iloc[0]
    assert first["tournament"] == "Canadian Open"
    assert first["result"] == "L"
    assert first["round"] == "Q1"
    assert first["opponent_info"] == "19770119"


def test_rows_to_frame_reads_male_opponent_age(male_js):
    matches = career_data._rows_to_frame(career_data._extract_match_rows(male_js))
    assert list(matches["opponent_info"]) == ["22.264202601", "24.2902121834", "18.7597535934"]


def test_rows_to_frame_skips_incomplete_rows(female_js):
    rows = career_data._extract_match_rows(female_js) + [["20000101", "Too short"]]
    assert len(career_data._rows_to_frame(rows)) == 3


def mock_matches(js_text):
    """Mock career file -> data frame with real dates, as used by the age helpers."""
    matches = career_data._rows_to_frame(career_data._extract_match_rows(js_text))
    matches["match_date"] = pd.to_datetime(matches["match_date"], format="%Y%m%d")
    return matches


def test_is_birth_date_column_detects_female_file(female_js):
    assert career_data._is_birth_date_column(mock_matches(female_js)["opponent_info"])


def test_is_birth_date_column_detects_male_file(male_js):
    assert not career_data._is_birth_date_column(mock_matches(male_js)["opponent_info"])


def test_years_between_uses_365_25_day_years():
    start = pd.Series(pd.to_datetime(["2000-01-01"]))
    end = pd.Series(pd.to_datetime(["2001-01-01"]))
    assert career_data._years_between(start, end).iloc[0] == pytest.approx(366 / DAYS_PER_YEAR)


def test_compute_opponent_age_from_birth_date(female_js):
    matches = mock_matches(female_js)
    ages = career_data._compute_opponent_age(matches["opponent_info"], matches["match_date"])
    # Anne Miller, born 1977-01-19, played on 1995-10-30
    expected_days = (pd.Timestamp("1995-10-30") - pd.Timestamp("1977-01-19")).days
    assert ages.iloc[0] == pytest.approx(expected_days / DAYS_PER_YEAR)
    assert ages.iloc[0] == pytest.approx(18.78, abs=0.01)


def test_compute_opponent_age_read_directly_for_men(male_js):
    matches = mock_matches(male_js)
    ages = career_data._compute_opponent_age(matches["opponent_info"], matches["match_date"])
    assert list(ages) == pytest.approx([22.264202601, 24.2902121834, 18.7597535934])


def test_compute_opponent_age_missing_birth_date_is_nan(female_js):
    matches = mock_matches(female_js)
    matches.loc[1, "opponent_info"] = ""
    ages = career_data._compute_opponent_age(matches["opponent_info"], matches["match_date"])
    assert ages.isna().tolist() == [False, True, False]


def test_clean_matches_female_columns_and_values(female_js):
    serena = career_data._clean_matches(female_js, "Serena Williams", SERENA_BIRTH_DATE)
    assert list(serena.columns) == career_data.OUTPUT_COLUMNS
    assert len(serena) == 3
    first = serena.iloc[0]
    assert first["player"] == "Serena Williams"
    assert first["opponent"] == "Anne Miller"
    assert first["result"] == "lost"
    assert first["player_age"] == pytest.approx(14.09, abs=0.01)
    assert first["opponent_age"] == pytest.approx(18.78, abs=0.01)
    assert first["age_difference"] == pytest.approx(first["player_age"] - first["opponent_age"])


def test_clean_matches_male_results_and_ages(male_js):
    nadal = career_data._clean_matches(male_js, "Rafael Nadal", NADAL_BIRTH_DATE)
    assert list(nadal["result"]) == ["lost", "lost", "won"]
    assert nadal["player_age"].iloc[0] == pytest.approx(15.27, abs=0.01)
    assert nadal["opponent_age"].iloc[0] == pytest.approx(22.264202601)
    assert (nadal["age_difference"] < 0).all()  # Nadal was younger in all three


def test_clean_matches_is_sorted_by_date(female_js):
    rows = career_data._extract_match_rows(female_js)
    js_text = "var morematchmx = " + json.dumps(rows[::-1]) + ";"  # newest first
    serena = career_data._clean_matches(js_text, "Serena Williams", SERENA_BIRTH_DATE)
    assert serena["match_date"].is_monotonic_increasing
    assert serena["opponent"].iloc[0] == "Anne Miller"


def test_clean_matches_drops_match_with_missing_birth_date(female_js):
    js_text = female_js.replace('"19700503"', '""')  # Alexia Dechaume Balleret
    serena = career_data._clean_matches(js_text, "Serena Williams", SERENA_BIRTH_DATE)
    assert len(serena) == 2
    assert "Alexia Dechaume Balleret" not in set(serena["opponent"])


def test_clean_matches_drops_duplicate_rows(female_js):
    rows = career_data._extract_match_rows(female_js)
    js_text = "var morematchmx = " + json.dumps(rows + [rows[0]]) + ";"
    serena = career_data._clean_matches(js_text, "Serena Williams", SERENA_BIRTH_DATE)
    assert len(serena) == 3


def test_extract_player_info_reads_name_and_birth_date():
    full_name, birth_date = career_data._extract_player_info(MOCK_PLAYER_PAGE, "serena williams")
    assert full_name == "Serena Williams"
    assert birth_date == SERENA_BIRTH_DATE


def test_extract_player_info_without_birth_date_raises_error():
    page = MOCK_PLAYER_PAGE.replace("var dob = 19810926;", "")
    with pytest.raises(ValueError, match="date of birth of 'serena williams'"):
        career_data._extract_player_info(page, "serena williams")


def test_download_career_js_unknown_player_has_clear_message(monkeypatch):
    monkeypatch.setattr(career_data, "_download_text", not_found)
    with pytest.raises(ValueError, match="No career data found for player 'Gaston Sanchez'"):
        career_data._download_career_js("GastonSanchez", "Gaston Sanchez")


def test_download_career_js_builds_the_career_url(monkeypatch):
    requested_urls = []
    monkeypatch.setattr(career_data, "_download_text", lambda url: requested_urls.append(url) or "")
    career_data._download_career_js("SerenaWilliams", "serena williams")
    assert requested_urls == ["https://www.tennisabstract.com/jsmatches/SerenaWilliamsCareer.js"]


def test_download_text_turns_network_failure_into_connection_error(monkeypatch):
    def offline(*args, **kwargs):
        raise urllib.error.URLError("no internet")

    monkeypatch.setattr(urllib.request, "urlopen", offline)
    with pytest.raises(ConnectionError, match="check your internet connection"):
        career_data._download_text("https://www.tennisabstract.com/")


def fake_site(career_js):
    """Stand-in for tennisabstract.com that serves a mock career file and player page."""
    def download(url):
        return career_js if url.endswith("Career.js") else MOCK_PLAYER_PAGE
    return download


def test_get_career_data_end_to_end_with_mock_site(monkeypatch, female_js):
    monkeypatch.setattr(career_data, "_download_text", fake_site(female_js))
    serena = get_career_data("serena williams")
    assert list(serena.columns) == career_data.OUTPUT_COLUMNS
    assert len(serena) == 3
    assert set(serena["player"]) == {"Serena Williams"}  # full name from the player page


def test_get_career_data_unknown_player(monkeypatch):
    monkeypatch.setattr(career_data, "_download_text", not_found)
    with pytest.raises(ValueError, match="No career data found for player 'GastonSanchez'"):
        get_career_data("GastonSanchez")
