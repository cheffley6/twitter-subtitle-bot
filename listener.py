from tweepy import OAuthHandler, API, Stream, StreamListener
import sys
from pprint import pprint

from config import twitter_credentials
from tweet_handler import handle_tweet
from mongo_interface import Tweet


# TweetStreamListener class inherits from tweepy.StreamListener and overrides on_status/on_error methods.
class TweetStreamListener(StreamListener):
    def on_status(self, status):
        # if "retweeted_status" attribute exists, flag this tweet as a retweet.
        is_retweet = hasattr(status, "retweeted_status")
        if is_retweet:
            return
        
        video_tweet_id = status.in_reply_to_status_id
        mention_author = status.user.screen_name
        mention_id = status.id
        video_author = status.in_reply_to_screen_name

        video_tweet = Tweet(video_tweet_id, video_author)
        mention_tweet = Tweet(mention_id, mention_author, video_tweet_id, video_author)

        handle_tweet(video_tweet, mention_tweet)

    def on_error(self, status_code):
        print("Encountered streaming error (", status_code, ")")
        sys.exit()

if __name__ == "__main__":
    # complete authorization and initialize API endpoint
    auth = OAuthHandler(twitter_credentials.TWITTER_CONSUMER_KEY, twitter_credentials.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(twitter_credentials.TWITTER_ACCESS_KEY, twitter_credentials.TWITTER_ACCESS_SECRET)
    api = API(auth)

    # initialize stream
    streamListener = TweetStreamListener()
    stream = Stream(auth=api.auth, listener=streamListener, tweet_mode='extended')

    tags = ["@VideoSubtitle"]
    stream.filter(track=tags)
