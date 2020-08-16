import re
import requests

from datetime import datetime

from bs4 import BeautifulSoup
from pymongo import MongoClient


class GBBlogParse:
    domain = 'http://geekbrains.ru'
    start_url = 'http://geekbrains.ru/posts'

    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['parse_gb_blog']
        self.collection = self.db['posts']
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []

    def parse_rows(self, url=start_url):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url)
            soap = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soap)
            self.search_post_links(soap)

    def get_next_page(self, soap):
        ul = soap.find('ul', attrs={'class': 'gb__pagination'})
        a = ul.find('a', text=re.compile('›'))
        return f'{self.domain}{a.get("href")}' if a and a.get("href") else None

    def search_post_links(self, soap):
        wrapper = soap.find('div', attrs={'class': 'post-items-wrapper'})
        posts = wrapper.find_all('div', attrs={'class': 'post-item'})
        links = {f'{self.domain}{itm.find("a").get("href")}' for itm in posts}
        self.post_links.update(links)

    def post_page_parse(self):
        for url in self.post_links:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soap = BeautifulSoup(response.text, 'lxml')

            self.post_data.append(self.get_post_data(url, soap))
            print(len(self.post_data))

    def get_post_data(self,  url, soap):
        result = {}
        result['url'] = url

        result['title'] = soap.find('h1',
                                    attrs={'class': 'blogpost-title'}).text

        content = soap.find('div',
                            attrs={'class': 'blogpost-content',
                                          'itemprop': 'articleBody'})
        img = content.find('img')
        result['image'] = img.get('src') if img else None

        result['writer_name'] = soap.find('div',
                                          attrs={'itemprop': 'author'}
                                          ).text

        content = soap.find('div', attrs={'class': 'row m-t'})
        writer_url = content.find('a',
                                  attrs={'style': 'text-decoration:none;'}
                                  )
        result['writer_url'] = f'{self.domain}{writer_url["href"]}'

        date_content = soap.find('time', attrs={'itemprop': 'datePublished'})
        date = datetime.strptime(date_content['datetime'],
                                 '%Y-%m-%dT%H:%M:%S%z')
        result['pub_date'] = date

        return result

    def save_to_mongo(self):
        self.collection.insert_many(self.post_data)

    def get_from_mongo(self, from_date, to_date):
        posts = self.collection.find({"pub_date": {"$gt": from_date,
                                                   "$lt": to_date}})
        return list(posts)


if __name__ == '__main__':
    parser = GBBlogParse()
    parser.parse_rows()
    parser.post_page_parse()
    parser.save_to_mongo()
    posts = parser.get_from_mongo(datetime(2020, 8, 1), datetime(2020, 8, 10))
