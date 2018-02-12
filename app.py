import re
import tweepy
from textblob import TextBlob
from tweepy import OAuthHandler
import pandas as pd
import os
from keys import *

directory = 'data'
usr = 'SrBachchan'
count = 3000

consumer_key = 'MQzBTc1EU7khKXyGZSXzIXEwu'
consumer_secret = 'ileULPagQp0Bmo0V5FS1KeHamMIsI8jQ6EdUlVmiTLQfjcx2sP'
access_token = '711802845511614464-JdZ9gos2V1faZAXZLHRqAIkjrwU3ESE'
access_secret = 'yTONtgIeVgPaiBHvIEArdrOPbERXur9Nnfz4w9sT1btHw'


if not os.path.exists(directory):
    os.makedirs(directory)


class Twitter(object):
    def __init__(self):
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Failed")

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_query_tweets(self, query, count=4):
        tweets = []
        try:
            fetched_tweets = self.api.search(q=query, count=count, lang='en')

            for i, tweet in enumerate(fetched_tweets, 1):
                print("{}. {}".format(i, tweet.text))
                print("{}. {}".format(i, self.clean_tweet(tweet.text)))
                tweet = self.clean_tweet(tweet.text)
                tweets.append(tweet)
        except tweepy.TweepError as e:
            print("error : ", str(e))
        return tweets

    def get_user_tweet(self, name, count=5):
        all_tweets = []
        tweets = self.api.user_timeline(screen_name=name, count=count)
        count -= len(tweets)
        all_tweets.extend(tweets)

        last_id = tweets[-1].id - 1

        while len(tweets) > 0 and count > 0:
            tweets = self.api.user_timeline(screen_name=name, count=count, max_id=last_id)
            all_tweets.extend(tweets)
            count -= len(tweets)
            last_id = tweets[-1].id - 1

        return all_tweets

    def sentiment_analysis(self, tweets):
        sentiments = []
        for tweet in tweets:
            tweet = TextBlob(tweet.text)
            pol = tweet.sentiment.polarity
            if pol > 0:
                sentiments.append(1)
            elif pol == 0:
                sentiments.append(0)
            else:
                sentiments.append(-1)
        return sentiments

    def store_tweets(self, tweets, usr, count):
        data = {'Sno': [], 'Tweet': [], 'Date': [], 'Likes': [], 'RTs': []}
        for index, tweet in enumerate(tweets, 1):
            data['Sno'].append(index)
            data['Tweet'].append(self.clean_tweet(tweet.text))
            data['Date'].append(tweet.created_at)
            data['Likes'].append(tweet.favorite_count)
            data['RTs'].append(tweet.retweet_count)
        data['Sentiments'] = self.sentiment_analysis(tweets)
        df = pd.DataFrame(data, columns=['Sno', 'Tweet', 'Date', 'Likes', 'RTs', 'Sentiments'])

        df.to_csv('{}/{}-{}.csv'.format(directory, usr, count), index=None)


def main():
    api = Twitter()
    tweets = api.get_user_tweet(name=usr, count=count)
    api.store_tweets(tweets, usr, count)


if __name__ == '__main__':
    main()
