from birdy.twitter import UserClient, StreamClient
import os
try: import simplejson as json
except ImportError: import json
import re
from urllib import quote
import urllib2

CONSUMER_KEY = 'EffXBq4AQdKBvLEduXQdDK4nB'
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = '725756018739662848-YOLLA6SOWI6ohN9w5ejMhkXHdYD1jDZ'
ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
TEEMILL_API_KEY = os.environ['TEEMILL_API_KEY']

teemill_url = 'https://rapanuiclothing.com/api-access-point/?api_key='+TEEMILL_API_KEY+'&item_code=RNA1&colour=White&image_url='

count = 0

tweets = ['\n2015: Tweeting bitmoji \n2016: Wearing bitmoji!\n','Your bitmoji is the cutest ever!!! I WANT A T-SHIRT LIKE THAT!!!', 'Time to kick this up a notch and become the coolest kid in school?', "Your wishes have been heard. Here's a t-shirt for that", "Wouldn't it be cool to have that on a t-shirt?"]




client = StreamClient(CONSUMER_KEY,
                   CONSUMER_SECRET,
                   ACCESS_TOKEN,
                   ACCESS_TOKEN_SECRET)

response = client.stream.statuses.filter.post(track='bitmoji')

for data in response.stream():
	print data['text']
	print data
	if 'media' in data['entities']:
		image_url = data['entities']['media'][0]['media_url']
		print image_url
		encoded_image_url = quote(image_url)
		print encoded_image_url
		temp_teemill_url = teemill_url + encoded_image_url
		print temp_teemill_url
		product_url = urllib2.urlopen(temp_teemill_url).read()
		print product_url

		user_name = data['user']['screen_name']
		print user_name

		tweet_text = 'Hey @' + user_name + '! ' + tweets[count] + product_url
		print tweet_text
		count += 1
		count = count%len(tweets)

		client.api.statuses.update.post(status=tweet_text)