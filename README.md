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

## Usage

The package will have two public functions:

- `get_career_data(player_name)`: downloads a player's career matches from
  Tennis Abstract and returns a clean data frame (like the `serena` data frame
  of HW2). Accepts names such as `"serena williams"`, `"Serena Williams"` or
  `"SerenaWilliams"`, and gives a meaningful error for an unknown player.
- `plot_age_difference(career_data)`: makes the scatter plot of the player's
  age (x-axis) against the age difference with each opponent (y-axis), with
  points colored by match result.

```python
from tennisages import get_career_data, plot_age_difference

serena = get_career_data("serena williams")
plot_age_difference(serena)
```

*(Examples and output to be completed.)*

## Data

The data come from each player's career file on Tennis Abstract, e.g.
<https://www.tennisabstract.com/jsmatches/SerenaWilliamsCareer.js>.
Files of female players contain the opponents' dates of birth, from which their
ages are derived; files of male players already contain the opponents' ages.

*(Details of the cleaning steps to be completed.)*

## Package structure

*(To be completed.)*

## Running the tests

The tests use mock JS content and never contact tennisabstract.com.

*(Instructions to be completed.)*

## Reflections

*(To be completed.)*
