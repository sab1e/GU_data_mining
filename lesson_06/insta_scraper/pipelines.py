from pymongo import MongoClient


class InstaScrapyPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['insta_parse']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item
