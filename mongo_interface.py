from pymongo import MongoClient
from datetime import datetime

mongo_client = MongoClient('localhost', 27017)
database = mongo_client.subtitle_bot
collection = database.tweets


class Tweet:

    def __init__(self, id, create_date=None):
        self.id = id
        self.create_date = create_date
    
    def is_in_mongo(self):
        return True if collection.find_one({"tweet_id": self.id}) else False

    def get_response_tweet_ids(self):
        entry = collection.find_one({"tweet_id": self.id})
        if entry:
            return entry['captioned_tweet_ids']
        else:
            return None

    def insert_into_mongo(self, captioned_tweets):
        if self.is_in_mongo():
            return {
                "success": 0,
                "error_text": "Tweet is already in mongo."
            }
        
        response = collection.insert_one({
            "tweet_id": self.id,
            "captioned_tweet_ids": [t.id for t in captioned_tweets],
            "create_date": captioned_tweets[0].create_date
        })

        if response and response.inserted_id:
            return {
                "success": 1
            }
        else:
            return {
                "success": 0,
                "error_text": "Error inserting to Mongo (to-do: get Mongo error text for here)."
            }
        


    def remove_from_mongo(self):
        collection.delete_one({"tweet_id": self.id})
        assert not self.is_in_mongo()


if __name__ == "__main__":
    print("Testing mongo interface.")
    fake_tweet = Tweet(-1)
    fake_captioned_tweet = Tweet(-2, datetime.now())
    fake_second_captioned_tweet = Tweet(-3, datetime.now())

    assert not fake_tweet.is_in_mongo()
    fake_tweet.insert_into_mongo([fake_captioned_tweet, fake_second_captioned_tweet])

    print(collection.find_one({"tweet_id": fake_tweet.id}))
    
    assert fake_tweet.is_in_mongo()
    fake_tweet.remove_from_mongo()

    assert not fake_tweet.is_in_mongo()
    print("Tests successful.")