import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, ForeignKeyConstraint, MetaData
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, mapper
from users import VKclass

load_dotenv()
Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    vk_id = Column(Integer, primary_key=True)
    first_name = Column(String(length=30), nullable=False)
    last_name = Column(String(length=30), nullable=False)
    sex = Column(Integer, nullable=False)
    birth_date = Column(String, nullable=False)
    city_id = Column(Integer, nullable=True)
    city = Column(String, nullable=True)


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    vk_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    likes = Column(Integer)
    photo_name = Column(String)
    # person_photo = relationship(Person, backref='persons')


class WhiteList(Base):
    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    ForeignKeyConstraint(('user_id', 'select_id'), ['persons.vk_id', 'persons.vk_id'])


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer, nullable=False)
    # ForeignKeyConstraint(['user_id', 'select_id'], ['persons.vk_id', 'blacklist.select_id'])
    # blacklist = relationship(Person, backref='blacklist')
    # person_blacklist = relationship(Person, backref='persons')


def open_session():
    """
        Открывает сессию postgres
            необходимо настроить доступ к серверу postgres со своей учетной записью  postgres
    :return: session
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
        Oткрывает поновой таблицы базы данных. Для последующего применения отключить вызов этой функции
    """
    session = open_session()
    # meta = MetaData(session.bind)
    # for table in reversed(mBase.metadata.sorted_tables):
    #     meta.Session.execute(table.delete())
    # meta.Session.commit()
    # session.execute(persons.delete())
    Base.metadata.drop_all(session.bind)
    Base.metadata.create_all(session.bind)
    session.close()


def add_person_to_base(dict_info, photo_list):
    """
            Добавляет нового пользователя в таблицу Persons
    :param dict_info: dict
    :param photo_list: json
    :return: True при удачном коммите, False при неудачном
    """
    if isinstance(dict_info, dict):
        session = open_session()
        try:
            new_person = Person(**dict_info)
            session.add(new_person)
            session.commit()
            add_photos(photo_list)
            return True
        except sq.exc.IntegrityError:
            session.close()
    return False


def add_photos(photo_list):
    """
            Добавляет в таблицу Photos  3 фото выбранного пользователя
    :param photo_list: json от функции photos_get
    :return: True при удачном коммите, False при неудачном
    """
    if isinstance(photo_list, list):
        session = open_session()
        try:
            for photo_dict in photo_list:
                new_photo = Photo(**photo_dict)
                session.add(new_photo)
            session.commit()
            return True
        except sq.exc.IntegrityError:
            session.close()
    return False


def add_blacklist(user_id, select_id):
    """
            Добавляет пару id пользователя и выбранного им кандидата в базу данных в таблицу  Blacklist,
            в таблицу Persons пишет пользователя и не пишет кандидата

    :param user_id: int пользователь бота
    :param select_id: int выбранный пользователь ВК
    :return: True при удачном коммите, False при неудачном
    """
    if check_blacklist(user_id, select_id) is True:
        session = open_session()
        add_person_to_base(user.users_info(user_id), user.photos_get(user_id))
        blacklist_person = BlackList(user_id=user_id, select_id=select_id)
        session.add(blacklist_person)
        session.commit()
        return True
    else:
        return False


def add_whitelist(user_id, select_id):
    """
            Добавляет пару id пользователя и выбранного им кандидата в базу данных в таблицу  Whitelist,
            если какого то id нет в таблице Persons записывает их в нее

    :param user_id: int
    :param select_id: int
    :return: True при удачном коммите, False при неудачном
    """
    session = open_session()
    if session.query(Person).filter(Person.vk_id == user_id).first() is None:
        add_person_to_base(user.users_info(user_id), user.photos_get(user_id))
    result = session.query(WhiteList).filter(WhiteList.select_id == select_id and WhiteList.user_id == user_id).first()
    if result is None:
        whitelist_person = WhiteList(user_id=user_id, select_id=select_id)
        add_person_to_base(user.users_info(select_id), user.photos_get(select_id))
        session.add(whitelist_person)
        session.commit()
        return True
    else:
        session.close()
        return False


# выбирает всех фаворитов для выбранного юзера
def choose_favorite(vk_id):
    session = open_session()
    favorite = session.query(Person).join(WhiteList, (WhiteList.select_id == Person.vk_id)).filter(
        WhiteList.user_id == vk_id).all()
    session.close()
    return favorite


# проверяет есть ли выбранная личность в черном списке
def check_blacklist(user_id, select_id):
    session = open_session()
    result = session.query(BlackList).filter(BlackList.select_id == select_id and BlackList.user_id == user_id).first()
    if result is None:
        return True
    else:
        session.close()
        return False


if __name__ == "__main__":
    # использовать только один раз для открытии базы, после строку закомментировать
    # create_database()
    user = VKclass()
    # print(user.photos_get(os.getenv('M_VK_ID')))
    # add_person_to_base(user.users_info(os.getenv('M_VK_ID')), user.photos_get(os.getenv('M_VK_ID')))
    add_blacklist(os.getenv('VK_ID'), os.getenv('N_VK_ID'))
    add_whitelist(os.getenv('VK_ID'), os.getenv('L_VK_ID'))
    # # response = choose_favorite(os.getenv('VK_ID'))
    # # for row in response:
    #     print(row.vk_id, row.name)
    # print(check_blacklist(os.getenv('VK_ID'), os.getenv('LL_VK_ID')))
