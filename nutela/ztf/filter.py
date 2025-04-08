import tempfile

import matplotlib.pyplot as plt

from nutela.notice import AstrotrackNotice
from nutela.slack import send_image, send_message
from nutela.ztf.utils import get_planner


def select_alerts_ztf(nu: AstrotrackNotice) -> bool:
    """
    Function to determine whether an alert should be triggered.

    :param nu: GCN Notice
    :return: Boolean whether trigger criteria is met
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        plan = get_planner(nu=nu, temp_dir=tmpdir)

        schedule = plan.generate_schedule(constraints=plan.constraints)
        plan.plot_schedule(schedule, constraints=plan.constraints)
        plt.close()

        if not schedule:
            plan.generate_schedule(constraints=plan.constraints)

        send_image(plan.output_png_path)

    send_message(
        f"Neutrino galactic latitude is {plan.coordinates_galactic.b.deg:.1f}, "
        f"observable = {schedule.observable}"
    )

    return schedule.observable
