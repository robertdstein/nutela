import logging

import matplotlib
import numpy as np
import pandas as pd
from nuwinter.neutrino import get_square
from nuztf.parse_nu_gcn import find_gcn_no, parse_gcn_circular
from wintertoo.fields import plot_fields

from nutela.notice import AstrotrackNotice
from nutela.winter.utils import get_bounds


def get_tiles(
    nu: AstrotrackNotice,
) -> tuple[pd.DataFrame, matplotlib.axes.Axes]:

    ra_lim, dec_lim = get_bounds(nu)

    res = get_square(ra_lim, dec_lim)

    ax = plot_fields(res, ra_lim, dec_lim)

    return res, ax
