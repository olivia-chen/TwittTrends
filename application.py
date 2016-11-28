from flask import Flask, redirect
from flask import render_template
from pyes import *
from flask import request
import json
import requests
from wsgiref.simple_server import make_server
import flask_googlemaps
import boto3

# Address of the elasticsearch host
elasticsearchURL = ''
conn = ES(elasticsearchURL)
application = Flask(__name__)
application.config['GOOGLEMAPS_KEY'] = ""
flask_googlemaps.GoogleMaps(application)

res_count = requests.get(elasticsearchURL + '/test-tweet-index/test-tweet-type/_count')
global count
count_json = json.loads(res_count.text.replace("\\", r"\\"))
count = count_json['count']

addressurl=''
global subscribed
subscribed = False


@application.route('/sns', methods=['POST','GET'])
def subscribe():
    global count
    global subscribed
    try:

        json_req= json.loads(request.data.decode("utf-8"))
        if request.headers['X-Amz-Sns-Message-Type'] == 'SubscriptionConfirmation':
            topicArn = json_req['TopicArn']
            token = json_req['Token']
            snsclient = boto3.client('sns', region_name='us-west-2')
            snsclient.confirm_subscription(TopicArn=topicArn,Token=token)
            subscribed = True
        else:
            msg_toindex = json_req['Message']
            msg_toindex = str(msg_toindex)
            msg_toindex = json.loads(msg_toindex)
            tweet_geo = msg_toindex["geo"]
            tweet_coordinates = tweet_geo["coordinates"]
            tweet_long=tweet_coordinates[1]
            tweet_lat=tweet_coordinates[0]
            tweet_text = msg_toindex["tweet"]
            tweet_sentiment_type = msg_toindex["sentiment"]["type"]
            tweet_user = msg_toindex["user"]
            conn.index({'location': {'lat': tweet_lat, 'lon': tweet_long},'message': tweet_text,'sentiment_type': tweet_sentiment_type,'user':tweet_user}, "test-tweet-index", "test-tweet-type")
    except Exception as e:
        print(e)
    if request.headers['type'] == 'newTweets':
        temp = requests.get(elasticsearchURL + '/test-tweet-index/test-tweet-type/_count')
        cc = json.loads(temp.text.replace("\\", r"\\"))
        dd = cc['count']
        if dd > count:
            count = dd
            return 'There comes a new Tweet, now there are ' + str(dd) + ' tweets in total!'
    return 'OK'

@application.route('/', methods=['POST'])
def backend_query():
    global dd_select
    dd_select = request.form['keyword_drop_down']
    global selected
    selected = dd_select
    conn = ES([''])
    q = TermQuery("message", dd_select)
    results = conn.search(indices = "test-tweet-index", query=q)
    count = 0
    coord_list = []
    sentiment_list = []
    for i in results:
        count = count + 1
        if (i["location"]["lat"]) is not None:
            coordinates = str(i["location"]["lat"]) + "," + str(i["location"]["lon"])
        sentiment_tweet = str(i["sentiment_type"])
        sentiment_list.append(sentiment_tweet)
        coord_list.append(coordinates)
    return render_template('MapUI_new.html', coord_list=coord_list,sentiment_list=sentiment_list,selected=selected,
                           keyword=dd_select)


@application.route('/', methods=['GET'])
def home():
    global subscribed
    if not subscribed:
        addressurl_tosubsribe = addressurl
        sendsubscription(addressurl_tosubsribe)
    return render_template('MapUI_new.html',coord_list=[],sentiment_list=[], keyword="select")


def sendsubscription(addressurl):
    try:
        sns = boto3.resource('sns', region_name='us-west-2')
        topicarn = sns.Topic('')
        endpoint = 'http://' + addressurl + '/sns'
        topicarn.subscribe(Protocol='http', Endpoint=endpoint)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    #application.run(host='127.0.0.1')
    make_server("", application).serve_forever()

