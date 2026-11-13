"""Download and clean a player's career match data from tennisabstract.com.

Tennis Abstract stores a player's career matches in a JavaScript file, such as SerenaWilliamsCareer.js.
This module downloads the file and calculates the player's age, their opponent's age, and the age difference for each match.


Only ``get_career_data()`` is the only public function.
"""

import json
import re

import pandas as pd

DATE_FORMAT = "%Y%m%d"  # dates in the JS files look like "19951030"
DAYS_PER_YEAR = 365.25

# Position of each field we need inside one match array of the JS file.
MATCH_FIELDS = {
    "match_date": 0,      # e.g. "19951030"
    "tournament": 1,      # e.g. "Canadian Open"
    "surface": 2,         # e.g. "Carpet"
    "result": 4,          # "W" = player won, "L" = player lost
    "round": 8,           # e.g. "Q1", "R32", "F"
    "opponent": 11,       # e.g. "Anne Miller"
    "opponent_info": 16,  # women's files: birth date "19770119"; men's: age "22.26"
}
RESULT_LABELS = {"W": "won", "L": "lost"}
OUTPUT_COLUMNS = [
    "player", "match_date", "tournament", "surface", "round", "result",
    "opponent", "player_age", "opponent_age", "age_difference",
]


def _format_player_name(player_name):
    """Turn "serena williams" or "Serena Williams" into "SerenaWilliams".
    """
    if not isinstance(player_name, str):
        raise TypeError(f"player_name must be a string, not {type(player_name).__name__}")
    if not player_name.strip():
        raise ValueError("player_name is empty; use a name such as 'Serena Williams'")
    words = re.split(r"[\s-]+", player_name.strip())
    return "".join(_capitalize(word) for word in words)


def _capitalize(word):
    """Upper-case the first letter, keeping inner capitals as in "McEnroe"."""
    if word.isupper() or word.islower():
        return word.capitalize()
    return word[0].upper() + word[1:]


def _extract_match_rows(career_js):
    """Return the list of match arrays stored in the career JS text.

    The text looks like ``var morematchmx = [["19951030", ...], [...]];``.
    The part after ``=`` is valid JSON once trailing commas are removed.
    """
    array_match = re.search(r"=\s*(\[.*\])", career_js, flags=re.DOTALL)
    if array_match is None:
        raise ValueError("No match array ('var morematchmx = [...]') found in the career JS text")
    array_text = re.sub(r",\s*\]", "]", array_match.group(1))  # drop trailing commas
    return json.loads(array_text)


def _rows_to_frame(match_rows):
    """Build a data frame with the fields in MATCH_FIELDS, one row per match.

    Rows too short to contain every field are skipped.
    """
    min_length = max(MATCH_FIELDS.values()) + 1
    rows = [row for row in match_rows if len(row) >= min_length]
    columns = {field: [row[index] for row in rows] for field, index in MATCH_FIELDS.items()}
    return pd.DataFrame(columns)


def _years_between(start_dates, end_dates):
    """Number of years (of 365.25 days) from start_dates to end_dates."""
    return (end_dates - start_dates).dt.days / DAYS_PER_YEAR


def _is_birth_date_column(opponent_info):
    """Tell whether opponent_info holds birth dates (women) or ages (men).

    Women's career files store each opponent's birth date ("19770119"),
    while men's files store the opponent's age ("22.264202601"). Returns
    True when most of the non-empty values look like YYYYMMDD dates.
    """
    known_values = opponent_info[opponent_info != ""]
    return bool(known_values.str.fullmatch(r"\d{8}").mean() > 0.5)


def _compute_opponent_age(opponent_info, match_dates):
    """Opponent's age in years at each match (NaN when it is unknown)."""
    if _is_birth_date_column(opponent_info):
        birth_dates = pd.to_datetime(opponent_info, format=DATE_FORMAT, errors="coerce")
        return _years_between(birth_dates, match_dates)
    return pd.to_numeric(opponent_info, errors="coerce")


def _clean_matches(career_js, player_name, player_birth_date):
    """Turn the raw career JS text into the data frame used for plotting.

    ``age_difference`` is the player's age minus the opponent's age, so a
    positive value means the player was older than the opponent.
    """
    matches = _rows_to_frame(_extract_match_rows(career_js))
    matches["match_date"] = pd.to_datetime(matches["match_date"], format=DATE_FORMAT, errors="coerce")
    matches["result"] = matches["result"].map(RESULT_LABELS)
    matches["player"] = player_name
    matches["player_age"] = _years_between(player_birth_date, matches["match_date"])
    matches["opponent_age"] = _compute_opponent_age(matches["opponent_info"], matches["match_date"])
    matches["age_difference"] = matches["player_age"] - matches["opponent_age"]
    return _tidy_matches(matches)


def _tidy_matches(matches):
    """Drop incomplete or repeated matches, sort by date, keep OUTPUT_COLUMNS."""
    matches = matches.dropna(subset=["match_date", "result", "age_difference"])
    matches = matches.drop_duplicates(subset=["match_date", "tournament", "round", "opponent"])
    matches = matches.sort_values("match_date", kind="stable")
    return matches[OUTPUT_COLUMNS].reset_index(drop=True)


def _extract_player_info(player_page, player_name):
    """Return the player's full name and birth date from their profile page.

    The page defines JavaScript variables such as
    ``var fullname = 'Serena Williams';`` and ``var dob = 19810926;``.
    """
    dob_match = re.search(r"var dob\s*=\s*'?(\d{8})'?\s*;", player_page)
    if dob_match is None:
        raise ValueError(f"Could not find the date of birth of '{player_name}' on tennisabstract.com")
    name_match = re.search(r"var fullname\s*=\s*'([^']+)'", player_page)
    full_name = name_match.group(1) if name_match else player_name
    return full_name, pd.to_datetime(dob_match.group(1), format=DATE_FORMAT)
