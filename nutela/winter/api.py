import os

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


def post_winter_queue():
    """
    Get the queue of the Winter neutrino program.

    :return: None
    """
    winter = WinterAPI()
    res, queue = winter.get_observatory_queue(program_name=WINTER_PROGRAM_NAME)
    send_message(f"WINTER queue:\n {tabulate(queue)} \n")
