from mongo_interface import *
from datetime import datetime, timedelta
from twython import Twython, exceptions.TwythonError

from config import twitter_credentials


# This cron job automatically deletes the bot's video/transcript tweets once they are four weeks old
# It also deletes the bot's video/transcript tweets if the source tweet has been deleted

twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET
)
    
all_tweets = collection.find({})

for tweet in all_tweets:

    # this line is terrible, but as a note to my future self:
    # this is casting the mongoDB object of the tweet into 
    # the class version defined in mongo_interface
    tweet = Tweet(tweet.tweet_id)
    bot_tweets = []
    for t in tweet.captioned_tweet_ids:
        bot_tweets.append(Tweet(t.id))

    # remove tweets four weeks or older
    if (datetime.now() - tweet.create_date).days >= 28:
        for t in bot_tweets:
            twitter.destroy_status(id=t.id)
        tweet.remove_from_mongo()

    # check if original tweet deleted. if so, delete bot's tweets
    try:
        twitter.show_status(id=tweet.id)
    except exceptions.TwythonError:
        for t in bot_tweets:
            twitter.destroy_status(id=t.id)
        tweet.remove_from_mongo()