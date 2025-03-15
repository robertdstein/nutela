from slack_sdk import WebClient
import os
import dotenv
from pathlib import Path

from slack_sdk.errors import SlackApiError
import logging

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

CHANNEL = os.environ['SLACK_CHANNEL']

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def send_message(text: str):
    """
    Function for sending a message to a Slack channel.

    :param text: Text to send
    :return: None
    """
    try:
        response = client.chat_postMessage(
            channel=CHANNEL,
            text=text
        )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        logger.error(f"Slack API error: {e}")

def send_image(path: Path):
    """
    Function to upload image

    :param path: Path of image
    :return: None
    """
    try:
        with open(path, 'rb') as image:
            client.files_upload_v2(
                file=image,
                filename=path.name,
                channels=CHANNEL,
            )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        logger.error(f"Slack API error: {e}")