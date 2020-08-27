from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class YoulaScraperPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client['youla_parse']

    def process_item(self, item, spider):
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item


class YoulaImagePipline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('images', []):
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        item['images'] = [itm[1] for itm in results if itm[0]]

