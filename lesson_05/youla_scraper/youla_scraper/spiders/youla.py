import scrapy


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']

    def parse(self, response):
        pass
