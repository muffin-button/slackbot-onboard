# Public packages
import os
import logging
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from fastapi import Request
from starlette.datastructures import FormData

# Local modules
from pyslack.db import *


slack_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
client = WebClient(token=slack_token)

signature_verifier = SignatureVerifier(
    signing_secret=slack_signing_secret
)


def generateSlackSignature(body: FormData, req: Request):
    """
    Generates a message signature by hashing the timestamp, payload, and a shared signing secret
    """
    return signature_verifier.is_valid(
        body, req.headers.get('X-Slack-Request-Timestamp'),
        req.headers.get('X-Slack-Signature'))


def getChannelName(id: str) -> str:
    """
    Retrieve the name for a given channel ID from the Slack API
    """

    result = 'UNKNOWN'
    logging.info(f'{__name__}.getChannelName :: Getting channel name for [{id}]')
    channel_info = client.conversations_info(channel=id)

    logging.info(f'{__name__}.getChannelName :: Channel info {channel_info}')
    if channel_info['ok']:
        result = channel_info['channel']['name']

    return result


def publishView():
    """
    Publishes an updated View to the Slackbot's page
    """

    logging.info(f'{__name__}.publishView :: Publishing updated view')

    protected_channels = getProtectedChannels()
    logging.info(f'{__name__}.publishView :: Protected channels {protected_channels}')

    blocks = []
    # Manage Users
    blocks.append({'type': 'header', 'text': {'type': 'plain_text',
                  'text': 'Manage Users', 'emoji': False}})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":large_green_circle: Onboard a user"
        },
        "accessory": {
            "type": "users_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a user :smile_cat:",
                "emoji": True
            },
            "action_id": "onboard-user"
        }
    })
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":large_red_square: Outprocess a user"
        },
        "accessory": {
            "type": "users_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select a user :crying_cat_face:",
                "emoji": True
            },
            "action_id": "outprocess-user"
        }
    })
    # Divider
    blocks.append({'type': 'divider'})
    # Manage Channels
    blocks.append({'type': 'header', 'text': {'type': 'plain_text',
                  'text': 'Manage Channels', 'emoji': False}})
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Designate protected channels"
        },
        "accessory": {
            "type": "multi_conversations_select",
            "placeholder": {
                    "type": "plain_text",
                    "text": "Select channels :speech_balloon: ",
                    "emoji": True
            },
            "action_id": "set-conversations"
        }
    })
    for channel in protected_channels:
        blocks.append({
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "#" + channel['name']
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": ":wastebasket:",
                    "emoji": True
                },
                "action_id": "unset-conversation",
                "value": channel['id']
            }
        })

    client.views_publish(user_id="U24JD6XJ7", view={"type": "home", "blocks": blocks})
    client.views_publish(user_id="U24TKQ1DY", view={"type": "home", "blocks": blocks})
