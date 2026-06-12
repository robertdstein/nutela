"""
Module to check the Winter neutrino program and its queue.
"""

import os

import pandas as pd
from tabulate import tabulate
from winterapi import WinterAPI

from nutela.slack import send_message

WINTER_PROGRAM_NAME = os.getenv("WINTER_PROGRAM_NAME", "2024A001")
WINTER_PROGRAM_KEY = os.getenv("WINTER_PROGRAM_KEY", None)


def check_winter_program():
    """
    Check if the Winter neutrino program is available.

    :return: None
    """
    winter = WinterAPI()

    try:
        print(f"User is {winter.get_user()}")
    except KeyError:
        print("No user credentials found. Please add these first!")
        winter.add_user_details(overwrite=True)

    program_list = winter.get_programs()
    print(f"Available programs: {program_list}")

    if WINTER_PROGRAM_NAME not in program_list:
        print("Winter neutrino program not available. Adding it now.")
        winter.add_program(
            program_name=WINTER_PROGRAM_NAME,
            program_api_key=WINTER_PROGRAM_KEY,
            overwrite=True,
        )


check_winter_program()


def get_winter_queue() -> pd.DataFrame:
    """
    Get Winter neutrino program and its queue.

    :return:
    """
    winter = WinterAPI()
    _, queue = winter.get_observatory_queue(program_name=WINTER_PROGRAM_NAME)
    if len(queue) > 0:
        queue.drop(columns=["target_names", "prog_name"], inplace=True)
    return queue


def post_winter_queue():
    """
    Get the queue of the Winter neutrino program.

    :return: None
    """
    queue = get_winter_queue()

    if len(queue) == 0:
        send_message("No observations in the Winter queue.")
        return

    send_message(f"WINTER queue:\n ```{tabulate(queue, headers=queue.columns)}``` \n")
