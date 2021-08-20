# Public packages
import logging
from typing import Any
from slack_sdk.errors import SlackApiError
import os
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from threading import Event

# Local modules
from pyslack.db import *
from pyslack.slack import *


logging.basicConfig(
    format='[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S %z'
)

# publish initial view at startup
publishView()


# Initialize SocketModeClient with an app-level token + WebClient
client = SocketModeClient(
    # This app-level token will be used only for establishing a connection
    app_token=os.environ.get("SLACK_APP_TOKEN"),  # xapp-A111-222-xyz
    # You will be using this WebClient for performing Web API calls in listeners
    web_client=WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))  # xoxb-111-222-xyz
)

def incomingWebhook(payload: Any):
    logging.info(f'{__name__}.incomingWebhook :: Received message')
    try:
        logging.info(f'payload {str(payload)}')

        if 'actions' in payload:
            actions = payload['actions']
            logging.info(f'{__name__}.incomingWebhook :: Found actions {actions}')

            for action in actions:
                logging.info(f'{__name__}.incomingWebhook ::    Action:' + action['action_id'])

                if action['action_id'] == 'set-conversations':
                    selected_conversations = action['selected_conversations']

                    logging.info(f'{__name__}.incomingWebhook :: Setting conversations {selected_conversations}')

                    for channel_id in selected_conversations:
                        logging.info(f'{__name__}.incomingWebhook :: getChannelName [{channel_id}]')

                        channel_name = getChannelName(channel_id)
                        addProtectedChannel(channel_id, channel_name)

                    publishView()

                elif action['action_id'] == 'unset-conversation':
                    action_value = action['value']

                    logging.info(f'{__name__}.incomingWebhook :: Unsetting conversation:')
                    logging.info(action_value)

                    deleteProtectedChannel(action_value)
                    publishView()

                elif action['action_id'] == 'onboard-user':
                    logging.info(f'{__name__}.incomingWebhook :: Onboarding user:')
                    logging.info(action['selected_user'])

                    user = action['selected_user']

                    channels = getProtectedChannels()
                    for channel in channels:
                        channel_id = channel['id']
                        channel_name = channel['name']

                        logging.info(f'{__name__}.incomingWebhook :: Inviting [{user}] to [{channel_name}]')

                        #client.conversations_invite(channel=channel_id, users=user)
                        client.web_client.conversations_invite(channel=channel_id, users=user)

                    publishView()

                elif action['action_id'] == 'outprocess-user':
                    logging.info(f'{__name__}.incomingWebhook :: Outprocessing user:')
                    logging.info(action['selected_user'])

                    user = action['selected_user']

                    channels = getProtectedChannels()
                    for channel in channels:
                        channel_id = channel['id']
                        channel_name = channel['name']

                        logging.info(f'{__name__}.incomingWebhook :: Kicking [{user}] from [{channel_name}]')

                        client.web_client.conversations_kick(channel=channel_id, user=user)
                        

                    publishView()

        return {"success": 1}

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]

def process(client: SocketModeClient, req: SocketModeRequest):
    logging.info(req.type)
    #dir(req)
    if req.type == "interactive":
        # Acknowledge the request anyway
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        logging.info(req.payload)
        incomingWebhook(req.payload)



# Add a new listener to receive messages from Slack
# You can add more listeners like this
client.socket_mode_request_listeners.append(process)
# Establish a WebSocket connection to the Socket Mode servers
client.connect()
# Just not to stop this process
Event().wait()