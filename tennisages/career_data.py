"""Download and clean a player's career match data from tennisabstract.com.

Tennis Abstract stores a player's career matches in a JavaScript file, such as SerenaWilliamsCareer.js.
This module downloads the file and calculates the player's age, their opponent's age, and the age difference for each match.


Only ``get_career_data()`` is the only public function.
"""

import json
import re


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
