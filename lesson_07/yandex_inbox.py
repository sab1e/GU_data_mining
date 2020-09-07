import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotInteractableException,\
    StaleElementReferenceException


class YandexMail:
    __start_url = "https://passport.yandex.ru/auth?from=mail&origin=hostroot_homer_auth_ru&retpath=https%3A%2F%2Fmail.yandex.ru%2F&backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1"

    def __init__(self, *args, **kwargs):
        self.__login = kwargs['login']
        self.__password = kwargs['password']
        self.driver = webdriver.Firefox(executable_path='./geckodriver')
        self.driver.get(self.__start_url)

        self.client_db = MongoClient()
        self.db = self.client_db['YandexMail']
        self.collection = self.db['mail']

    def start(self):
        self.login()
        mail_list = self.get_all_mail_list()
        self.get_inbox_mail(mail_list)

    def login(self):
        __query = {
            'enter_button': 'HeadBanner-Button-Enter',
            'login': 'passp-field-login',
            'password': 'passp-field-passwd',
            'control_load': 'AuthSocialBlock-provider'
        }

        input_login = self.driver.find_element_by_id(__query['login'])
        input_login.send_keys(self.__login, Keys.RETURN)

        input_password = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, __query['password']))
        )
        input_password.send_keys(self.__password, Keys.ENTER)

    def get_inbox_mail(self, inbox_mails):
        __query = {
            'mail_from': 'mail-Message-Sender-Email',
            'mail_date': 'ns-view-message-head-date',
            'mail_title': 'mail-Message-Toolbar-Subject',
            'mail_text': '//div[contains(@class, "mail-Message-Body-Content")]/div',
        }

        for mail in inbox_mails:
            mail_list_wait = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'mail-MessageSnippet')
                )
            )

            mail.click()

            mail_body_wait = WebDriverWait(
                self.driver,
                10,
                ignored_exceptions=StaleElementReferenceException).until(
                EC.presence_of_element_located(
                (By.CLASS_NAME, __query['mail_from']))
            )

            mail_data = {
                'mail_from': self.driver.find_element_by_class_name(
                    __query['mail_from']).text,
                'mail_date': self.driver.find_element_by_class_name(
                    __query['mail_date']).text,
                'mail_title': self.driver.find_element_by_class_name(
                    __query['mail_title']).text,
            }

            mail_text_elements = self.driver.find_elements_by_xpath(
                __query['mail_text']
            )
            mail_text = ''
            for text_element in mail_text_elements:
                mail_text += text_element.text
            mail_data['mail_text'] = mail_text

            self._save_to_mongo(mail_data)

            self.driver.back()

    def get_all_mail_list(self):
        __query = {
            'button_more_mails': 'mail-MessagesPager-button',
            'inbox_mails_list': 'mail-MessageSnippet',
        }
        try:
            while True:
                el = WebDriverWait(
                        self.driver, 50,
                        ignored_exceptions=StaleElementReferenceException). \
                    until(EC.presence_of_element_located((
                    By.CLASS_NAME, __query['button_more_mails']))
                )
                button_more_mails = self.driver.find_element_by_class_name(
                    __query['button_more_mails']
                )
                button_more_mails.click()
        except ElementNotInteractableException:
            inbox_mails_list = self.driver.find_elements_by_class_name(
                __query['inbox_mails_list']
            )
            return inbox_mails_list

    def _save_to_mongo(self, mail_data):
        self.collection.insert_one(mail_data)


if __name__ == '__main__':
    load_dotenv(dotenv_path=Path('.env').absolute())
    ya_mail_mining = YandexMail(
        login=os.getenv('YA_LOGIN'),
        password=os.getenv('YA_PASSWORD')
    )

    ya_mail_mining.start()
