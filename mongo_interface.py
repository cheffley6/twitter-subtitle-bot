from pymongo import MongoClient

mongo_client = pymongo.MongoClient('localhost', 27017)
database = mongo_client.subtitlebot
collection = database.tweets
class Tweet:

    def __init__(self, id):
        self.id = id
    
    def is_in_mongo(self):
        return True if collection.find_one({"tweet_id": self.id}) else False

    def get_response_tweet(self):
        entry = collection.find_one({"tweet_id": self.id})
        if entry:
            return entry.captioned_tweet_id
        else:
            return None

    def insert_into_mongo(self, captioned_tweet):
        if self.is_in_mongo():
            return {
                "success": 0,
                "error_text": "Tweet is already in mongo."
            }
        
        response = collection.insert_one({
            "tweet_id": self.id,
            "captioned_tweet_id": captioned_tweet.id
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

        