from gcn_kafka import Consumer
import dotenv
import os
from nutela.parse import parse_gcn_notice
from astropy.time import Time
from astropy import units as u

from nutela.slack import send_message
from nutela.ztf import select_alerts_ztf, schedule_ztf

dotenv.load_dotenv()

client_id, client_secret = os.getenv('GCN_ID'), os.getenv('GCN_SECRET')

if client_id is None or client_secret is None:
    raise ValueError('Missing GCN_ID or GCN_SECRET in .env file')

config = {'auto.offset.reset': 'earliest'}  # FIXME

consumer = Consumer(
    client_id=client_id,
    client_secret=client_secret,
    config=config
)

# List all topics
# print(consumer.list_topics().topics)

# # Subscribe to topics and receive alerts
consumer.subscribe(['gcn.classic.text.ICECUBE_ASTROTRACK_BRONZE',
                    'gcn.classic.text.ICECUBE_ASTROTRACK_GOLD'])

latest_status = Time.now()

while True:
    if Time.now() - latest_status > 1 * u.day:
        print('Listening...')
        latest_status = Time.now()

    for message in consumer.consume(timeout=1):
        if message.error():
            print(message.error())
            continue
        # Print the topic and message ID
        print(f'topic={message.topic()}, offset={message.offset()}')
        value = message.value()
        nu = parse_gcn_notice(message)
        print(nu)

        nu_time = nu.event_time

        message = (f"Found neutrino at time {nu_time.isot}, of type {nu.notice_type}, and energy {nu.energy:.0f} TeV. "
                   f"Revision is {nu.revision}. \n"
                   f"The signalness is {100.*nu.signalness:.0f}%, with FAR {nu.far:.2f} per year. \n"
                   f"The sun distance is {nu.sun_dist}, and the moon distance is {nu.moon_dist}. \n"
                   f"The best fit coordinates are RA: {nu.src_ra:.2f}, Dec: {nu.src_dec:.2f}, "
                   f"with uncertainty radius of {nu.src_error:.2f} degrees.")

        send_message(message)

        valid_ztf = select_alerts_ztf(nu=nu)

        if valid_ztf:
            schedule_ztf(nu=nu)
        # raise