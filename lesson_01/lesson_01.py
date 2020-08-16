import requests
import json
import time
import os


class Parser5ka:
    _domain = 'https://5ka.ru'
    _api_path = '/api/v2/special_offers/'
    _categories_path = '/api/v2/categories'
    params = {
        'records_per_page': 20,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) "
                      "Gecko/20100101 Firefox/78.0",
    }

    def __init__(self):
        self.products_by_categories = []

    def download(self):
        categories_url = self._domain + self._categories_path
        response = requests.get(categories_url, headers=self.headers)
        categories_data = response.json()

        for categoria in categories_data:
            url = self._domain + self._api_path

            offers_by_categoria = {
                'name': categoria['parent_group_name'],
                'code': int(categoria['parent_group_code']),
                'products': []
            }

            self.params['categories'] = offers_by_categoria['code']
            params = self.params

            while url:
                response = requests.get(url,
                                        headers=self.headers,
                                        params=params)
                data = response.json()
                params = {}
                url = data['next']
                offers_by_categoria['products'].extend(data['results'])
                time.sleep(0.1)

            if offers_by_categoria['products']:
                self.products_by_categories.append(offers_by_categoria)

    def save_to_file(self):
        for categoria in self.products_by_categories:
            file_path = os.path.join(os.getcwd(), categoria['name'] + '.json')
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(categoria, json_file, ensure_ascii=False)


if __name__ == '__main__':
    parser = Parser5ka()
    parser.download()
    parser.save_to_file()
