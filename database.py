import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, ForeignKeyConstraint, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from bot_auth import Auth
from users import users_info

Base = declarative_base()


class Person(Base):
    """
        Наследный клаас Person, хранит сведения о пользователе ВК

        :type vk_id
        :type first_name
        :type last_name
        :type sex
        :type birth_date
        :type city_id
        :type city
        :type photos
        :type age
    """
    __tablename__ = 'persons'

    vk_id = Column(Integer, primary_key=True)
    first_name = Column(String(length=30), nullable=False)
    last_name = Column(String(length=30), nullable=False)
    sex = Column(Integer, nullable=False)
    birth_date = Column(String, nullable=True)
    city_id = Column(Integer, nullable=True)
    city = Column(String, nullable=True)
    photos = Column(String, nullable=True)
    age = Column(Integer, nullable=True)


class WhiteList(Base):
    """
            Наследный класс WhiteList хранит информацию о понравившихся людях

            :type id
            :type user_id
                :key -> Person.vk_id
            :type select_id
                :key -> Person.vk_id
        """
    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id', ondelete='CASCADE'), nullable=False)
    select_id = Column(Integer, ForeignKey('persons.vk_id', ondelete='CASCADE'), nullable=False)
    ForeignKeyConstraint(('user_id', 'select_id'), ['persons.vk_id', 'persons.vk_id'])


class BlackList(Base):
    """
        Наследный класс BlackeList хранит информацию по непонравившимся людям

        :type id
        :type user_id
            :key -> Person.vk_id
        :type select_id
    """
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id', ondelete='CASCADE'), nullable=False)
    select_id = Column(Integer, nullable=False)


def open_session():
    """
        Открывает сессию postgres
            необходимо настроить доступ к серверу postgres со своей учетной записью  postgres

    :return:  object session

    """
    driver = 'postgresql+psycopg2'
    path_db = 'localhost:5432'
    DSN = f"{driver}://{os.getenv('USER')}:{os.getenv('PASSWORD')}@{path_db}/v_kinder_db"
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_database():
    """
        Oткрывает по новой таблицы базы данных. Для последующего применения отключить вызов этой функции
    """
    session = open_session()
    Base.metadata.drop_all(session.bind)
    Base.metadata.create_all(session.bind)
    session.close()


def add_person_to_base(dict_info: dict):
    """
            Добавляет нового пользователя в таблицу Persons
    :param dict_info: dict

    :return: True при удачном коммите, False при неудачном
    """
    if isinstance(dict_info, dict):
        session = open_session()
        try:
            new_person = Person(**dict_info)
            session.add(new_person)
            session.commit()
            return True
        except sq.exc.IntegrityError:
            session.close()
    return False


def add_whitelist(user_dict_info: dict, select_dict_info: dict):
    """
            Добавляет пару id пользователя и выбранного им кандидата в базу данных в таблицу  Whitelist,
            если какого то id нет в таблице Persons записывает их в нее

    :param user_dict_info: dict
    :param select_dict_info: dict

    :return: True при удачном коммите, False при неудачном
    """
    session = open_session()
    add_person_to_base(user_dict_info)
    add_person_to_base(select_dict_info)
    result = session.query(WhiteList).filter(
        WhiteList.select_id == select_dict_info['vk_id'] and WhiteList.user_id == user_dict_info['vk_id']).first()
    if result is None:
        whitelist_person = WhiteList(user_id=user_dict_info['vk_id'], select_id=select_dict_info['vk_id'])
        session.add(whitelist_person)
        session.commit()
        return True
    session.close()
    return False


def add_blacklist(user_dict_info: dict, select_id: int):
    """
        Добавляет пару id пользователя и выбранного им кандидата в базу данных в таблицу  Blacklist,
            в таблицу Persons пишет пользователя и не пишет кандидата

        :param user_dict_info: dict пользователь бота
        :param select_id: int выбранный пользователь ВК

        :return: True при удачном коммите, False при неудачном
    """
    session = open_session()
    res = session.query(BlackList).filter(BlackList.select_id == select_id and BlackList.user_id == user_dict_info['vk_id']).first()
    if res is None:
        add_person_to_base(user_dict_info)
        blacklist_person = BlackList(user_id=user_dict_info['vk_id'], select_id=select_id)
        session.add(blacklist_person)
        session.commit()
        return True
    session.close()
    return False


def choose_favorites(vk_id: int):
    """
        Функция выводит всех понравившихся кандидатов

        :param vk_id:
        :return: favorites: json [{'id': int, 'first_name': str, 'last_name': str, 'photos': str}, ...]
    """
    session = open_session()
    res = session.query(Person).join(WhiteList, (WhiteList.select_id == Person.vk_id)).\
        filter(WhiteList.user_id == vk_id).all()
    favorites = []
    for fav in res:
        favorites.append({'id': fav.vk_id, 'first_name': fav.first_name, 'last_name': fav.last_name,
                          'photos': fav.photos})
    session.close()
    return favorites


if __name__ == "__main__":
    load_dotenv()
    # create_database()
    user = Auth()
    vk_id = os.getenv('M_VK_ID')
    n_vk_id = os.getenv('N_VK_ID')
    my_vk_id = os.getenv('VK_ID')
    my_dict_info = users_info( my_vk_id, user.gr_params, user.us_params)
    l_dict_info = users_info(os.getenv('L_VK_ID'), user.gr_params, user.us_params)
    # использовать только один раз для открытии базы, после строку закомментировать

    # print(photos_get(os.getenv('M_VK_ID')))
    result1 = add_person_to_base(users_info(vk_id, user.gr_params, user.us_params))

    result3 = add_blacklist(users_info(vk_id, user.gr_params, user.us_params), n_vk_id)

    result4 = add_whitelist(my_dict_info, l_dict_info )
    print(result4)
    fav1 = choose_favorites(my_vk_id)
    print(fav1)
    # for row in fav:
    #     print(row.vk_id, row.name)
    # print(check_blacklist(os.getenv('VK_ID'), os.getenv('LL_VK_ID')))
