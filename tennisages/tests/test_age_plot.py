"""Tests for tennisages.age_plot (no network, no windows: Agg backend)."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt 
import pandas as pd 
import pytest 

from tennisages import plot_age_difference 
from tennisages import age_plot  

@pytest.fixture(autouse=True)
def close_figures():
    """Close the figures created by each test."""
    yield
    plt.close("all")


@pytest.fixture
def career_data():
    """Small data frame shaped like the output of get_career_data()."""
    return pd.DataFrame({
        "player": ["Serena Williams"] * 4,
        "player_age": [14.1, 15.4, 22.0, 40.9],
        "age_difference": [-4.7, -11.4, 0.5, 21.7],
        "result": ["lost", "won", "won", "won"],
    })


def test_plot_returns_axes_with_won_and_lost_points(career_data):
    ax = plot_age_difference(career_data)
    won_points, lost_points = (collection.get_offsets() for collection in ax.collections)
    assert len(won_points) == 3
    assert len(lost_points) == 1
    assert tuple(lost_points[0]) == pytest.approx((14.1, -4.7))


def test_plot_labels_follow_the_nyt_graphic(career_data):
    ax = plot_age_difference(career_data)
    assert ax.get_title() == "Serena Williams's Professional Matches, Age 14 to 40"
    assert ax.get_xlabel() == "Williams's age"
    y_labels = [label.get_text() for label in ax.get_yticklabels()]
    assert y_labels == ["-20", "-10", "Same age", "+10", "+20 years"]
    legend = [text.get_text() for text in ax.get_legend().get_texts()]
    assert legend == ["Match Williams won", "Match lost"]


def test_plot_shows_every_point(career_data):
    ax = plot_age_difference(career_data)
    low, high = ax.get_ylim()
    assert low < career_data["age_difference"].min()
    assert high > career_data["age_difference"].max()


def test_y_tick_label():
    assert age_plot._y_tick_label(0, 20) == "Same age"
    assert age_plot._y_tick_label(-10, 20) == "-10"
    assert age_plot._y_tick_label(10, 20) == "+10"
    assert age_plot._y_tick_label(20, 20) == "+20 years"


def test_plot_rejects_non_data_frame():
    with pytest.raises(TypeError, match="get_career_data"):
        plot_age_difference([1, 2, 3])


def test_plot_rejects_missing_columns(career_data):
    with pytest.raises(ValueError, match="age_difference"):
        plot_age_difference(career_data.drop(columns="age_difference"))


def test_plot_rejects_empty_data(career_data):
    with pytest.raises(ValueError, match="no matches"):
        plot_age_difference(career_data.iloc[0:0])
