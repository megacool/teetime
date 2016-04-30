"""
This bot listens to port 5002 for incoming connections from Facebook. It takes
in any messages that the bot receives and echos it back.
"""
from flask import Flask, request
import requests
import uuid
import tinys3
import sys
import os
import logging
from urllib import quote
import urllib2
from bs4 import BeautifulSoup

import teetime

app = Flask(__name__)
TOKEN = os.environ['MESSENGER_TOKEN']
WEBHOOK_TOKEN = os.environ['WEBHOOK_TOKEN']
TEEMILL_API_KEY = os.environ['TEEMILL_API_KEY']

TEEMILL_URL = 'https://rapanuiclothing.com/api-access-point/?api_key='+TEEMILL_API_KEY+'&item_code=RNA1&colour=White&image_url='

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


    def send_generic_message(self, recipient_id, product_url, image_url):
        payload = {'recipient': {'id': recipient_id},
                   'message': {
                                "attachment": {
                                    "type": "template",
                                    "payload": {
                                        "template_type": "generic",
                                        "elements": [{
                                            "title": "Here's your T-Shirt!",
                                            "subtitle": "Buy it now for only $20!",
                                            "image_url": image_url,
                                            "buttons": [{
                                                "type": "web_url",
                                                "url": product_url,
                                                "title": "Buy it now!"
                                            }]
                                        }]
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


def get_product_url(image_url):
    encoded_image_url = quote(image_url)
    print encoded_image_url
    temp_teemill_url = TEEMILL_URL + encoded_image_url
    print temp_teemill_url
    product_url = urllib2.urlopen(temp_teemill_url).read()
    print product_url
    return product_url


def get_tshirt_image_url(product_url):
    product_page = urllib2.urlopen(product_url).read()
    soup = BeautifulSoup(product_page, "html.parser")
    meta_tag_data = soup.findAll(attrs={"property":"og:image"})
    print meta_tag_data
    image_url = meta_tag_data[0]['content']
    print image_url
    return image_url


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
        for message_wrapper in event:
            try:
                message = message_wrapper['message']['text']
            except KeyError:
                continue

            try:
                local_image_path = teetime.create_typography(message)
                s3_image_url = upload_to_s3(local_image_path)
                os.remove(local_image_path)
                recipient_id = message_wrapper['sender']['id']

                product_url = get_product_url(s3_image_url)
                tshirt_image_url = get_tshirt_image_url(product_url)

                print bot.send_generic_message(recipient_id, product_url, tshirt_image_url)
            except:
                response = 'Failed to create image from your message, please try again later'
                print bot.send_text_message(recipient_id, response)
        return "success"


def upload_to_s3(path):
    access_id = os.environ['S3_ACCESS_ID']
    access_key = os.environ['S3_SECRET_ACCESS_KEY']
    conn = tinys3.Connection(access_id, access_key, tls=True, endpoint='s3-us-west-2.amazonaws.com')
    s3_filename = '%s.png' % uuid.uuid4()
    bucket = 'teetime-prod'
    with open(path, 'rb') as fh:
        conn.upload(s3_filename, fh, bucket, public=True)

    return 'https://%s.s3.amazonaws.com/%s' % (bucket, s3_filename)


if __name__ == "__main__":
    init_logging(app.logger)
    app.run(port=5002, debug=True)
