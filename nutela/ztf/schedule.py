import tempfile

from astropy import units as u
from planobs.models import ObservingConstraints

from nutela.notice import AstrotrackNotice
from nutela.slack import send_image, send_message
from nutela.ztf.submit import submit_ztf
from nutela.ztf.utils import get_planner

BASE_CONSTRAINTS_KWARGS = {
    "site_name": "Palomar",
}

# Less stringent constraints for later nights
LOOSE_CONSTRAINTS_KWARGS = {
    "max_airmass": 3.0,
    "separation_time": 0.0,
}


def schedule_ztf(nu: AstrotrackNotice, debug: bool = False):
    """
    Schedule a ZTF observation for a neutrino notice.

    :param nu: Neutrino notice
    :param debug: Debug flag
    :return: None
    """
    if nu.revision == 0:
        schedule_revision_0(nu, debug=debug)
    elif nu.revision == 1:
        schedule_revision_1(nu, debug=debug)
    else:
        send_message(f"Unrecognised revision {nu.revision}, for notice {nu}")


def schedule_revision_0(nu: AstrotrackNotice, debug: bool = False):
    """
    Build a plan for revision 0 of the notice.

    :param nu: Neutrino notice
    :param debug: Debug flag
    :return: None
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        plan = get_planner(nu, temp_dir=tmpdirname)

        all_fields = plan.request_ztf_fields()
        plan.plot_ztf_fields()

        for field_id in all_fields:
            best_field_path = plan.grid_plot_path(fieldid=field_id)
            send_image(best_field_path)

    best_field = plan.recommended_field
    send_message(f"Best ZTF field is {best_field}, options were {all_fields}")

    constraints = ObservingConstraints(
        bands=["g", "r"], exposure_time=300.0, **BASE_CONSTRAINTS_KWARGS
    )

    schedule = plan.generate_schedule(constraints=constraints)
    if not schedule.observable:
        send_message(f"No observable fields: {schedule.rejection_reason}")
        return

    submit_ztf(schedule.observations, nu, field_id=best_field, debug=debug)


def schedule_revision_1(nu: AstrotrackNotice, debug: bool = False):
    """
    Build a plan for revision 1 of the notice.

    :param nu: Neutrino notice
    :return: None
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        plan = get_planner(nu, temp_dir=tmpdirname)

        plan.request_ztf_fields()
        plan.plot_ztf_fields()

        best_field = plan.recommended_field
        send_message(f"Best ZTF field is {best_field}")
        best_field_path = plan.grid_plot_path(fieldid=best_field)
        send_image(best_field_path)

    time_ref = nu.event_time

    all_obs = []

    for night in [1, 2, 3, 5, 7]:
        constraints = ObservingConstraints(
            bands=["g"],
            exposure_time=30.0,
            start_time=time_ref + night * u.day,
            **BASE_CONSTRAINTS_KWARGS,
            **LOOSE_CONSTRAINTS_KWARGS,
        )

        new = plan.generate_schedule(constraints=constraints)
        all_obs += new.observations

    for night in [9]:
        constraints = ObservingConstraints(
            bands=["g", "r"],
            exposure_time=300.0,
            start_time=time_ref + night * u.day,
            **BASE_CONSTRAINTS_KWARGS,
            **LOOSE_CONSTRAINTS_KWARGS,
        )
        all_obs += plan.generate_schedule(constraints=constraints).observations

    submit_ztf(all_obs, nu, field_id=best_field, debug=debug)
