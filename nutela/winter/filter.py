from pathlib import Path

import matplotlib.pyplot as plt
from planobs.models import ObservingConstraints
from planobs.plan import PlanObservation
from planobs.slackbot import Slackbot

from nutela.notice import AstrotrackNotice
from nutela.slack import CHANNEL, client, send_image, send_message
from nutela.ztf.utils import get_planner

BASE_CONSTRAINTS_KWARGS = {
    "site_name": "Palomar",
    "min_galactic_latitude": 0.0,
    "bands": ["J"],
    "exposure_time": 8.0 * 120.0,
}


def select_alerts_winter(nu: AstrotrackNotice) -> bool:
    """
    Function to determine whether an alert should be triggered.

    :param nu: GCN Notice
    :return: Boolean whether trigger criteria is met
    """

    plan = get_planner(nu=nu)

    constraints = ObservingConstraints(**BASE_CONSTRAINTS_KWARGS)

    schedule = plan.generate_schedule(constraints=constraints)
    plan.plot_schedule(schedule, constraints=constraints)
    plt.close()

    send_image(plan.output_png_path)

    send_message(
        f"Neutrino galactic latitude is {plan.coordinates_galactic.b.deg:.1f}, "
        f"observable = {schedule.observable}"
    )

    return schedule.observable
