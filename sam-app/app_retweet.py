import boto3
import tweepy
import os
import json

ssm = boto3.client('ssm', region_name='us-east-1')


def authenticate_twitter():
    #consumer_key = #(ssm.get_parameter(Name='twitter-consumer-key', WithDecryption=True))['Parameter']['Value']
    #consumer_secret = #(ssm.get_parameter(Name='twitter-consumer-secret', WithDecryption=True))['Parameter']['Value']
    #access_token = #(ssm.get_parameter(Name='twitter-access-token', WithDecryption=True))['Parameter']['Value']
    #access_token_secret = #(ssm.get_parameter(Name='twitter-access-token-secret', WithDecryption=True))['Parameter']['Value']
    
    access_token=""
    access_token_secret=""
    consumer_key=""
    consumer_secret=""
       
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    return api

def retweet(api, search, numberOfTweets):
    
    for tweet in tweepy.Cursor(api.search, search).items(numberOfTweets):
        try:
            tweet_id = tweet.id
            #print("ID = " + str(tweet_id))
            # Create a tweet
            # api.update_status("Hello Tweepy")
            print("Hello Tweepy: " + tweet.lang)
            if tweet.lang in ("pt","es","en"):
                #print(tweet.body)
                tweet.retweet()
                print('Retweeted the tweet: ' + str(tweet_id))
            else:
                print('no retweet')
        except tweepy.TweepError as e:
            print(e.reason)
        except StopIteration:
            break


def lambda_handler(event, context):
    try:     
        apiuse = authenticate_twitter()
        
        searchString = os.environ['TweetSearchString']
        
        numberOfTweets = 15
        print('String to look for: {0} and nb of tweets to retrieve: {1}'.format(searchString,numberOfTweets))
        
        retweet(apiuse, searchString, numberOfTweets)

    except Exception as e:
        print(e)
    
    return {
        "statusCode": 200,
        "body": json.dumps(
            {"message": "TwitterPoller"}
        ),
    }
