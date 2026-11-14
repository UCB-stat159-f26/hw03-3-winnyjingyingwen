"""Scatter plot of a player's career matches.

x-axis: the player's age at each match; y-axis: the player's age minus the
opponent's age; colour: whether the player won or lost the match.

Only ``plot_age_difference()`` is public.
"""

import math
import matplotlib.pyplot as plt
import pandas as pd

RESULT_COLORS = {"won": "#5BC0E3", "lost": "#7B2D8E"}  # light blue, purple (NYT)
REQUIRED_COLUMNS = ["player", "player_age", "age_difference", "result"]
FIGURE_SIZE = (10, 6)
POINT_SIZE = 14
POINT_ALPHA = 0.7
X_TICK_STEP = 2   
Y_TICK_STEP = 10 
Y_MARGIN = 1     
TITLE_PAD = 48    
SOURCE_NOTE = "Source: Tennis Abstract (tennisabstract.com)."
SOURCE_POSITION = (0.01, 0.01)  


def plot_age_difference(career_data):
    """Scatter plot of a player's age vs. the age gap with each opponent.

    career_data: the data frame returned by get_career_data(). Returns the
    matplotlib Axes (call plt.show() in a script); raises TypeError or
    ValueError if career_data cannot be plotted.
    """
    _check_career_data(career_data)
    player = career_data["player"].iloc[0]
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    ax.axhline(0, color="grey", linewidth=1)
    for result, color in RESULT_COLORS.items():
        matches = career_data[career_data["result"] == result]
        _plot_matches(ax, matches, color, _legend_label(result, player))
    _style_x_axis(ax, career_data["player_age"], player)
    _style_y_axis(ax, career_data["age_difference"])
    ax.set_title(_plot_title(player, career_data["player_age"]),
                 fontsize=14, fontweight="bold", pad=TITLE_PAD)
    ax.legend(loc="upper left", frameon=False)
    fig.text(*SOURCE_POSITION, SOURCE_NOTE, fontsize=8, color="grey")
    return ax


def _check_career_data(career_data):
    """Raise a helpful error if career_data cannot be plotted."""
    if not isinstance(career_data, pd.DataFrame):
        raise TypeError(f"career_data must be the data frame returned by get_career_data(), "
                        f"not {type(career_data).__name__}")
    missing = [column for column in REQUIRED_COLUMNS if column not in career_data.columns]
    if missing:
        raise ValueError(f"career_data is missing the column(s) {missing}; create it with get_career_data()")
    if career_data.empty:
        raise ValueError("career_data has no matches to plot")


def _plot_matches(ax, matches, color, label):
    """Add one group of points (matches won, or matches lost) to the plot."""
    ax.scatter(matches["player_age"], matches["age_difference"], color=color,
               s=POINT_SIZE, alpha=POINT_ALPHA, linewidths=0, label=label)


def _last_name(player):
    """'Serena Williams' -> 'Williams'."""
    return player.split()[-1]


def _legend_label(result, player):
    """'Match Williams won' or 'Match lost', as in the NYT legend."""
    return f"Match {_last_name(player)} won" if result == "won" else "Match lost"


def _plot_title(player, player_ages):
    """e.g. "Serena Williams's Professional Matches, Age 14 to 40"."""
    first_age, last_age = math.floor(player_ages.min()), math.floor(player_ages.max())
    return f"{player}'s Professional Matches, Age {first_age} to {last_age}"


def _style_x_axis(ax, player_ages, player):
    """Player's age along the top of the plot, with a tick every two years."""
    low, high = math.floor(player_ages.min()), math.ceil(player_ages.max())
    ax.set_xlim(low, high)
    ax.set_xticks(range(low + low % X_TICK_STEP, high + 1, X_TICK_STEP))
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax.set_xlabel(f"{_last_name(player)}'s age")


def _style_y_axis(ax, age_differences):
    """Symmetric age-difference axis labelled '-10', 'Same age', '+20 years'."""
    largest_gap = age_differences.abs().max()
    top_tick = Y_TICK_STEP * max(1, math.floor(largest_gap / Y_TICK_STEP))
    ticks = list(range(-top_tick, top_tick + 1, Y_TICK_STEP))
    y_limit = max(largest_gap, top_tick) + Y_MARGIN
    ax.set_ylim(-y_limit, y_limit)
    ax.set_yticks(ticks)
    ax.set_yticklabels([_y_tick_label(tick, top_tick) for tick in ticks])
    ax.set_ylabel("Age difference with opponent (Older / Younger)")


def _y_tick_label(tick, top_tick):
    """'Same age' at 0, signed numbers elsewhere, and 'years' on the top tick."""
    if tick == 0:
        return "Same age"
    label = f"{tick:+d}"
    return f"{label} years" if tick == top_tick else label

