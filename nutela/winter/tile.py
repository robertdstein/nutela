import matplotlib
import numpy as np
import pandas as pd
from nuwinter.neutrino import get_square
from wintertoo.data import WINTER_BASE_WIDTH
from wintertoo.fields import plot_fields

from nutela.notice import AstrotrackNotice
from nutela.slack import send_message
from nutela.winter.utils import get_bounds

ALL_MODES = ["best", "square", "single"]


def find_single(
    nu: AstrotrackNotice,
) -> tuple[pd.DataFrame, matplotlib.axes.Axes]:
    """
    Find the single best field for the neutrino alert.

    :param nu: Neutrino alert
    :return:
    """
    ra_lim, dec_lim = get_bounds(nu)

    res = pd.DataFrame({"RA": [np.mean(ra_lim)], "Dec": [np.mean(dec_lim)]})

    ax = plot_fields(res, ra_lim, dec_lim)
    return res, ax


def find_square(
    nu: AstrotrackNotice,
) -> tuple[pd.DataFrame, matplotlib.axes.Axes]:
    """
    Find the square field for the neutrino alert.

    :param nu: Neutrino alert
    :return:
    """
    ra_lim, dec_lim = get_bounds(nu)
    res = get_square(ra_lim, dec_lim)
    ax = plot_fields(res, ra_lim, dec_lim)
    return res, ax


def get_tiles(
    nu: AstrotrackNotice, mode: str | None = None
) -> tuple[pd.DataFrame, matplotlib.axes.Axes]:
    """
    Get the tiles for the neutrino alert.

    :param nu: GCN Notice
    :param mode: Mode to use for selecting tiles
    :return: DataFrame of tiles and matplotlib axes
    """
    # Choose the mode based on the neutrino error
    if mode is None:
        if nu.src_error > WINTER_BASE_WIDTH:
            mode = "square"
        else:
            mode = "single"
        send_message(
            f"Neutrino error is {nu.src_error:.1f} degrees, using mode `{mode}`"
        )

    if mode not in ALL_MODES:
        raise ValueError(f"Mode {mode} not in {ALL_MODES}")

    if mode == "square":
        return find_square(nu)
    elif mode == "single":
        return find_single(nu)
    else:
        raise ValueError(f"Unknown mode {mode}")
