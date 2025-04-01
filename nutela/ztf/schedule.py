from astroplan import Schedule
from astropy import units as u
from astropy.time import Time
from planobs.models import ObservingConstraints

from nutela.notice import AstrotrackNotice
from nutela.slack import send_image, send_message
from nutela.ztf import get_planner
from nutela.ztf.submit import submit_ztf

BASE_CONSTRAINTS_KWARGS = {
    "site_name": "Palomar",
}


def schedule_ztf(nu: AstrotrackNotice):
    """
    Schedule a ZTF observation for a neutrino notice.

    :param nu: Neutrino notice
    :return: None
    """
    if nu.revision == 0:
        schedule_revision_0(nu)
    elif nu.revision == 1:
        schedule_revision_1(nu)
    else:
        send_message(f"Unrecognised revision {nu.revision}, for notice {nu}")


def schedule_revision_0(nu: AstrotrackNotice):
    """
    Build a plan for revision 0 of the notice.

    :param nu: Neutrino notice
    :return: None
    """
    plan = get_planner(nu)

    plan.request_ztf_fields()
    plan.plot_ztf_fields()

    best_field = plan.recommended_field
    send_message(f"Best ZTF field is {best_field}")
    best_field_path = plan.grid_plot_path(fieldid=best_field)
    send_image(best_field_path)

    constraints = ObservingConstraints(
        bands=["g", "r"], exposure_time=300.0, **BASE_CONSTRAINTS_KWARGS
    )

    schedule = plan.generate_schedule(constraints=constraints)
    if not schedule.observable:
        send_message(f"No observable fields: {schedule.rejection_reason}")
        return

    submit_ztf(schedule.observations, nu, field_id=best_field)


def schedule_revision_1(nu: AstrotrackNotice):
    """
    Build a plan for revision 1 of the notice.

    :param nu: Neutrino notice
    :return: None
    """
    plan = get_planner(nu)

    plan.request_ztf_fields()
    plan.plot_ztf_fields()

    best_field = plan.recommended_field
    send_message(f"Best ZTF field is {best_field}")
    best_field_path = plan.grid_plot_path(fieldid=best_field)
    send_image(best_field_path)

    time_now = Time.now()

    all_obs = []

    for night in [1, 2, 3, 5, 7]:
        constraints = ObservingConstraints(
            bands=["g"],
            exposure_time=30.0,
            start_time=time_now + night * u.day,
            **BASE_CONSTRAINTS_KWARGS,
        )
        all_obs += plan.generate_schedule(constraints=constraints).observations

    for night in [9]:
        constraints = ObservingConstraints(
            bands=["g", "r"],
            exposure_time=300.0,
            start_time=time_now + night * u.day,
            **BASE_CONSTRAINTS_KWARGS,
        )
        all_obs += plan.generate_schedule(constraints=constraints).observations

    submit_ztf(all_obs, nu, field_id=best_field)
