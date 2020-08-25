import scrapy
import json

from pymongo import MongoClient


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru']
    start_urls = ['https://www.avito.ru/tyumen/kvartiry/prodam']

    __xpath_query = {
        'pagination': '//div[@class="index-content-2lnSO"]//'
                      'div[contains(@data-marker, "pagination-button")]/'
                      'span[@class="pagination-item-1WyVp"]/@data-marker',
        'ads': '//h3[@class="snippet-title"]/'
               'a[@class="snippet-link"][@itemprop="url"]/@href'

    }

    def __init__(self, **kwargs):
        self.client = MongoClient()
        self.db = self.client['parse_avito']
        self.collections = self.db['ads_data']

    def parse(self, response, start=True):
        if start:
            pages_count = int(
                response.xpath(self.__xpath_query['pagination']). \
                    extract()[-1].split('(')[-1].replace(')', ''))

            for num in range(2, pages_count + 1):
                yield response.follow(
                    f'?p={num}',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        ads_data = {
            'url': response.url
        }

        ads_data['title'] = response.css(
            'h1.title-info-title '
             'span.title-info-title-text::text').extract_first()

        ads_data['img_url'] = response.css(
            'div.gallery-list-wrapper '
            'ul.gallery-list.js-gallery-list '
            'img::attr("src")').extract()

        price = {'price': response.xpath(
            '//div[@id="price-value"]/'
            'span[contains(@class, "price-value-string")]/'
            'span[@class="js-item-price"]/@content').extract_first(),
                 'cash_sign': response.xpath(
                 '//div[@id="price-value"]/'
                 'span[contains(@class, "price-value-string")]//'
                 'span[@class="font_arial-rub"]/text()').extract_first()}
        ads_data['price'] = price

        ads_data['address'] = response.css(
            'div.item-address '
            'span.item-address__string::text').\
            extract_first().replace('\n', '').strip()

        params_names = response.css('ul.item-params-list '
                                    'li.item-params-list-item '
                                    'span::text').extract()
        params_values_all = response.css('div.item-params '
                                     'ul.item-params-list '
                                     'li::text').extract()
        params_values = [value for value in params_values_all if value != ' ']

        params = [{'name': param, 'value':value} for param, value in zip(params_names, params_values)]

        ads_data['params'] = params

    #     req = scrapy.http.Request(url='https://m.avito.ru/api/1/items/1965146039/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir')
    #     resp = scrapy.http.Response(
    #             url='https://m.avito.ru/api/1/items/1965146039/phone?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
    #             request=req
    #         )
    #     data = json.loads(resp.text)
    #     print(1)
    #
    # def phone_parse(self, response):
    #     print(1)
    #     return json.loads(response.text)

        self.save_to_db(ads_data)

    def save_to_db(self, ads_data):
        self.collections.insert_one(ads_data)