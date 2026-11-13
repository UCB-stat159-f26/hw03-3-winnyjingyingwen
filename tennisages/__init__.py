"""tennisages: plot a tennis player's age against their opponents' ages."""

from tennisages.age_plot import plot_age_difference
from tennisages.career_data import get_career_data

__version__ = "0.1.0"
__all__ = ["get_career_data", "plot_age_difference"]
