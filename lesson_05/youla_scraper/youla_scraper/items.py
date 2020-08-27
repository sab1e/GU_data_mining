import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy import Selector


def get_price(value):
    price_tag = Selector(text=value)
    result_price = float(
        price_tag.xpath('//text()').extract_first().replace('\u2009', ''))

    return result_price


def get_params(value):
    params_tag = Selector(text=value)
    key = params_tag.xpath(
        './/div[@class="AdvertSpecs_label__2JHnS"]/text()').extract_first()
    value = params_tag.xpath(
        './/div[@class="AdvertSpecs_data__xK2Qx"]//text()').extract_first()

    return key, value


def get_photo_url(value):
    return value.split()[0]


class YoulaScraperItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    images = scrapy.Field(input_processor=MapCompose(get_photo_url))
    params = scrapy.Field(
        output_processor=lambda x: dict(get_params(itm) for itm in x))
    description = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=MapCompose(get_price))
    author_url = scrapy.Field()
    phone = scrapy.Field()
