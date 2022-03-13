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

    def login(self, username: str, password: str):
        """Аутентификация

        Args:
            username (str): имя пользователя
            password (str): пароль пользователя
        """
        print('Вводим имя пользователя...')
        username_input = self.driver.find_element_by_name("username")
        username_input.send_keys(username)

        print('Вводим пароль...\n')
        password_input = self.driver.find_element_by_name("password")
        password_input.send_keys(password)  
        # password_input.send_keys(Keys.ENTER) # симуляция нажатия на enter

        login_button = self.driver.find_element_by_xpath("//button[@class='sqdOP  L3NKy   y3zKF     ']/div")
        login_button.click()
        time.sleep(5)

    def like_posts_by_hashtags(self, hashtag_page: str):
        """Ставит лайки на произвольное кол-во постов с заданным хештегом

        Args:
            hashtag (str): url страницы с заданным хештегом
        """

        self.driver.get(hashtag_page) # получаем страницу с постами по заданному хештегу
        time.sleep(3) # пауза для прогрузки контента страницы

        print('Собираем посты...\n')

        # прокручивам страницу для прогрузки постов
        for i in range(1, 5):
            print(f'Прокрутка страницы #{i}')
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # непосредственно прокрутка страницы
            time.sleep(3) # пауза для прогрузки постов

        print('\n')

        posts = self.driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG _bz0w']/a") # собираем все прогруженные посты
        time.sleep(1)
        post_urls = [post.get_attribute('href') for post in posts] # формируем список url адресов постов

        self.put_likes_to_posts(post_urls)

    def put_likes_to_posts(self, posts: list, username: str = None):
        """Ставит лайки на все переданные посты

        Args:
            posts (list): список url-адресов постов
            username (str, optional): имя пользователя для последующего сохранения постов в каталог с соответствующим именем. None по умолчанию
        """
        for post in posts:
            self.put_like_to_post(post, username)
            time.sleep(2) # 90 - рекомендуемая задержка для избежания бана со стороны instagram

    def put_like_to_post(self, post: str, username: str or None):
        """Ставит лайк на переданный пост

        Args:
            post (str): url-адрес поста
            username (strorNone): имя пользователя для последующего сохранения постов в каталог с соответствующим именем
        """
        self.driver.get(post) # получаем страницу поста
        time.sleep(3) # прогрузка страницы поста

        print(f'Ставим лайк на пост {post}...')
        like_button = self.driver.find_element_by_xpath("//section[@class='ltpMr  Slqrh ']/span[@class='fr66n']/button[@class='wpO6b  ']")
        like_button.click()

def main():
    driver = webdriver.Firefox()
    bot = InstagramBot(driver)
    bot.login(config.USERNAME, config.PASSWORD)
    bot.like_posts_by_hashtags('https://www.instagram.com/explore/tags/bmw/')

if __name__ == '__main__':
    main()