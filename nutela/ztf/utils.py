#!/usr/bin/env python3
# Author: Simeon Reusch (simeon.reusch@desy.de)
# License: BSD-3-Clause
from astropy import units as u  # type: ignore
from astropy.coordinates import EarthLocation  # type: ignore
from astropy.time import Time  # type: ignore
from slack import WebClient  # type: ignore
from nutela.slack import CHANNEL, client
from planobs.plan import PlanObservation
from planobs.models import Position

SITE_ZTF = "Palomar"

def get_planner(nu, multiday: bool = False) -> PlanObservation:
    """
    Convert a neutrino notice into a plan for observation.

    :param nu: Neutrino Notice
    :param multiday: Plan Multiday
    :return: PlanObs
    """

    name = "ICTEST"


    ic_date_name = str(nu.event_time.isot).split("T")[0]#.replace("-", "")[2:]

    source = f"Notice {nu.revision}\n"

    position = Position.from_circle(ra=nu.src_ra, dec=nu.src_dec, err_radius=nu.src_error)

    plan = PlanObservation(
        channel=CHANNEL,
        name=name,
        position=position,
        date=ic_date_name,
        max_airmass=2.0,
        multiday=multiday,
        submit_trigger=False,
        alertsource=source,
        site=SITE_ZTF,
        signalness=nu.signalness,
    )
    return plan