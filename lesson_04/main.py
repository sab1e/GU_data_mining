from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from avito_scraper import settings
from avito_scraper.spiders.avito import AvitoSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(AvitoSpider)
    crawl_proc.start()
