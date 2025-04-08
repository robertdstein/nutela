import os

from tabulate import tabulate
from winterapi import WinterAPI

from nutela.notice import AstrotrackNotice
from nutela.slack import send_message
from nutela.winter.api import WINTER_PROGRAM_NAME
from nutela.winter.plan import plan_tiling


def submit_winter(tiles, nights, nu: AstrotrackNotice, debug: bool = False):
    """
    Submit the Winter tiles to the Winter system.

    :param tiles: List of tiles to submit
    :param nights: List of nights to observe
    :param nu: Neutrino notice
    :return: None
    """

    name = f"IC_{nu.run_num}_{nu.event_num}_rev{nu.revision}"

    too_list = plan_tiling(nights, tiles, nu_name=name)

    send_message(f"Submitting {len(too_list)} observations to Winter")

    winter = WinterAPI()

    try:
        api_res, api_schedule = winter.submit_too(
            program_name=WINTER_PROGRAM_NAME, data=too_list, submit_trigger=(not debug)
        )
    except ValueError as e:
        send_message(f"Error submitting to Winter: {e}")
        return

    try:
        send_message(api_res.json()["msg"])
        api_schedule.drop(
            columns=[
                "bestDetector",
                "obsHistID",
                "visitExpTime",
                "progID",
                "progPI",
                "ditherStepSize",
                "observed",
                "fieldID",
            ],
            inplace=True,
        )
        send_message(
            f"WINTER request: \n ```{tabulate(api_schedule, headers=api_schedule.columns)}``` \n"
        )

    except KeyError:
        send_message(f"Error in API response: {api_res.json()}")
