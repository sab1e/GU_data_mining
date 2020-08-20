import requests
import time

from bs4 import BeautifulSoup


class HabraBestDayParser:
    domain = 'https://habr.com'
    start_utr = 'https://habr.com/ru/top/'

    def __init__(self):
        self.visited_urls = set()
        self.post_links = set()
        self.post_data = []

    def parse_rows(self, url=start_utr):
        while url:
            if url in self.visited_urls:
                break
            response = requests.get(url)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url = self.get_next_page(soup)
            self.search_post_links(soup)

    def get_next_page(self, soup):
        next_page_link = soup.find('a', attrs={'id': 'next_page'})
        return f'{self.domain}{next_page_link.get("href")}' \
            if next_page_link and next_page_link.get('href') else None

    def search_post_links(self, soup):
        posts = soup.find_all('a', attrs={'class': 'post__habracut-btn'})
        posts_links = {f'{post.get("href")}' for post in posts}
        self.post_links.update(posts_links)

    def post_page_parse(self):
        for url in self.post_links[5]:
            if url in self.visited_urls:
                continue
            response = requests.get(url)
            self.visited_urls.add(url)
            soup = BeautifulSoup(response.text, 'lxml')
            self.post_data.append(self.get_post_data(soup))
            time.sleep(0.1)

    def get_post_data(self, soup):
        result = {}
        result['title'] = soup.find('span',
                                    attrs={'class': 'post__title-text'}).text
        content = soup.find('div', attrs={'id': 'post-content-body'})
        result['url'] = content.get('data-io-article-url')

        author = soup.find('a', attrs={'class': 'user-info__nickname'})
        result['writer_name'] = author.text
        result['writer_url'] = author.get('href')

        tags_ul = soup.find('ul', attrs={'class': 'js-post-tags'})
        tags_a = tags_ul.find_all('a', attrs={'rel': 'tag'})
        result['tags'] = {tag.text: tag.get('href') for tag in tags_a}
        hubs_ul = soup.find('ul', attrs={'class': 'js-post-hubs'})
        hubs_a = hubs_ul.find_all('a', attrs={'rel': 'tag'})
        result['hubs'] = {hub.text: hub.get('href') for hub in hubs_a}

        return result


if __name__ == '__main__':
    parser = HabraBestDayParser()
    parser.parse_rows()
    parser.post_page_parse()
