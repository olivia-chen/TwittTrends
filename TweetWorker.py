from time import sleep


import boto3
import json
from watson_developer_cloud import AlchemyLanguageV1
from pyes import *

arn = ''
queueName = 'tweet_SQS_queue'
new_thread_waittime =  10
working_slot = 15

sqs = boto3.resource('sqs')
# Get the queue. This returns an SQS.Queue instance
queue = sqs.get_queue_by_name(QueueName=queueName)

alchemyapi = AlchemyLanguageV1(api_key='')

sns = boto3.resource('sns')
platform_endpoint = sns.PlatformEndpoint(arn)
count = 0

def parse_tweet():
    global queue, platform_endpoint, alchemyapi, count, working_slot

    count += 1
    print(count)

    sleep(working_slot)

    for message in queue.receive_messages(MessageAttributeNames=['All'], VisibilityTimeout=30, MaxNumberOfMessages=1):
        
        if message.message_attributes is not None:
            
            snsMsg = {}
            ## geo
            coordinates = message.message_attributes.get('coordinates').get('StringValue')
            if coordinates:
                snsMsg['geo'] = json.loads(coordinates.replace("'",'"'))

                ## sentiment
                
                tweet_text = message.body
                response = alchemyapi.sentiment(text=tweet_text)
                

                if response['status'] == 'OK':

                    sentimentResult = response["docSentiment"]
                    
                    snsMsg['sentiment'] = sentimentResult
                    snsMsg['tweet'] = message.body
                    snsMsg['user'] = message.message_attributes.get('user_name').get('StringValue')

                    ## dump snsMsg and send message to SNS
                    snsMessage = json.dumps(snsMsg)
                    response = platform_endpoint.publish(Message=snsMessage,Subject='Tweet')
                    

                else:
                    print('Error in sentiment analysis call: ', response['statusInfo'])

        # Let the queue know that the message is processed
        message.delete()


from concurrent.futures import ThreadPoolExecutor

def main():
    executor = ThreadPoolExecutor(max_workers=10)
    while True:
        executor.submit(parse_tweet)
        sleep(new_thread_waittime)

if __name__ == '__main__':
    main()
