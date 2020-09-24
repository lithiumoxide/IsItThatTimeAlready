import json
import tweepy
import os
import requests
import arrow
import boto3

cw_event = boto3.client('events')

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_KEY = os.environ['ACCESS_KEY']
ACCESS_SECRET = os.environ['ACCESS_SECRET']

hours = {
    0 : 'twelve',
    1 : 'one',
    2 : 'two',
    3 : 'three',
    4 : 'four',
    5 : 'five',
    6 : 'six',
    7 : 'seven',
    8 : 'eight',
    9 : 'nine',
    10 : 'ten',
    11 : 'eleven',
    12 : 'twelve',
    13 : 'one',
    14 : 'two',
    15 : 'three',
    16 : 'four',
    17 : 'five',
    18 : 'six',
    19 : 'seven',
    20 : 'eight',
    21 : 'nine',
    22 : 'ten',
    23 : 'eleven',
    24 : 'twelve',
}

minutes = {
    # Text format: hour + minute
    0 : 'o\'clock',
    1 :  'o\'clock',

    # Text format: minute + hour
    2 : 'just after',
    3 : 'just after',
    4 : 'about five past',
    5 : 'five past',
    6 : 'about five past',
    7 : 'just after five past',
    8 : 'comin\' up to ten past',
    9 : 'ten past',
    10 : 'ten past',
    11 : 'after ten past',
    12 : 'after ten past',
    13 : 'quarter past',
    14 : 'quarter past',
    15 : 'a quarter past',
    16 : 'a quarter past',
    17 : 'about quarter past',
    18 : 'after quarter past',
    19 : 'about twenty past',
    20 : 'twenty past',
    21 : 'twenty past',
    22 : 'after twenty past',
    23 : 'after twenty past',
    25 : 'twenty-five past',
    26 : 'twenty-five past',
    27 : 'after twenty-five past',
    28 : 'about half past',
    29 : 'half past',
    30 : 'half past',

    # Text format: minute + hour+1
    31 : 'half past',
    32 : 'just gone half',
    33 : 'after twenty-five to',
    34 : 'twenty-five to',
    35 : 'twenty-five to',
    36 : 'about twenty-five to',
    37 : 'after twenty-five to',
    38 : 'about twenty to',
    39 : 'twenty to',
    40 : 'twenty to',
    41 : 'after twenty to',
    42 : 'after twenty to',
    43 : 'quarter to',
    44 : 'quarter to',
    45 : 'a quarter to',
    46 : 'a quarter to',
    47 : 'just after a quarter to',
    48 : 'about ten to',
    49 : 'about ten to',
    50 : 'ten to',
    51 : 'ten to',
    52 : 'after ten to',
    53 : 'comin\' up to five to',
    54 : 'about five to',
    55 : 'five to',
    56 : 'five to',
    57 : 'just after five to',

    # Text format: minute + hour + "o clock"
    58 : 'about',
    59 : 'about'
}

def lambda_handler(event, context):
    api = authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    tweet_time = create_tweet_time()
    send_tweet(api, tweet_time)
    update_cw_event_rule(create_cron_time(get_time()))

def authenticate(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    return api
    
def get_time():
    r = requests.get(url = 'https://api.sunrise-sunset.org/json?lat=53.3497645&lng=-6.2602732&formatted=0&date=tomorrow')
    data = r.json()
    raw_time = data['results']['civil_twilight_end']
    utc_time = arrow.get(raw_time)
    
    return utc_time

def create_cron_time(utc_time):
    cron_expression = '%s %s %s %s %s %s' % (utc_time.minute, utc_time.hour, utc_time.day, utc_time.month, '?', utc_time.year)
    
    return cron_expression

def update_cw_event_rule(cron_expression):
    response = cw_event.put_rule(
        Name='IsItThatTimeAlready',
        ScheduleExpression='cron(' + cron_expression +')',
    )

def create_tweet_time(hours=hours, minutes=minutes):
    r_tweet = requests.get(url = 'https://api.sunrise-sunset.org/json?lat=53.3497645&lng=-6.2602732&formatted=0')
    data_tweet = r_tweet.json()
    raw_time_tweet = data_tweet['results']['civil_twilight_end']
    utc_time_tweet = arrow.get(raw_time_tweet)
    
    t_tweet = utc_time_tweet.to('Europe/Dublin')
    m_tweet = t_tweet.minute
    h_tweet = t_tweet.hour
    
    if m_tweet in range(0,2):
        tweet_time = '%s %s' % (hours[h_tweet], minutes[m_tweet])
    elif m_tweet in range(2,31):
        tweet_time = '%s %s' % (minutes[m_tweet], hours[h_tweet])
    elif m_tweet in range(31,58):
        tweet_time = '%s %s' % (minutes[m_tweet], hours[h_tweet+1])
    elif m_tweet in range(58,60):
        tweet_time = '%s %s %s' % (minutes[m_tweet], hours[h_tweet+1], 'o\'clock')
    
    return tweet_time

def send_tweet(api, tweet_time):
    tweet = "I can't believe it's dark out already and it only " + tweet_time + "."
    print(tweet)
    api.update_status(status=tweet)