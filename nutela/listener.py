import argparse
import os
import time

import dotenv
from anyio import sleep
from astropy import units as u
from astropy.time import Time
from gcn_kafka import Consumer

from nutela.parse import parse_gcn_notice
from nutela.slack import send_message
from nutela.winter import post_winter_queue, schedule_winter, select_alerts_winter
from nutela.ztf import post_ztf_queue, schedule_ztf, select_alerts_ztf


def start_listener():
    """
    Connect to the GCN broker and listen for neutrino alerts.

    :return:
    """

    args = argparse.ArgumentParser()
    args.add_argument(
        "--load-recent",
        action="store_true",
        help="Enable debug mode",
        default=False,
    )
    args.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
        default=False,
    )

    res = args.parse_args()

    dotenv.load_dotenv()

    latest_status = Time.now()

    send_message(f"Switching on at {latest_status} UTC")
    post_ztf_queue()
    post_winter_queue()

    try:

        client_id, client_secret = os.getenv("GCN_ID"), os.getenv("GCN_SECRET")

        if client_id is None or client_secret is None:
            raise ValueError("Missing GCN_ID or GCN_SECRET in .env file")

        config = {"auto.offset.reset": "earliest"}  # FIXME

        consumer = Consumer(
            client_id=client_id, client_secret=client_secret, config=config
        )

        t_start = Time.now()

        # # Subscribe to topics and receive alerts
        consumer.subscribe(
            [
                "gcn.classic.text.ICECUBE_ASTROTRACK_BRONZE",
                "gcn.classic.text.ICECUBE_ASTROTRACK_GOLD",
            ]
        )

        while True:
            if Time.now() - latest_status > 1 * u.day:
                latest_status = Time.now()
                send_message(f"Still active at {latest_status} UTC")
                post_winter_queue()

            for message in consumer.consume(timeout=1):
                if message.error():
                    print(message.error())
                    continue
                # Print the topic and message ID
                print(f"topic={message.topic()}, offset={message.offset()}")
                value = message.value()
                nu = parse_gcn_notice(message)
                print(nu)

                nu_time = nu.event_time

                age = (t_start - nu_time).to(u.day).value

                if (age > 7) | ((not res.load_recent) and (age > 0.0)):
                    send_message(
                        f"Skipping {nu_time.isot} as it is {age:.1f} days relative to tstart"
                    )
                    continue

                message_str = (
                    f"Found neutrino at time {nu_time.isot}, of type {nu.notice_type}, "
                    f"and energy {nu.energy:.0f} TeV. "
                    f"Revision is {nu.revision}. \n"
                    f"The signalness is {100.*nu.signalness:.0f}%, with a FAR of {nu.far:.2f} per year. \n"
                    f"The sun distance is {nu.sun_dist:.0f} deg, "
                    f"and the moon distance is {nu.moon_dist:.0f} deg. \n"
                    f"The best fit coordinates are RA: {nu.src_ra:.2f}, Dec: {nu.src_dec:.2f}, "
                    f"with uncertainty radius of {nu.src_error:.2f} degrees."
                )

                send_message(message_str)

                send_message("Scheduling ZTF")

                valid_ztf = select_alerts_ztf(nu=nu)

                if valid_ztf:
                    schedule_ztf(nu=nu, debug=res.debug)

                post_ztf_queue()

                time.sleep(10.0)

                send_message("Scheduling WINTER")

                valid_winter = select_alerts_winter(nu=nu)

                if valid_winter:
                    schedule_winter(nu=nu, debug=res.debug)

                else:
                    send_message("Not valid for WINTER")

                post_winter_queue()

                time.sleep(10.0)

                send_message(
                    f"Finished scheduling neutrino at time {nu_time.isot} (revision {nu.revision})"
                )

    finally:
        send_message(f"Disconnecting at {Time.now()} UTC")
