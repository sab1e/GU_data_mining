import scrapy

from scrapy.loader import ItemLoader
from youla_scraper.items import YoulaScraperItem


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/moskva/cars/used/volvo/']

    __xpath_query = {
        'pagination': '//div[contains(@class, "Paginator_block__2XAPy")]/'
                      'div[@class="Paginator_total__oFW1n"]/text()',
        'ads': '//div[@id="serp"]//'
               'article[contains(@class, "SerpSnippet_snippet__3O1t2")]//'
               'div[@class="SerpSnippet_titleWrapper__38bZM"]/'
               'a/@href',
        'title': '//div[contains(@class, "AdvertCard_pageContent__24SCy")]//'
                 'div[@class="AdvertCard_advertTitle__1S1Ak"]/text()',
        'params': '//div[@class="AdvertCard_specs__2FEHc"]//'
                  'div[@class="AdvertSpecs_row__ljPcX"]',
        'description':
            '//div[contains(@class, "AdvertCard_pageContent__24SCy")]//'
            'div[contains (@class, "AdvertCard_description__2bVlR")]//'
            'div[@class="AdvertCard_descriptionInner__KnuRi"]/text()',
        'price': '//div[contains(@class, "AdvertCard_pageContent__24SCy")]//'
                 'div[@class="AdvertCard_topAdvertHeader__iqqNl"]//'
                 'div[contains(@class, "AdvertCard_price__3dDCr")]/text()',
        'images': '//div[@class="PhotoGallery_block__1ejQ1"]/'
                  'div[@class="PhotoGallery_photoWrapper__3m7yM"]/'
                  'figure[@class="PhotoGallery_photo__36e_r"]//'
                  'source/@srcset',
    }

    def parse(self, response, start=True):
        if start:
            page_count = int(
                response.xpath(self.__xpath_query['pagination']).extract()[1])

            for page_num in range(2, page_count + 1):
                yield response.follow(
                    f'?page={page_num}#serp',
                    callback=self.parse,
                    cb_kwargs={'start': False}
                )

        for link in response.xpath(self.__xpath_query['ads']):
            yield response.follow(
                link,
                callback=self.ads_parse
            )

    def ads_parse(self, response):
        item_loader = ItemLoader(YoulaScraperItem(), response)
        for key, value in self.__xpath_query.items():
            if key in ('pagination', 'ads'):
                continue
            item_loader.add_xpath(key, value)

        item_loader.add_value('url', response.url)

        yield item_loader.load_item()
