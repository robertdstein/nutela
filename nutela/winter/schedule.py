import tempfile
from pathlib import Path

import matplotlib.pyplot as plt

from nutela.notice import AstrotrackNotice
from nutela.slack import send_image, send_message
from nutela.winter.submit import submit_winter
from nutela.winter.tile import get_tiles

NIGHTS_REV0 = [0.0, 0.0]
NIGHTS_REV1 = [1.0, 7.0]


def schedule_winter(nu: AstrotrackNotice, debug: bool = False):
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


def base_schedule(
    nu: AstrotrackNotice,
    nights: list[float],
    debug: bool = False,
    mode: str | None = None,
):
    """
    Build a plan for the notice.

    :param nu: Neutrino notice
    :param nights: List of nights to observe
    :param debug: Debug flag
    :param mode: Tiling mode for the observation
    :return: None
    """
    # Send the tiles
    with tempfile.TemporaryDirectory() as tmpdirname:
        plt.figure()
        tiles, ax = get_tiles(nu, mode=mode)
        path = Path(tmpdirname) / "winter_tiles.png"
        plt.savefig(path)
        send_image(path)

    submit_winter(tiles, nights=nights, nu=nu, debug=debug)


def schedule_revision_0(nu: AstrotrackNotice, debug: bool = False):
    """
    Build a plan for revision 0 of the notice.
    Always do a 2x2 square tiling.

    :param nu: Neutrino notice
    :param debug: Debug flag
    :return: None
    """
    base_schedule(nu, nights=NIGHTS_REV0, debug=debug, mode="square")


def schedule_revision_1(nu: AstrotrackNotice, debug: bool = False):
    """
    Build a plan for revision 1 of the notice.

    :param nu: Neutrino notice
    :param debug: Debug flag
    :return: None
    """
    base_schedule(nu, nights=NIGHTS_REV1, debug=debug)
