from time import sleep


import boto3
import json
from watson_developer_cloud import AlchemyLanguageV1
from pyes import *
from kafka import KafkaConsumer

arn = 'arn:aws:sns:us-west-2:756554415895:TweetTrendsSNS'
new_thread_waittime =  10
working_slot = 15

KAFKA_HOST = 'localhost:9092'
TOPIC = 'test'
TIMEOUT = 10000

# Get the queue. This returns an SQS.Queue instance
#alchemyapi = AlchemyLanguageV1(api_key='4b3947040aeb1bcbb31429e6f400e7e1561f6d63')
alchemyapi = AlchemyLanguageV1(api_key='206274cfeb6f215a4493da7ff8156fca5abafa50')
#alchemyapi = AlchemyLanguageV1(api_key='abf549f17b8a5b7487b1d1cff03329bdabe68f50')

sns = boto3.resource('sns')
platform_endpoint = sns.PlatformEndpoint(arn)
count = 0
#consumer = KafkaConsumer(TOPIC, bootstrap_servers=[KAFKA_HOST], consumer_timeout_ms=-1)
consumer = KafkaConsumer('test',bootstrap_servers='localhost:9092')

def parse_tweet():
    global queue, platform_endpoint, alchemyapi, count, working_slot

    count += 1
    print(count)

    sleep(working_slot)


    #for message in queue.receive_messages(MessageAttributeNames=['All'], VisibilityTimeout=30, MaxNumberOfMessages=1):
    for message in consumer:
        print ("mmmmmmmmmmmmmmmmm")
        print(message)
        tweetContent = json.loads(message.value.decode('utf-8'))
        print(tweetContent)
        try:
            '''{"name": "mynameisssz",
                "text": "\u0e44\u0e21\u0e48\u0e40\u0e23\u0e35\u0e22\u0e19 (@ Dream World in Thanyaburi, Pathum Thani) https://t.co/E3q9X4fUeP",
                "id": "804510826308702208",
                "latitude": "13.98835907",
                "longitude": "100.67508314"}'''
            snsMsg = {}
            lat = tweetContent['longitude']
            lon = tweetContent['latitude'] #??
            print(lat)
            print(lon)
            if lat and lon:
                #snsMsg['geo'] = json.loads(coordinates.replace("'",'"'))
                tweet_text = tweetContent['text']
                response = alchemyapi.sentiment(text=tweet_text)
                print(response)
                print(response['status'])
                if response['status'] == 'OK':
                    sentimentResult = response["docSentiment"]
                    #print(message.body)
                    print(sentimentResult)
                    '''{'type': 'positive', 'score': '0.646364'}'''
                    snsMsg['sentiment'] = sentimentResult
                    snsMsg['tweet'] = tweetContent['text']
                    snsMsg['user'] = tweetContent['name']
                    snsMsg['latitude'] = lat
                    snsMsg['longitude'] = lon

                    ## dump snsMsg and send message to SNS
                    snsMessage = json.dumps(snsMsg)
                    response = platform_endpoint.publish(Message=snsMessage,Subject='Tweet')
                    print(snsMessage)
                    print(response)
                else:
                    print('Error in sentiment analysis call: ', response['statusInfo'])
            '''{"latitude": "-80.2732666",
            "sentiment": {"score": "-0.0274927", "mixed": "1", "type": "negative"},
            "longitude": "25.77508716",
            "user": "Pairsonnalites",
            "tweet": "AIDS :  World AIDS Day put spotlight on high Sask. HIV rates https://t.co/qyrc9HWSBy"}'''
        except Exception as e:
            print (e)
            print ('*******')
        message.delete()

    # Let the queue know that the message is processed
    #message.delete()


from concurrent.futures import ThreadPoolExecutor

def main():
    executor = ThreadPoolExecutor(max_workers=10)
    while True:
        executor.submit(parse_tweet)
        sleep(new_thread_waittime)

if __name__ == '__main__':
    main()
