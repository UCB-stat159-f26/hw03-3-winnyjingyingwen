# tennisages

A Python package that downloads the career matches of a tennis player from
[Tennis Abstract](https://www.tennisabstract.com/) and plots the player's age
against the age difference with each opponent, in the style of the New York
Times graphic "Serena Williams's Professional Matches, Age 14 to 40" (HW3,
continuation of HW1 and HW2).

## Installation

```bash
pip install git+https://github.com/UCB-stat159-f26/hw03-3-winnyjingyingwen.git
```

This also installs the two dependencies, `pandas` and `matplotlib`
(Python 3.10 or newer).

## Usage

The package has two public functions:

| Function | Input | Output |
|---|---|---|
| `get_career_data(player_name)` | a player's name, e.g. `"serena williams"`, `"Serena Williams"` or `"SerenaWilliams"` | a clean `pandas.DataFrame`, one row per match |
| `plot_age_difference(career_data)` | the data frame returned by `get_career_data()` | a scatter plot (returns the matplotlib `Axes`) |

```python
from tennisages import get_career_data, plot_age_difference

# Serena Williams data and plot
serena = get_career_data("serena williams")
plot_age_difference(serena)

# Rafael Nadal data and plot
rafa = get_career_data("Rafael Nadal")
plot_age_difference(rafa)

# Unknown player: raises a ValueError with a meaningful message
unknown_player = get_career_data("GastonSanchez")
```

The last call stops with:

```
ValueError: No career data found for player 'GastonSanchez' (looked for
https://www.tennisabstract.com/jsmatches/GastonSanchezCareer.js). Check the
spelling, e.g. 'Serena Williams' or 'Rafael Nadal'. Note that not every player
has a career file on tennisabstract.com.
```

In Jupyter the plot is displayed automatically. In a Python script, add
`import matplotlib.pyplot as plt` and call `plt.show()` after
`plot_age_difference()`.

### The data frame

`get_career_data()` returns one row per match, sorted by date (for example,
1038 matches for Serena Williams and 1096 for Rafael Nadal):

| Column | Description |
|---|---|
| `player` | player's full name, e.g. `Serena Williams` |
| `match_date` | date of the match (the tournament's start date in the data) |
| `tournament`, `surface`, `round` | e.g. `Canadian Open`, `Carpet`, `Q1` |
| `result` | `won` or `lost`, from the player's point of view |
| `opponent` | opponent's name |
| `player_age` | player's age at the match, in years |
| `opponent_age` | opponent's age at the match, in years |
| `age_difference` | `player_age - opponent_age`; positive means the player was older |

### The plot

- **x-axis:** the player's age, shown along the top as in the NYT graphic
- **y-axis:** age difference with the opponent, labelled from "Same age" to
  "+20 years"
- **color:** light blue for matches the player won, purple for matches lost
- The title ("..., Age 14 to 40"), labels and axis limits adapt to each player.

## Data

The data come from each player's career file on Tennis Abstract, e.g.
<https://www.tennisabstract.com/jsmatches/SerenaWilliamsCareer.js>.
`get_career_data()` processes them in these steps:

1. **Name to URL.** `"serena williams"` becomes `SerenaWilliams`, the form used
   in Tennis Abstract's URLs. If no career file exists for that name
   (404 Not Found), a `ValueError` explains what went wrong.
2. **Player's birth date.** The career file does not contain the player's own
   birth date, so it is read from the player's page
   (e.g. `https://www.tennisabstract.com/cgi-bin/player.cgi?p=SerenaWilliams`,
   which defines `var dob = 19810926;`). In HW2 this date was typed in by hand.
3. **Match arrays.** The text after `var morematchmx =` is read as JSON, giving
   one list of fields per match. Only the needed fields are kept: date
   (position 0), tournament (1), surface (2), result (4), round (8),
   opponent (11) and opponent's birth date or age (16).
4. **Female vs. male files.** Position 16 holds the opponent's *birth date* in
   women's files (`"19770119"`) and the opponent's *age* in men's files
   (`"22.264202601"`). The package tells them apart from the values themselves
   (most values look like `YYYYMMDD` dates) and derives the age from the birth
   date when needed.
5. **Ages.** Ages are the number of days between two dates divided by 365.25.
6. **Cleaning.** Matches with a missing date, result or age are dropped, as are
   repeated rows (same date, tournament, round and opponent). The round is part
   of the key on purpose: at season-ending events a player can meet the same
   opponent twice, e.g. Serena Williams vs. Venus Williams in both the round
   robin and the final of the 2009 WTA Championships.

## Package structure

```
hw03-3-winnyjingyingwen/
├── .gitignore
├── README.md
├── instructions.md
├── pyproject.toml
└── tennisages/
    ├── __init__.py
    ├── career_data.py
    ├── age_plot.py
    └── tests/
        ├── __init__.py
        ├── conftest.py
        ├── test_career_data.py
        ├── test_age_plot.py
        └── data/
            ├── FemalePlayerCareer.js
            └── MalePlayerCareer.js
```

- `pyproject.toml`: package metadata and dependencies, used by `pip install`
- `tennisages/__init__.py`: makes the two public functions importable with
  `from tennisages import ...`
- `tennisages/career_data.py`: `get_career_data()` and its helpers
- `tennisages/age_plot.py`: `plot_age_difference()` and its helpers
- `tennisages/tests/`: the tests and the mock female and male JS files from
  the assignment instructions

### Functions

Public functions are at most 20 lines of code and private helpers (names
starting with `_`) at most 10, not counting docstrings, comments and blank
lines.

| Module | Function | What it does |
|---|---|---|
| `career_data` | `get_career_data` | **public:** download and clean a player's career matches |
| | `_format_player_name` | `"serena williams"` → `"SerenaWilliams"` |
| | `_capitalize` | capitalize a word, keeping inner capitals (`McEnroe`) |
| | `_download_text` | download a web page, with a readable connection error |
| | `_download_career_js` | download the career file; `ValueError` for unknown players |
| | `_extract_player_info` | player's full name and birth date from the player page |
| | `_extract_match_rows` | match arrays from the JS text |
| | `_rows_to_frame` | keep the needed fields in a data frame |
| | `_years_between` | time between dates, in years |
| | `_is_birth_date_column` | female file (birth dates) or male file (ages)? |
| | `_compute_opponent_age` | opponent's age at each match |
| | `_clean_matches` | assemble the clean data frame |
| | `_tidy_matches` | drop incomplete and repeated rows, sort by date |
| `age_plot` | `plot_age_difference` | **public:** NYT-style scatter plot |
| | `_check_career_data` | clear errors for input that cannot be plotted |
| | `_plot_matches` | draw the points for matches won (or lost) |
| | `_style_x_axis`, `_style_y_axis` | axis limits, ticks and labels |
| | `_y_tick_label` | `"Same age"`, `"+10"`, `"+20 years"` |
| | `_plot_title`, `_legend_label`, `_last_name` | title and legend text |

## Running the tests

```bash
git clone https://github.com/UCB-stat159-f26/hw03-3-winnyjingyingwen.git
cd hw03-3-winnyjingyingwen
pip install -e ".[test]"
pytest
```

The 39 tests never contact tennisabstract.com:

- The data-cleaning tests use the mock female and male JS content from the
  assignment (`tennisages/tests/data/`), e.g. Anne Miller's age (18.78) is
  derived from her birth date, while the men's ages are read directly.
- Downloads in `get_career_data()` are replaced by small stand-in functions
  (pytest's `monkeypatch`) to test the whole pipeline and the error for an
  unknown player.
- `tests/conftest.py` makes any real download fail, so no test can reach the
  live website by accident.
- The plot tests check the title, labels, legend, points and error messages
  on a small made-up data frame.

## Notes and limitations

- Names are matched to Tennis Abstract's URL format by capitalizing each word
  and removing spaces. Unusual spellings may need to be typed as in the site's
  URL (e.g. `"JohnMcEnroe"`).
- Not every player has a career file on Tennis Abstract; for those players
  `get_career_data()` raises the same "No career data found" error.
- Ages use 365.25-day years, so they can differ from exact ages by a day.
- Match dates in the data are tournament start dates, as in HW2.

## Reflections
In HW 3, I learned how detail-oriented and patient we need to be in order to turn
our code into a package that other people can actually install and use. Small details turned out to matter a lot, such as an empty file that I
committed by accident because I forgot to save it or a dependency missing from the package settings. Any of these can break the package or confuse the person using it.
I also learned to slow down and understand what every file is for, instead
of just making the code run. Writing tests and committing one small step at a time taught me to build the project piece by piece. Each step had to pass its tests before I moved on, which made mistakes much easier to find.
