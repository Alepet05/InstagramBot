# InstagramBot
Бот для автоматизации действий в Instagram
# Установка
* Склонируйте репозиторий командой git clone "https://github.com/u5er-name/instagram_bot.git"
* Выполните команду "pip install -r requirements.txt"
# Настройка
* В файле config.py впишите свои имя пользователя и пароль
* Убедитесь, что версия драйвера соответствует вашей версии браузера Chrome (текущая версия драйвера: 100.0.4896.60). Иначе, на сайте https://chromedriver.storage.googleapis.com/index.html выберите нужную версию и распакуйте архив в каталог бота с заменой
# Использование
В функции main после аутентификации, но до закрытия соединения вызвать один из следующих методов:
* bot.like_posts_by_hashtags('hashtag') - пролайкать посты по заданному хештегу
* bot.put_likes_to_user_posts('user_url') - пролайкать посты пользователя
* bot.take_user_likes_back('user') - убрать поставленные лайки с постов пользователя
* bot.take_all_likes_back() - убрать все поставленные лайки
* bot.subscribe_to_users('user_url') - подписка на пользователей переданного пользователя (включая его)
* bot.unsubscribe_from_all_users('your_profile_url') - отписка от пользователей
* bot.unsubscribe_from_unsubscribed_users('your_profile_url') - отписка от неподписавшихся в ответ пользователей
* bot.send_message_to_user('user_url') - рассылка сообщений пользователю/пользователям