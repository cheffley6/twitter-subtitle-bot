from tweet import *
from datetime import datetime, timedelta
from twython import Twython, exceptions

from config import twitter_credentials

# It also deletes the bot's video/transcript tweets if the source tweet has been deleted

twitter = Twython(
    twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET,
    twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET
)
    
all_tweets = collection.find({})

for mongo_entry in all_tweets:

    if "tweet_id" not in mongo_entry:
        collection.delete_one({"_id": mongo_entry._id})
    print(mongo_entry)

    # this line is terrible, but as a note to my future self:
    # this is casting the mongoDB object of the tweet into 
    # the class version defined in mongo_interface
    
    bot_tweets = []
    for t in mongo_entry['captioned_tweet_ids']:
        bot_tweets.append(Tweet(t, "videosubtitle"))

    # check if original tweet deleted. if so, delete bot's tweets

    try:
        twitter.show_status(id=mongo_entry['tweet_id'])
    except exceptions.TwythonError:
        for t in bot_tweets:
            try:
                twitter.destroy_status(id=t.id)
            except exceptions.TwythonError:
                continue
        original_tweet = Tweet(mongo_entry['tweet_id'], None)
        original_tweet.remove_from_mongo()