from pathlib import Path

import matplotlib.pyplot as plt
from planobs.plan import PlanObservation
from planobs.slackbot import Slackbot

from nutela.notice import AstrotrackNotice
from nutela.slack import CHANNEL, client, send_image, send_message
from nutela.ztf.utils import get_planner


def select_alerts_ztf(nu: AstrotrackNotice) -> bool:
    """
    Function to determine whether an alert should be triggered.

    :param nu: GCN Notice
    :return: Boolean whether trigger criteria is met
    """

    plan = get_planner(nu=nu)

    schedule = plan.generate_schedule(constraints=plan.constraints)
    plan.plot_schedule(schedule, constraints=plan.constraints)
    plt.close()

    send_image(plan.output_png_path)

    return schedule.observable
