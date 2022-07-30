## Работа на проектом курсовой  
  
* В файле `env_example` лежит шаблон для .env,  который надо заполнить своими данными  
* `basic_code.py`  это шаблон для бота
* database это модуль для открытия database
* requirements.txt необходимые импортированные библиотеки `pip install -r requirements.txt`
* сделал новые функции для записи в БД  
  - add_person_to_base(vk_id, name, sex, age, city)  добавляет юзера в базу
  - add_whitelist(user_id, select_id, name, sex, age, city) добавляет в белый лист и записывает
  выбранного в базу данных
  - add_blacklist(user_id, select_id) добавляет в черный лист, в таблицу Person ничего не пишет
