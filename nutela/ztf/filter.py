from nutela.notice import AstrotrackNotice
from planobs.slackbot import Slackbot
from planobs.plan import PlanObservation
from nutela.slack import CHANNEL, client, send_message, send_image
import matplotlib.pyplot as plt
from pathlib import Path
from nutela.ztf.utils import get_planner


def select_alerts_ztf(nu: AstrotrackNotice) -> bool:
    """
    Function to determine whether an alert should be triggered.

    :param nu: GCN Notice
    :return: Boolean whether trigger criteria is met
    """

    plan = get_planner(nu=nu)
    plan.plot_target()
    plt.close()

    send_image(plan.output_png_path)

    return plan.observable

