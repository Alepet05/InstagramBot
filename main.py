import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
import config
import time
import requests


class InstagramBot():
    def __init__(self, driver: WebDriver):
        """Инициализирует драйвер, затем открывает главную страницу instagram

        Args:
            driver (WebDriver): объект драйвера FireFox
        """
        self.driver = driver
        self.driver.get('https://www.instagram.com')
        time.sleep(5) # пауза для прогрузки главной страницы


driver = webdriver.Firefox()
bot = InstagramBot(driver)
