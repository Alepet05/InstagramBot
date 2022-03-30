import os
import config
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
import time


class InstagramBot():
    def __init__(self, driver: WebDriver):
        """Инициализирует драйвер, затем открывает главную страницу instagram

        Args:
            driver (WebDriver): объект драйвера FireFox
        """
        self.driver = driver
        self.load_page('https://www.instagram.com')
        self.subscribers_index = 2 # индекс html-элемента, отвечающего за выпадающий список подписчиков
        self.subscribings_index = 3 # индекс html-элемента, отвечающего за выпадающий список подписок

    def load_page(self, url: str):
        """Переходит на страницу по переданному url-адресу

        Args:
            url (str): url-адрес страницы
        """
        self.driver.get(url)
        time.sleep(5)

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

        login_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button")
        login_button.click()
        time.sleep(5)

    def like_posts_by_hashtags(self, hashtag_page: str):
        """Ставит лайки на произвольное кол-во постов с заданным хештегом

        Args:
            hashtag (str): url страницы с заданным хештегом
        """

        self.load_page(hashtag_page) # получаем страницу с постами по заданному хештегу

        print('Собираем посты...\n')

        # прокручивам страницу для прогрузки постов
        for i in range(1, 5):
            print(f'Прокрутка страницы #{i}')
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # непосредственно прокрутка страницы
            time.sleep(3) # пауза для прогрузки постов

        print('\n')

        posts = self.driver.find_elements_by_xpath("//div/a") # собираем все прогруженные посты
        time.sleep(1) # опциональная задержка
        post_urls = [post.get_attribute('href') for post in posts] # формируем список url адресов постов

        self.put_likes_to_posts(post_urls) # ставим лайки постам

    def put_likes_to_user_posts(self, user: str):
        """Ставит лайки на посты пользователя

        Args:
            user (str): url-адрес пользователя
        """
        self.load_page(user) # открываем страницу пользователя
        username = user.split('/')[-2] # получаем имя пользователя из url-адреса его страницы

        posts_count = int(self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span").text) # получаем кол-во постов
        iteration_count = posts_count // 12 # получаем кол-во итераций. 12 - число подгружаемых постов

        post_urls = []

        # собираем посты пользователя
        for i in range(iteration_count+1):
            posts = self.driver.find_elements_by_xpath("//div/a") # получаем посты на n-ой итерации
            time.sleep(1)
            for post in posts:
                post_urls.append(post.get_attribute('href')) # сохраняем url-адреса постов с n-ой итерации в список всех постов

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # прокрутка страницы
            time.sleep(3)
            print(f'Итерация №{i+1}')

        post_urls = list(set(post_urls)) # из за несовершенства механизма прокрутки страницы некоторые посты продублировались, поэтому превращаем их в множество, а затем в список

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
        self.load_page(post) # получаем страницу поста

        print(f'Ставим лайк на пост {post}...')

        # находим кнопку лайка и нажимаем на нее
        like_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button")
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
                
            self.load_page(post) # переходим на странцу поста

            print(f'Убираем лайк с поста {post}...')
            like_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button")
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
            self.load_page(post)

            print(f'Убираем лайк с поста {post}...')
            like_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button")
            like_button.click()

        # обновляем файл
        with open('all_liked_posts.txt', 'w') as f:
            f.write(lines)

    def get_iteration_count(self, html_el_index: int):
        """Возвращет кол-во итераций

        Args:
            html_el_index (int): индекс html-элемента подписчиков/подписок в зависимости от места, из которого был вызван метод

        Returns:
            int: кол-во итераций для прокрутки списка подписок/подписчиков
        """
        user_count = self.driver.find_element_by_xpath(f"/html/body/div[1]/section/main/div/header/section/ul/li[{html_el_index}]/a/div/span").get_attribute('title')
        iteration_count = int(user_count.replace(',', '').replace(' ', '')) // 12 # 12 - число подгружаемых подписчиков/подписок
        
        return iteration_count

    def get_users_list(self, html_el_index: int):
        """Возвращает html-элемент, представляющий собой список пользователей

        Args:
            html_el_index (int): индекс html-элемента подписчиков/подписок в зависимости от места, из которого был вызван метод
        
        Returns:
            WebElement: объект selenium, представляющий собой список пользователей
        """
         # выпадающее окно с пользователями
        users = self.driver.find_element_by_xpath(f"/html/body/div[1]/section/main/div/header/section/ul/li[{html_el_index}]/a/div")
        users.click()
        time.sleep(2)

        users_list = self.driver.find_element_by_xpath(f"/html/body/div[6]/div/div/div/div[{html_el_index}]") # непосредственно сам элемент-список пользователей, для его дальнейшей прокрутки
        
        return users_list

    def get_users_elements(self, html_el_index: int):
        """Получает информацию, необходимую для дальнейшей работы с пользователями

        Args:
            html_el_index (int): индекс html-элемента подписчиков/подписок в зависимости от места, из которого был вызван метод

        Returns:
            tuple: кол-во итераций, html-элемент, представляющий собой список пользователей
        """

        iteration_count = self.get_iteration_count(html_el_index)
        users_list = self.get_users_list(html_el_index)

        return iteration_count, users_list

    def get_users(self, iteration_count: int, users_list: WebElement):
        """Возвращает пользователей, которые являются либо подписчиками, либо подписками

        Args:
            iteration_count (int): кол-во итераций для прокрутки списка пользователей
            users_list (WebElement): html-элемент-список пользователей, который нужно прокручивать для получения очередных пользователей
            
        Returns:
            list: список url-адресов пользователей
        """
        users = []

        for _ in range(iteration_count+1):
            users_hrefs = self.driver.find_elements_by_xpath('//div/span/a')
            time.sleep(1)

            # добавляем очередных пользователей в список всех пользователей
            for user_href in users_hrefs[1:]:
                users.append(user_href.get_attribute('href'))

            # прокручиваем список пользователей дальше
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", users_list)
            time.sleep(2)

        return users

    def subscribe_to_users(self, user: str):
        """Подписывается на пользователей, которые находятся в подписчиках у переданного пользователя

        Args:
            user (str): url-адрес пользователя
        """
        # заходим на страницу пользователя
        self.load_page(user)

        # подписка на переданного пользователя
        # находим кнопку подписки и тыкаем на нее, иначе пользователь уже подписан
        try:
            subscribe_button = self.driver.find_element_by_class_name('jIbKX')
            subscribe_button.click()
            time.sleep(1)
        except:
            username = user.split('/')[-2] # получаем имя пользователя из Url-адреса
            print(f'Вы уже подписаны на {username}')

        user_subscribers_urls = list(set(self.get_users(*self.get_users_elements(self.subscribers_index))))

        # подписка на найденных пользователей
        for user_subscriber in user_subscribers_urls:
            self.load_page(user_subscriber) # переходим на страницу пользователя

            username = user_subscriber.split('/')[-2]

            try:
                closed_profile = self.driver.find_element_by_class_name('_4Kbb_') # уникальный класс для закрытых профилей
            except:
                closed_profile = False

            if closed_profile:
                try:
                    subscribe_button = self.driver.find_element_by_class_name('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')
                    subscribe_button.click()
                    print(f'Вы подали заявку {username}')
                    time.sleep(2)
                except:
                    print(f'Вы уже подали заявку {username}')
            else:
                try:
                    subscribe_button = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')
                    subscribe_button.click()
                    print(f'Вы подписались на {username}')
                    time.sleep(2)
                except:
                    print(f'Вы уже подписаны на {username}')

    def unsubscribe_from_all_users(self, user: str):
        """Отписка от всех пользователей

        Args:
            user (str): url-адрес пользователя
        """
        self.load_page(user) # заходим на странцу пользователя

        iteration_count = self.get_iteration_count(self.subscribings_index)

        # производится отписка от первых 12 найденных подписок
        # далее перезагружаем страницу и отписываемся от следующих 12 подписок
        for _ in range(iteration_count+1):
            self.load_page(user) # перегружаем страницу для генерации следующих подписок
            
            self.get_users_list(self.subscribings_index)

            subscribings = self.driver.find_elements_by_xpath("/html/body/div[6]/div/div/div/div[3]/ul/div/li") # находим аккаунты подписок

            for subscribing in subscribings:
                user = subscribing.find_element_by_tag_name('a').get_attribute('href') # получаем ссылку на аккаунт подписки
                username = user.split('/')[-2] # получаем имя пользователя через url-адрес

                unsubscribe_button = self.driver.find_element_by_xpath("/html/body/div[6]/div/div/div/div[3]/ul/div/li/div/div[3]/button") # находим кнопку отписки в том же списке
                unsubscribe_button.click()
                time.sleep(1)

                # подтверждаем отписку
                confirm_button = self.driver.find_element_by_class_name('aOOlW') # /html/body/div[7]/div/div/div/div[3]/button[1] на всякий оставлю абсолютный путь
                confirm_button.click()
                time.sleep(1)

                print(f'Отписались от {username}')

    def unsubscribe_from_unsubscribed_users(self, user: str):
        """Отписка от пользователей, которые не подписались в ответ

        Args:
            user (str): url-адрес пользователя
        """
        self.load_page(user)

        user_subscribers_urls = set(self.get_users(*self.get_users_elements(self.subscribers_index)))

        self.load_page(user) # перегружаем страницу

        user_subscribings_urls = set(self.get_users(*self.get_users_elements(self.subscribings_index)))

        unsubscribed_users_urls = list(user_subscribers_urls - user_subscribings_urls) # выполняем вычитание множеств. Таким образом, получаем неподписанных в ответ пользователей

        for unsubscribed_user_url in unsubscribed_users_urls:
            username = unsubscribed_user_url.split('/')[-2]

            self.load_page(unsubscribed_user_url)

            print(f'{username} не подписался на нас в ответ. Отписываемся от него...')

            unsubscribe_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button")
            unsubscribe_button.click()

            time.sleep(2)

            confirm_button = self.driver.find_element_by_class_name('aOOlW') # /html/body/div[6]/div/div/div/div[3]/button[1]
            confirm_button.click()
            time.sleep(2)

            print(f'Отписались от {username}')

    def send_message_to_user(self, user: str, message: str):
        """Отправляет сообщение пользователю

        Args:
            user (str): имя пользователя, которому нужно отправить сообщение
            message (str): текст сообщения
        """
        self.load_page('https://www.instagram.com')

        username = user.split('/')[-2]

        self.disable_notifications()

        direct_button = self.driver.find_element_by_xpath("/html/body/div[1]/section/div/div[1]/div/div[3]/div/div[2]/a")
        direct_button.click()
        time.sleep(3)

        self.disable_notifications()

        send_message_button = self.driver.find_element_by_class_name('/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/div[3]/div/button')
        send_message_button.click()
        time.sleep(3)

        # ------------------
        # for username in users: если хотим рассылать сообщения нескольким пользователям
        user_input = self.driver.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div[1]/div/div[2]/input")
        print('Вводим имя пользователя...')
        user_input.send_keys(username)
        time.sleep(3)

        add_user = self.driver.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div[2]/div[1]") # кнопка добавления пользователя
        add_user.click()
        time.sleep(1)
        # -----------------

        next_button = self.driver.find_element_by_xpath("/html/body/div[6]/div/div/div[1]/div/div[3]/div/button/div")
        next_button.click()
        time.sleep(3)

        self.disable_notifications()

        message_placeholder = self.driver.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea")
        print('Вводим текст сообщения...')
        message_placeholder.send_keys(message)
        message_placeholder.send_keys(Keys.ENTER) # нажимаем enter для отправки сообщения
        time.sleep(2)

    def disable_notifications(self):
        """Отказывается от всплывающих уведомлений"""
        #time.sleep(3)
        cancel_notification_button = self.driver.find_element_by_class_name('aOOlW')
        cancel_notification_button.click()
        time.sleep(3)

    def close(self):
        """Закрывает соединение"""
        self.driver.close() # закрывает тольку 1 вкладку
        self.driver.quit() # полностью выходит из браузера

def main():
    driver = webdriver.Chrome(executable_path='chromedriver\\chromedriver.exe')
    bot = InstagramBot(driver)
    bot.login(config.USERNAME, config.PASSWORD)
    # используйте здесь нужные методы
    bot.close()

if __name__ == '__main__':
    main()