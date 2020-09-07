from pymongo import MongoClient

from selenium import webdriver


class OnlineTrade:
    __start_url = "https://www.onlinetrade.ru/"
    __xpath = {
        'hot_cards': '//div[@class="indexGoods"]//div[@id="tabs_hits"]'
                     '//div[@class="swiper-wrapper"]'
                     '/div[contains(@class, "indexGoods__item")]'
                     '/div[@class="indexGoods__item"]',
        'description': './div[@class="indexGoods__item__descriptionCover"]'
                       '/a',
        'price': './div[@class="indexGoods__item__price"]/span',
        'img': './a[@class="indexGoods__item__image"]/img',
        'swiper': '//div[@class="indexGoods"]//div[@id="tabs_hits"]'
                  '//span[@aria-label="Go to slide 6"]'
    }

    def __init__(self):
        self.driver = webdriver.Firefox(executable_path='./geckodriver')
        self.driver.get(self.__start_url)

        self.client_db = MongoClient()
        self.db = self.client_db['OnlineTrade']
        self.collection = self.db['hot_deals']

    def start(self):
        self.get_hot_deals_data()

    def load_all_hot_deals_cards_data(self):
        swiper_button = self.driver.find_element_by_xpath(
            self.__xpath['swiper'])
        swiper_button.click()

    def get_hot_deals_data(self):
        hot_cards = self.driver.find_elements_by_xpath(
            self.__xpath['hot_cards'])

        for card in hot_cards:
            description = card.find_element_by_xpath(
                self.__xpath['description']).text
            if description == '':
                self.load_all_hot_deals_cards_data()

            hot_deals_data = {
                'description': card. \
                    find_element_by_xpath(self.__xpath['description']).text,
                'price': card.find_element_by_xpath(
                    self.__xpath['price']).text,
                'img': card.find_element_by_xpath(self.__xpath['img']). \
                    get_attribute('src')
            }

            if hot_deals_data['description'] == '':
                continue
            else:
                self._save_to_mongo(hot_deals_data)

    def _save_to_mongo(self, hot_deals_data):
        self.collection.insert_one(hot_deals_data)


if __name__ == '__main__':
    ot = OnlineTrade()
    ot.start()
