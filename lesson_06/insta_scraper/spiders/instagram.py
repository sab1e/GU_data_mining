import json
import scrapy

from scrapy.loader import ItemLoader
from scrapy.http.response import Response

from insta_scraper.items import InstaScrapyItem, AuthorInstaScrapyItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __tag_url = '/explore/tags/авто/'

    __api_tag_url = '/graphql/query/'
    __query_hash = '9b498c08113f1e09617a1703c22b2f32'
    __query_hash_post = '6ff3f5c474a240353993056428fb851e'
    __query_hash_author = 'd4d88dc1500312af6f937f7b804c68c3'

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']

        super().__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.get_js_shared_data(response)
            yield scrapy.FormRequest(
                self.__login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.__login,
                    'enc_password': self.__password
                },
                headers={
                    'X-CSRFToken': js_data['config']['csrf_token']
                }
                )
        except AttributeError as e:
            if response.json().get('authenticated'):
                yield response.follow(self.__tag_url,
                                      callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        js_data = self.get_js_shared_data(response)
        hashtag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']

        variables = {"tag_name": hashtag['name'],
                     "first": 50,
                     "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}

        url = f'{self.__api_tag_url}?query_hash={self.__query_hash}' \
              f'&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_hastag_posts)

    def get_api_hastag_posts(self, response: Response):
        posts = response.json()['data']['hashtag']['edge_hashtag_to_media']['edges']
        for post in posts:
            item_loader = ItemLoader(InstaScrapyItem(), response)
            for key, value in post['node'].items():
                if key.startswith('__'):
                    continue
                item_loader.add_value(key, value)
            if post['node']['edge_liked_by']['count'] > 100 or \
                    post['node']['edge_media_to_comment']['count'] > 30:

                variables = {
                    'shortcode': post["node"]["shortcode"],
                    'include_reel': True,
                    'include_logged_out': False,
                }
                url = f'{self.__api_tag_url}' \
                      f'?query_hash={self.__query_hash_post}' \
                      f'&variables={json.dumps(variables)}'
                yield response.follow(url, callback=self.get_api_post)
            yield item_loader.load_item()

    def get_api_post(self, response):
        author_id = response.json()['data']['shortcode_media']['owner']['id']
        variables = {
            "user_id": author_id,
            "include_chaining": True,
            "include_reel": True,
            "include_suggested_users": False,
            "include_logged_out_extras": False,
            "include_highlight_reels": True,
            "include_live_status": True
        }

        url = f'{self.__api_tag_url}' \
              f'?query_hash={self.__query_hash_author}' \
              f'&variables={json.dumps(variables)}'

        yield response.follow(url, callback=self.author_parse)

    def author_parse(self, response):
        author_data = response.json()['data']['user']['reel']['user']
        item_loader = ItemLoader(AuthorInstaScrapyItem(), response)
        for key, value in author_data.items():
            item_loader.add_value(key, value)

        yield item_loader.load_item()

    @staticmethod
    def get_js_shared_data(response):
        marker = "window._sharedData = "
        data = response.xpath(
            f'/html/body/script[@type="text/javascript" '
            f'and contains(text(), "{marker}")]/text()'
        ).extract_first()
        data = data.replace(marker, '')[:-1]
        return json.loads(data)
