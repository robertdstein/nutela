from astropy.time import Time
from planobs.api import Queue
from planobs.models import Observation, TooTarget

from nutela.notice import AstrotrackNotice
from nutela.slack import send_message

ZTF_FILTER_IDS = {
    "g": 1,
    "r": 2,
    "i": 3,
}


def submit_ztf(observations: list[Observation], nu: AstrotrackNotice, field_id: int):
    """
    Submit a ZTF schedule to the ZTF scheduler.

    :param observations
    :return: None
    """
    base_name = f"ToO_IC_{nu.run_num}_{nu.event_num}_rev{nu.revision}"

    q = Queue(user="NUTELA")

    existing_triggers = [x for x in q.get_all_queues_nameonly() if base_name in x]

    if len(existing_triggers) > 0:
        send_message(
            f"Found {len(existing_triggers)} triggers, will delete these before submitting new ones"
        )
        for trigger in existing_triggers:
            q.delete_trigger(trigger)

    for obs in observations:
        q.add_trigger_to_queue(
            trigger_name=f"{base_name}",
            validity_window_start_mjd=obs.start_time.mjd,
            validity_window_end_mjd=obs.end_time.mjd,
            targets=[
                TooTarget(
                    field_id=field_id,
                    filter_id=ZTF_FILTER_IDS[obs.filter_name],
                    exposure_time=obs.exposure_time,
                    program_pi="Stein",
                )
            ],
        )

    send_message(f"Sending {q.get_triggers()} triggers to ZTF queue")
