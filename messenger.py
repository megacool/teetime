"""
This bot listens to port 5002 for incoming connections from Facebook. It takes
in any messages that the bot receives and echos it back.
"""
from flask import Flask, request
import requests
import sys
import os
import logging

app = Flask(__name__)
TOKEN = os.environ['MESSENGER_TOKEN']
WEBHOOK_TOKEN = os.environ['WEBHOOK_TOKEN']

class Bot(object):
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v2.6/me/messages?access_token={0}".format(access_token)


    def send_text_message(self, recipient_id, message):
        return self.send_message(recipient_id, {'text': message})


    def send_message(self, recipient_id, message):
        payload ={'recipient': {'id': recipient_id},
                  'message': message
                 }
        print "Posting payload to facebook: %s" % payload
        return requests.post(self.base_url, json=payload).json()


    def send_generic_message(self, recipient_id, elements):
        payload = {'recipient': {'id': recipient_id},
                   'message': { "attachment": {
                                "type": "template",
                                "payload": {
                                    "template_type": "generic",
                                    "elements": elements
                                    }
                                }
                              }
                   }
        return requests.post(self.base_url, json=payload).json()

bot = Bot(TOKEN)

def init_logging(logger):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@app.route("/webhook", methods=['GET', 'POST'])
def hello():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == WEBHOOK_TOKEN):
            return request.args.get("hub.challenge")
        else:
            app.logger.info('missing token')
            return 'missing challenge token', 400
    if request.method == 'POST':
        output = request.json
        event = output['entry'][0]['messaging']
        for x in event:
            if (x.get('message') and x['message'].get('text')):
                message = x['message']['text']
                recipient_id = x['sender']['id']
                print bot.send_text_message(recipient_id, message)
        return "success"

if __name__ == "__main__":
    init_logging(app.logger)
    app.run(port=5002, debug=True)
