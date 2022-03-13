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
        for i in range(1, 3):
            print(f'Прокрутка страницы #{i}')
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # непосредственно прокрутка страницы
            time.sleep(3) # пауза для прогрузки постов

        print('\n')

        posts = self.driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG _bz0w']/a") # собираем все прогруженные посты
        time.sleep(1) # опциональная задержка
        post_urls = [post.get_attribute('href') for post in posts] # формируем список url адресов постов

        self.put_likes_to_posts(post_urls) # ставим лайки постам

    def put_likes_to_posts(self, posts: list, username: str = None):
        """Ставит лайки на все переданные посты, затем сохраняет пролайканные посты

        Args:
            posts (list): список url-адресов постов
            username (str, optional): имя пользователя для последующего сохранения постов в каталог с соответствующим именем. None по умолчанию
        """
        all_liked_posts = []

        for post in posts[:3]:
            self.put_like_to_post(post)
            all_liked_posts.append(post) # добавляем пост в список пролайкнных постов, чтобы потом за один раз записать все посты в файл
            time.sleep(2) # 90 - рекомендуемая задержка для избежания бана со стороны instagram

        if username: # если имя пользователя было передано, то мы лайкаем его посты и сохраняем в каталог с соответствующим именем
            print('\nСохраняем пролайканные посты пользователя...')
            self.save_all_user_liked_post(all_liked_posts, username)
            print('Посты успешно сохранены\n')

        print('\nСохраняем пролайканные посты...')
        self.save_all_liked_post(all_liked_posts)
        print('Посты успешно сохранены\n')

    def put_like_to_post(self, post: str):
        """Ставит лайк на переданный пост

        Args:
            post (str): url-адрес поста
        """
        self.driver.get(post) # получаем страницу поста
        time.sleep(3) # прогрузка страницы поста

        print(f'Ставим лайк на пост {post}...')

        # находим кнопку лайка и нажимаем на нее
        like_button = self.driver.find_element_by_xpath("//section[@class='ltpMr  Slqrh ']/span[@class='fr66n']/button[@class='wpO6b  ']")
        like_button.click()

    def is_user_path_exists(username: str):
        """Проверяет, существует ли каталог с переданным именем пользователя. Если нет - создает его

        Args:
            username (str): имя пользователя
        """
        if not os.path.exists(username):
            print(f'\nСоздаем папку пользователя {username}...\n')
            os.mkdir(username)

    def save_all_user_liked_post(self, all_liked_posts: list, username: str):
        """Сохраняет все пролайканные посты пользователя"""
        self.is_user_path_exists(username)

        with open(f'{username}/liked_posts.txt', 'a') as f:
            for liked_post in all_liked_posts:
                f.write(liked_post + '\n')

    def save_all_liked_post(self, all_liked_posts: list):
        """Сохраняет все пролайканные где-либо посты

        Args:
            post (str): url-адрес поста
        """
        with open('all_liked_posts.txt', 'a') as f:
            for liked_post in all_liked_posts:
                f.write(liked_post + '\n')

def main():
    driver = webdriver.Firefox()
    bot = InstagramBot(driver)
    bot.login(config.USERNAME, config.PASSWORD)
    bot.like_posts_by_hashtags('https://www.instagram.com/explore/tags/bmw/')

if __name__ == '__main__':
    main()