from nutela.notice import AstrotrackNotice
from planobs.slackbot import Slackbot
from planobs.plan import PlanObservation
from nutela.slack import CHANNEL, client, send_message, send_image
import matplotlib.pyplot as plt
from nutela.ztf import get_planner
from pathlib import Path

def schedule_ztf(nu: AstrotrackNotice):
    if nu.revision == 0:
        schedule_revision_0(nu)
    # elif nu.revision == 1:
    #     schedule_revision_1(nu)
    else:
        send_message(f"Unrecognised revision {nu.revision}, for notice {nu}")

def schedule_revision_0(nu: AstrotrackNotice):
    """
    Build a plan for revision 0 of the notice.

    :param nu: Neutrino notice
    :return: None
    """
    plan = get_planner(nu)

    plan.fields = plan.request_ztf_fields()
    plan.plot_fields()

    best_field = plan.recommended_field
    send_message(f"Best field is {best_field}")
    best_field_path = plan.grid_plot_path(fieldid=best_field)
    send_image(best_field_path)

