import scrapy


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
        title = response.css(
            'h1.title-info-title span.title-info-title-text::text').extract()
        img_url = response.css(
            'div.gallery-list-wrapper '
            'ul.gallery-list.js-gallery-list '
            'img::attr("src")').extract()
        params_names = response.css('ul.item-params-list '
                                    'li.item-params-list-item '
                                    'span::text').extract()
        params_values = response.css('div.item-params '
                                     'ul.item-params-list '
                                     'li::text').extract()
        address = response.css('div.item-address '
                               'span.item-address__string::text').extract()
        price = response.xpath(
            '//div[@id="price-value"]/'
            'span[contains(@class, "price-value-string")]/'
            'span[@class="js-item-price"]/@content').extract_first()

        cash_sign = response.xpath(
            '//div[@id="price-value"]/'
            'span[contains(@class, "price-value-string")]//'
            'span[@class="font_arial-rub"]/text()').extract_first()

        print(1)
        yield response.follow(
                'https://m.avito.ru/tyumen/kvartiry/tel:phone',
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Mobile Safari/537.36'},
                callback=self.phone_parse
            )

    def phone_parse(self, response):
        print(1)
