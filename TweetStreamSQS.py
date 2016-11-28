# Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import boto3
from pyes import *

# Variables that contains the user credentials to access Twitter API
access_token = ''
access_token_secret = ''
consumer_key = ''
consumer_secret = ''

queueName = 'tweet_SQS_queue'
# Get the service resource
sqs = boto3.resource('sqs')
# Create/Get the SQS Queue instance
queue = sqs.create_queue(QueueName=queueName)


# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet_json = json.loads(data)
        try:
            if tweet_json["coordinates"]:
                if (tweet_json["lang"] == "en"):
                    print(tweet_json['lang'])


                    tweetAttr = {
                        "coordinates": {
                            'StringValue': json.dumps(tweet_json["coordinates"]),
                            'DataType': 'String'
                        },
                        "user_id": {
                            'StringValue': tweet_json["user"]["id"].__str__(),
                            'DataType': 'Number'
                        },
                        "user_name": {
                            'StringValue': tweet_json["user"]["name"],
                            'DataType': 'String'
                        },
                    }

                    queue.send_message(MessageBody=tweet_json["text"], MessageAttributes=tweetAttr)
                    print(tweet_json["user"]["name"])
                    return True
        except Exception as e:
            print(e)

    def on_error(self, status):
        print(status)


if __name__ == '__main__':
    # This handles Twitter authentication and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=['love', 'china', 'hillary', 'halloween', 'trump', 'gotham', 'netflix', 'world'])
