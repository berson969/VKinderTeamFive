## Работа на проектом курсовой  
  
* В файле `env_example` лежит шаблон для .env,  который надо заполнить своими данными  
* Также для работы `Selenium` потребуется установить драйвер к браузеру Chrome инструкция по его установке находится [здесь](https://selenium-python.com/install-chromedriver-chrome)
* `basic_code.py`  это шаблон для бота
* database это модуль для открытия database
* requirements.txt необходимые импортированные библиотеки `pip install -r requirements.txt`
* сделал новые функции для записи в БД  
  - `add_person_to_base()`  добавляет юзера в базу
  - `add_whitelist(user_id, select_id, name, sex, brith_year, city)` добавляет в белый лист и записывает
  выбранного в базу данных
  - `add_blacklist(user_id, select_id)` добавляет в черный лист, в таблицу `Person` ничего не пишет
  - `choose_favorite(vk_id)`   выбирает всех фаворитов для выбранного юзера


## Функции в модуле `users.py`
* в модуле  `users.py`находится три  функции 
  - `users_info(vk_id: int, gr_params)`  функция принимает `vk_id` id  клиента информацию по которому запрашиваем
  - в ответ приходит словарь следующего вида
  ```
   user_dict_info { 'vk_id': int, 'first_name': srt, 'last_name': str, 'sex': int
                             'city_id': int, 'city':  str ,'birth_date': str
                             }
  ```
    если каких то данных нету, в ответе `''`
* `photos_get(vk_id: int, us_params)` получает также  `vk_id` клиента и формирует список словарей следующего вида
  ```
  "photo_list список словарей [ {'id': int, 'likes': int,
                  'vk_id': int, 'photo_name': str (photo12345_12345)}, ... ,  
  ```
* `search_users(user_id: int, gr_params: str , us_params: str, offset=0)` получает информацию о клиенте `user_id`. Выполняет поисковый запрос на условиях `city_id` , `age_from`, `age_to`, а также поиск пропивоположного пола, 
Кроме этого, производится отбраковка анкет которые закрыты для просмотра `is_closed==True`
## Функцианал модуля `access_token.py`
* Модуль   `access_token.py`  автоматически получает токены необходимые для работы программы. Для корректной работы необходимо в `.env` заполнить поля `VK_LOGIN` и `VK_PASSWORD`. Полученные токены
также записываются в файл `.env`  под именами `GROUP_TOKEN` и `USER_TOKEN`.  Для корректной работы требуется самостоятельная установка [`chromedriver`](https://selenium-python.com/install-chromedriver-chrome) для версии chrome, установленного на вашем компьютере.
Для корректной авторизации необходимо отключить двухфакторную идентификацию в ВК или переставить ее с SMS на PUSH. Для повторной генерации токенов, необходимо закомментировать или удалить в .env текущие токены.

## Модуль  аутентификации `bot_auth.py`  
  - Создает класс `Auth`, который используется для авторизации запросов к базе данных ВК всеми другими модулями
  - Все действия автоматические при обращению к классу.
  - Существуют два типа ключей : групповые для сообществ в ВК (используется приствка gr_) и индивидуальная для конкретного пользователя ( используется приставка us_)

##  Модуль бота  `basic_code.py`

 ---
 - основная функция `messangerBot`  принимает сообщения от клиента и работает с ними по определенной схеме.
 - `show_selected()` подготавливает отправку фотографий для показа пользователю
 - `write_msg( params)` отправка новых сообщений 
 - `edit_msg( params)` редактирование и отправка (у меня так и не заработала)
 - 
 - `keyboard_creator()` формирует различные клавиатуры для сообщений
 - метод `_iter_selected()`  обеспечивают показ сообщений поочередно.
