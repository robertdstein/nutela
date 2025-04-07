import pandas as pd
from planobs.api import Queue
from tabulate import tabulate

from nutela.slack import send_message


def post_ztf_queue():
    """
    Post the queue to Kowalski
    """
    q = Queue(user="NUTELA")

    all_queues = q.get_all_queues()
    df = pd.DataFrame([x for x in all_queues["data"]])
    df.drop(columns=["queue"], inplace=True)
    send_message(f"ZTF queue: \n {tabulate(df)} \n")
