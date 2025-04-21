import tempfile

import matplotlib.pyplot as plt

from nutela.notice import AstrotrackNotice
from nutela.slack import send_image, send_message
from nutela.ztf.utils import get_planner

MAX_AREA_ZTF = 10.0


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

    # Reject if the area is too large
    if nu.area_square > MAX_AREA_ZTF:
        send_message(
            f"Neutrino area ({nu.area_square:.1f} sq deg) is larger than maximum "
            f"({MAX_AREA_ZTF:.1f} sq deg), skipping ZTF observation."
        )
        return False

    send_message(
        f"Neutrino galactic latitude is {plan.coordinates_galactic.b.deg:.1f}, "
        f"observable = {schedule.observable}"
    )

    return schedule.observable
