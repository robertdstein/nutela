"""
Module to interact with the ZTF queue.
"""

import json

import pandas as pd
from planobs.api import Queue
from tabulate import tabulate

from nutela.slack import send_message


def format_ztf_queue(res: list[dict]) -> pd.DataFrame:
    """
    Format the ZTF queue for display.

    :param res: ZTF queue response
    :return: DataFrame of the ZTF queue
    """
    triggers = []
    for x in res:
        data = x
        data["n_entries"] = len(data["queue"])
        entries = json.loads(data["queue"])
        data.update(**entries[0] if len(entries) > 0 else {})
        triggers.append(data)

    df = pd.DataFrame(triggers)
    if len(df) > 0:

        cols = [
            x
            for x in [
                "queue_name",
                "validity_window_mjd",
                "is_TOO",
                "n_entries",
                "field_id",
                "filter_id",
                "exposure_time",
                "max_airmass",
            ]
            if x in df.columns
        ]
        df = df[cols]
    return df


def get_ztf_queue() -> pd.DataFrame:
    """
    Get the ZTF queue for display

    :return: DataFrame of the ZTF queue
    """
    q = Queue(user="NUTELA")

    data = q.get_too_queues()["data"]

    return format_ztf_queue(data)


def post_ztf_queue():
    """
    Post the queue to Kowalski
    """
    try:
        df = get_ztf_queue()
        if len(df) > 0:
            send_message(
                f"ZTF ToO queue:  \n```{tabulate(df, headers=df.columns)} ``` \n"
            )
        else:
            send_message("ZTF ToO queue is currently empty.")
    except Exception as e:
        send_message(f"Error fetching ZTF ToO queue: {e}")
