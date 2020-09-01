import scrapy


class InstaScrapyItem(scrapy.Item):
    _id = scrapy.Field()
    comments_disabled = scrapy.Field()
    id = scrapy.Field()
    edge_media_to_caption = scrapy.Field()
    shortcode = scrapy.Field()
    edge_media_to_comment = scrapy.Field()
    taken_at_timestamp = scrapy.Field()
    dimensions = scrapy.Field()
    display_url = scrapy.Field()
    edge_liked_by = scrapy.Field()
    edge_media_preview_like = scrapy.Field()
    owner = scrapy.Field()
    thumbnail_src = scrapy.Field()
    thumbnail_resources = scrapy.Field()
    is_video = scrapy.Field()
    accessibility_caption = scrapy.Field()
    product_type = scrapy.Field()
    video_view_count = scrapy.Field()


class AuthorInstaScrapyItem(scrapy.Item):
    _id = scrapy.Field()
    id = scrapy.Field()
    profile_pic_url = scrapy.Field()
    username = scrapy.Field()
