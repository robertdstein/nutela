import pandas as pd
from planobs.api import Queue
from planobs.models import Observation, TooTarget
from tabulate import tabulate

from nutela.notice import AstrotrackNotice
from nutela.slack import send_message

ZTF_FILTER_IDS = {
    "g": 1,
    "r": 2,
    "i": 3,
}


def format_planobs_queue(res: list[dict]) -> pd.DataFrame:
    """
    Format the planobs queue for display.

    :param res: ZTF queue response
    :return: DataFrame of the ZTF queue
    """
    triggers = []
    for x in res:
        data = x[1]
        data.update(**data["targets"][0])
        triggers.append(data)

    df = pd.DataFrame(triggers)
    df.drop(
        columns=[
            "user",
            "queue_type",
            "targets",
            "subprogram_name",
            "request_id",
            "program_pi",
            "program_id",
        ],
        inplace=True,
    )
    return df


def submit_ztf(
    observations: list[Observation],
    nu: AstrotrackNotice,
    field_id: int,
    debug: bool = False,
):
    """
    Submit a ZTF schedule to the ZTF scheduler.

    :param observations
    :param nu: GCN Notice
    :param field_id: Field ID
    :param debug: Debug mode
    :return: None
    """
    base_name = f"ToO_IC_{nu.run_num}_{nu.event_num}_rev{nu.revision}"

    q = Queue(user="NUTELA")

    existing_triggers = [x for x in q.get_all_queues_nameonly() if base_name in x]

    if (len(existing_triggers) > 0) & (not debug):
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

    df = format_planobs_queue(q.get_triggers())

    str_table = f"\n ```{tabulate(df, headers=df.columns)}``` \n"

    if debug:
        send_message(
            f"DEBUG MODE, not submitting. \n Would submit triggers to ZTF queue: {str_table}"
        )
    else:
        send_message(f"Sending triggers to ZTF queue: {str_table}")
        q.submit_queue()
