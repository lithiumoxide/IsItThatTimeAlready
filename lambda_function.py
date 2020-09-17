# These are the libraries this bot needs. You can install the non-standard ones by running:
#    pip3 install tweepy
#    pip3 install arrow
#    pip3 install requests
# If you run this code in Lambda, you'll need to pack these libraries into Lambda Layers.

import tweepy
import os
import requests
import arrow
import boto3

cw_event = boto3.client('events')

# os.environ here reads in the keys and secrets from the Lambda environment variables so that
# they are not stored in the code itself. If you're running this code locally, you can plug
# in your credentials as-is. Remember not to publish your Twitter API credentials in public!

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

def lambda_handler(event, context):
    # This function is the entry point of the code. When the Lambda function is triggered by
    # its cron schedule, these next few lines run in order. Each lines calls other functions
    # that are defined further down below.
    api = authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    tweet_time = create_tweet_time(get_time())          # This figures out the timein a format used in the Tweet
    send_tweet(api, tweet_time)                         # This writes and sends the tweet
    update_cw_event_rule(create_cron_time(get_time()))  # Finally, this updates the EventBridge/CloudWatch cron schedule

def authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
    # In here we send our credentials to the Twitter API to "log in" so that we can
    # post stuff to the account later on.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api

def send_tweet(api, tweet_time):
    # This function compiles the tweet, combining some text with the time we worked out
    # and then calls the Twitter API to post the status update.
    tweet = "I can't believe it's dark already at " + tweet_time + "."
    print(tweet)
    api.update_status(status=tweet)
    
def get_time():
    # This function gets the time from the API below and gets it ready for use
    # to make a "Tweetable" time and a cron expression for the Lambd function to run next.
    # For info on the below API check out https://sunrise-sunset.org/api
    r = requests.get(url = 'https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400&formatted=0&date=tomorrow')
    data = r.json()
    raw_time = data['results']['nautical_twilight_end']
    utc_time = arrow.get(raw_time)
    
    return utc_time

def create_cron_time(utc_time):
    # This function creates the cron expression from the utc_time we worked out earlier.
    cron_expression = '%s %s %s %s %s %s' % (utc_time.minute, utc_time.hour, utc_time.day, utc_time.month, '?', utc_time.year)
    
    return cron_expression

def create_tweet_time(utc_time):
    # Here, we convert utc_time into local Irish time and format it liek HH:MM for use in the actual tweet.
    # If you follow all the time-related code closely, you'll notice that today's tweet will contain
    # tomorrow's time. The difference is so small, though, that it really makes no difference.
    time = utc_time.to('Europe/Dublin')
    tweet_time = '%s%s%s' % (time.hour, ':', time.minute)
    
    return tweet_time
    
def update_cw_event_rule(cron_expression):
    # In this fuction we update the EventBridge/CloudWatch cron schedule with the new expression
    # which is the date and time of the next time the code should run, i.e. end of nautical
    # twilight tomorrow.
    response = cw_event.put_rule(
        Name='IsItThatTimeAlready',
        ScheduleExpression='cron(' + cron_expression +')',
    )