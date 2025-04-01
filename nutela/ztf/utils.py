#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause
from astropy import units as u  # type: ignore
from astropy.coordinates import EarthLocation  # type: ignore
from astropy.time import Time  # type: ignore
from planobs.models import Localisation
from planobs.plan import PlanObservation
from slack import WebClient  # type: ignore

from nutela.slack import CHANNEL, client

SITE_ZTF = "Palomar"


def get_planner(nu) -> PlanObservation:
    """
    Convert a neutrino notice into a plan for observation.

    :param nu: Neutrino Notice
    :return: PlanObs
    """

    ic_date_name, time = str(nu.event_time.isot).split("T")  # .replace("-", "")[2:]

    fractional_day = (
        float(time.split(":")[0]) / 24.0
        + float(time.split(":")[1]) / 1440.0
        + float(time.split(":")[2]) / 86400.0
    )

    base_name = f"IC{ic_date_name[2:].replace('-','')}+{fractional_day:.3f}"

    localisation = Localisation.from_circle(
        ra=nu.src_ra,
        dec=nu.src_dec,
        err_radius=nu.src_error,
        signalness=nu.signalness,
        trigger_time=nu.event_time,
    )

    plan = PlanObservation(
        name=base_name,
        localisation=localisation,
    )
    return plan
