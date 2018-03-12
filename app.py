import re
import tweepy
from textblob import TextBlob
from tweepy import OAuthHandler
import pandas as pd
import os

consumer_key = '<your key here>'
consumer_secret = '<your secret key here>'
access_token = '<your access token here>'
access_secret = 'your access secret here'

directory = 'data'

if not os.path.exists(directory):
    os.makedirs(directory)


class Twitter(object):
    def __init__(self):
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Authentication failed")

    def clean_helper(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def clean_tweet(self, all_tweets):
        cleaned_tweets = []
        for tweet in all_tweets:
            tweet.text = self.clean_helper(tweet.text)
            cleaned_tweets.append(tweet)
        return cleaned_tweets

    def get_topic_tweets(self, topic, count=100):
        all_tweets = []
        tweets = self.api.search(q=topic, count=count, lang='en')
        count -= len(tweets)
        all_tweets.extend(tweets)
        last_id = tweets[-1].id - 1

        while len(tweets) > 0 and count > 0:
            tweets = self.api.search(q=topic, count=count, lang='en', max_id=last_id)
            all_tweets.extend(tweets)
            count -= len(tweets)
            last_id = tweets[-1].id - 1

        all_tweets = self.clean_tweet(all_tweets)
        return all_tweets

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

        all_tweets = self.clean_tweet(all_tweets)
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
            data['Tweet'].append(self.clean_helper(tweet.text))
            data['Date'].append(tweet.created_at)
            data['Likes'].append(tweet.favorite_count)
            data['RTs'].append(tweet.retweet_count)
        data['Sentiments'] = self.sentiment_analysis(tweets)
        df = pd.DataFrame(data, columns=['Sno', 'Tweet', 'Date', 'Likes', 'RTs', 'Sentiments'])

        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)

        df.to_csv('{}/{}-{}.csv'.format(directory, usr, count), index=None)


def user_wrapper(api):
    usr = input('Enter username : ')
    count = int(input('Enter number of tweets to be searched : '))

    tweets = api.get_user_tweet(name=usr, count=count)
    api.store_tweets(tweets, usr, count)


def topic_wrapper(api):
    topic = input('Enter topic to be searched : ')
    count = int(input('Enter number of tweets to be searched : '))

    tweets = api.get_topic_tweets(topic, count)
    api.store_tweets(tweets, topic, count)


def menu():
    print('1. Search by username')
    print('2. Search by topic')

    choice = int(input('Enter your choice (1 or 2) : '))
    return choice


def main():
    api = Twitter()
    choice = menu()

    if (choice == 1):
        user_wrapper(api)
    if (choice == 2):
        topic_wrapper(api)


if __name__ == '__main__':
    main()
