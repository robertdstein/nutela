import pandas as pd
from astropy.time import Time
from wintertoo.models.too import WinterRaDecToO

neutrino_nights = [0, 1, 2]
neutrino_priority = 150.0


def plan_tiling(
    nights: list[float], fields_df: pd.DataFrame, nu_name: str, **kwargs
) -> list[WinterRaDecToO]:
    """
    Plan the tiling for the neutrino observation.

    :param nights: List of nights to observe
    :param fields_df: List of fields to observe
    :param nu_name: Name of the neutrino
    :return: List of WinterRaDecToO objects
    """
    too_requests = []

    t_now = Time.now().mjd

    for j, offset in enumerate(nights):
        t_start = t_now + offset
        t_end = t_start + 7.0

        for k, row in fields_df.iterrows():

            args = {
                "target_priority": neutrino_priority,
                "start_time_mjd": t_start,
                "end_time_mjd": t_end,
                "target_name": f"{nu_name}_{j}_{k}",
                "use_best_detector": False,
                "filters": ["J"],
            }
            args.update(kwargs)

            too_request = WinterRaDecToO(ra_deg=row["RA"], dec_deg=row["Dec"], **args)

            too_requests.append(too_request)

    return too_requests
