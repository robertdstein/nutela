import numpy as np

from nutela.notice import AstrotrackNotice


def get_bounds(nu: AstrotrackNotice):
    """
    Get the bounds of the neutrino alert
    """
    # Get the bounds of the neutrino alert

    dec_lim = (nu.src_dec - nu.src_error, nu.src_dec + nu.src_error)

    dec_factor = np.cos(np.radians(nu.src_dec))

    ra_lim = (
        nu.src_ra - nu.src_error * dec_factor,
        nu.src_ra + nu.src_error * dec_factor,
    )

    return ra_lim, dec_lim
