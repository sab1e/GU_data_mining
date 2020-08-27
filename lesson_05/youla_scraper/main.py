from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from youla_scraper import settings
from youla_scraper.spiders.youla import YoulaSpider

if __name__ == '__main__':
    crawl_seiitngs = Settings()
    crawl_seiitngs.setmodule(settings)

    crawl_proc = CrawlerProcess(settings=crawl_seiitngs)
    crawl_proc.crawl(YoulaSpider)
    crawl_proc.start()
