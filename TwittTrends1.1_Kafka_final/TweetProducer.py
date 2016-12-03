# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import boto3
from pyes import *
import json
from kafka import SimpleProducer, SimpleClient, KafkaClient

# Variables that contains the user credentials to access Twitter API
access_token = '2883078087-vTzc3o6RzC4oK8B2kCWaPERALTZgUjcXcQcvPWd'
access_token_secret = 'uC04FX1weZCOzFlSmzHApNqDLy2mxbT6wucQb8KPGHD1F'
consumer_key = 'NPaf7LeqzfL2uh4DtyX5pRDiA'
consumer_secret = 'Jcli0JRMyNgAhybouRhiqGSKPUye5S3fnAm22dwBvBr2llXbal'



# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def __init__(self):
        super(StreamListener, self).__init__()
        client = SimpleClient("localhost:9092")
        self.producer = SimpleProducer(client, async = True,
                          batch_send_every_n = 1000,
                          batch_send_every_t = 10)
    def on_data(self, data):
        try:
            temp={}
            decoded = json.loads(data)
            if decoded['coordinates']:
                #print "ID:%s Username:%s Tweet:%s"%(decoded['id'],decoded['user']['screen_name'],decoded['text'])
                temp["text"]= decoded['text']
                temp["id"]= str(decoded['id'])
                temp["name"]= decoded['user']['screen_name']
                temp["latitude"]= str(decoded['coordinates']['coordinates'][1])
                temp["longitude"]= str(decoded['coordinates']['coordinates'][0])
                final = json.dumps(temp)
                print (final)
                self.producer.send_messages('test', bytes(final, 'utf-8'))
                '''{"name": "mynameisssz",
                "text": "\u0e44\u0e21\u0e48\u0e40\u0e23\u0e35\u0e22\u0e19 (@ Dream World in Thanyaburi, Pathum Thani) https://t.co/E3q9X4fUeP",
                "id": "804510826308702208",
                "latitude": "13.98835907",
                "longitude": "100.67508314"}'''
        except Exception as e:
            print(e)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    # This handles Twitter authentication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=['love', 'china', 'hillary', 'halloween', 'trump', 'gotham', 'netflix', 'world'])
