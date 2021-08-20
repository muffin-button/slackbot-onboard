# Public packages
import json
import logging
from fastapi import FastAPI, Request
from slack_sdk.errors import SlackApiError
from urllib.parse import unquote

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

# Create API
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/message")
async def incomingWebhook(req: Request):
    logging.info(f'{__name__}.incomingWebhook :: Received message')
    try:
        body = await req.body()

        payload_string = body[8:].decode('utf-8')
        unquoted = unquote(payload_string)
        payload = json.loads(unquoted)

        logging.info(f'payload {str(payload)}')

        isValid = generateSlackSignature(body, req)
        assert isValid, 'Invalid request signature'

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

                        client.conversations_invite(channel=channel_id, users=user)

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

                        client.conversations_kick(channel=channel_id, user=user)

                    publishView()

        return {"success": 1}

    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
