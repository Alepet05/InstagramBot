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

        self.put_likes_to_posts(post_urls[:3]) # ставим лайки постам

    def put_likes_to_user_posts(self, user: str):
        """Ставит лайки на посты пользователя

        Args:
            user (str): url-адрес пользователя
        """
        self.driver.get(user) # открываем страницу пользователя
        username = user.split('/')[-2] # получаем имя пользователя из url-адреса его страницы

        posts_count = int(self.driver.find_element_by_xpath("//span[@class='g47SY ']").text) # получаем кол-во постов
        iteration_count = posts_count // 12 # получаем кол-во итераций. 12 - число подгружаемых постов

        post_urls = []

        # собираем посты пользователя
        for i in range(iteration_count+1):
            posts = self.driver.find_elements_by_xpath("//div[@class='v1Nh3 kIKUG _bz0w']/a") # получаем посты на n-ой итерации
            time.sleep(1)
            for post in posts:
                post_urls.append(post.get_attribute('href')) # сохраняем url-адреса постов с n-ой итерации в список всех постов

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # прокрутка страницы
            time.sleep(3)
            print(f'Итерация №{i+1}')

        post_urls = list(set(post_urls[:3])) # из за несовершенства механизма прокрутки страницы некоторые посты продублировались, поэтому превращаем их в множество, а затем в список

        self.write_posts_to_file(username, post_urls)

        self.put_likes_to_posts(post_urls, username)

    def write_posts_to_file(self, username: str, posts: list):
        """Сохраняет посты пользователя

        Args:
            username (str): имя пользователя
            posts (list): список найденных постов пользователя
        """
        
        with open(f'{username}.txt', 'a') as f:
            for post in posts:
                f.write(post + '\n')

    def put_likes_to_posts(self, posts: list, username: str = None):
        """Ставит лайки на все переданные посты, затем сохраняет пролайканные посты

        Args:
            posts (list): список url-адресов постов
            username (str, optional): имя пользователя для последующего сохранения постов в каталог с соответствующим именем. None по умолчанию
        """
        all_liked_posts = []

        for post in posts:
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

    def save_all_user_liked_post(self, all_liked_posts: list, username: str):
        """Сохраняет все пролайканные посты пользователя"""
        self.is_user_path_exists(username)

        with open(f'{username}/liked_posts.txt', 'a') as f:
            for liked_post in all_liked_posts:
                f.write(liked_post + '\n')
    
    def is_user_path_exists(self, username: str):
        """Проверяет, существует ли каталог с переданным именем пользователя. Если нет - создает его

        Args:
            username (str): имя пользователя
        """
        if not os.path.exists(username):
            print(f'\nСоздаем папку пользователя {username}...\n')
            os.mkdir(username)

    def save_all_liked_post(self, all_liked_posts: list):
        """Сохраняет все пролайканные где-либо посты

        Args:
            post (str): url-адрес поста
        """
        with open('all_liked_posts.txt', 'a') as f:
            for liked_post in all_liked_posts:
                f.write(liked_post + '\n')

    def get_user_liked_posts(self, username: str):
        """Возвращает все пролайканные посты пользователя

        Args:
            username (str): имя пользователя

        Returns:
            list: список пролайканных постов, которые находятся в каталоге пользователя
        """
        liked_posts = []
        with open(f'{username}/liked_posts.txt') as f:
            for post in f.readlines():
                if post != '\n':
                    liked_posts.append(post.strip('\n'))
        return liked_posts

    def take_user_likes_back(self, user: str):
        """Убирает все поставленные лайки под постами пользователя

        Args:
            user (str): url-адрес пользователя
        """
        username = user.split('/')[-2] # получаем имя пользователя из url-адреса
        user_liked_posts = self.get_user_liked_posts(username) # получаем все пролайканные посты пользователя
        
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'{username}\liked_posts.txt') # формируем путь к файлу с лайкнутыми постами пользователя
        os.remove(path) # удаляем файл

        # считываем все когда-либо сохраненные лайкнутые посты
        with open('all_liked_posts.txt') as f:
            all_liked_posts = f.read()

        # пробегаемся по всем лайкнутым постам и удаляем те, что есть в списке лайкнутых постов пользователя
        for post in user_liked_posts:
            all_liked_posts = all_liked_posts.replace(post, '')
                
            self.driver.get(post) # переходим на странцу поста
            time.sleep(2) # подгрузка поста

            print(f'Убираем лайк с поста {post}...')
            like_button = self.driver.find_element_by_xpath("//section[@class='ltpMr  Slqrh ']/span[@class='fr66n']/button[@class='wpO6b  ']")
            like_button.click()

        # обновляем файл
        with open('all_liked_posts.txt', 'w') as f:
            f.write(all_liked_posts)

    def get_liked_posts(self):
        """Возвращает все пролайканные посты"""
        liked_posts = []
        with open('all_liked_posts.txt') as f:
            for post in f.readlines():
                if post != '\n':
                    liked_posts.append(post.strip('\n'))
        return liked_posts

    def take_all_likes_back(self):
        """Удаляет все поставленные где-либо лайки"""
        liked_posts = self.get_liked_posts() # получаем все пролайканные посты

        # считываем пролайканные посты из файла для его дальнейшего редактирования
        with open('all_liked_posts.txt') as f:
            lines = f.read()

        for post in liked_posts:
            # затираем пост в файле
            if post in lines:
                lines = lines.replace(post, '')

            # убираем лайк
            self.driver.get(post)
            time.sleep(2)

            print(f'Убираем лайк с поста {post}...')
            like_button = self.driver.find_element_by_xpath("//section[@class='ltpMr  Slqrh ']/span[@class='fr66n']/button[@class='wpO6b  ']")
            like_button.click()

        # обновляем файл
        with open('all_liked_posts.txt', 'w') as f:
            f.write(lines)

def main():
    driver = webdriver.Firefox()
    bot = InstagramBot(driver)
    

if __name__ == '__main__':
    main()