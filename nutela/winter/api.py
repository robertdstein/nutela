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


def post_winter_queue():
    """
    Get the queue of the Winter neutrino program.

    :return: None
    """
    winter = WinterAPI()
    res, queue = winter.get_observatory_queue(program_name=WINTER_PROGRAM_NAME)
    queue.drop(columns=["target_names", "prog_name"], inplace=True)

    # try:
    #     too_names = []
    #     for row in queue["target_names"]:
    #         all_names = [x.split("rev") for x in row]
    #         joins = ["rev".join([x[0], x[1][0]]) for x in all_names]
    #         name = list(set(joins))[0]
    #         too_names.append(name)
    #     queue.drop(columns=["target_names", "prog_name"], inplace=True)
    #     queue["too_name"] = too_names
    # except (KeyError, ValueError, TypeError, IndexError):
    #     pass

    send_message(f"WINTER queue:\n ```{tabulate(queue, headers=queue.columns)}``` \n")
