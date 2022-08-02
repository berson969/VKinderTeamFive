import os
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from users import VKcls

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    vk_id = Column(Integer, primary_key=True)
    name = Column(String(length=60), nullable=False)
    sex = Column(Integer, nullable=False)
    birth_date = Column(String, nullable=False)
    city_id = Column(Integer, nullable=True)
    city = Column(String, nullable=True)
    photo0 = Column(String)
    photo1 = Column(String)
    photo2 = Column(String)

class WhiteList(Base):
    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    ForeignKeyConstraint(['user_id', 'select_id'], ['persons.vk_id', 'persons.vk_id'])


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer, nullable=False)
    # ForeignKeyConstraint(['user_id', 'select_id'], ['persons.vk_id', 'blacklist.select_id'])
    # blacklist = relationship(Person, backref='blacklist')
    person = relationship(Person, backref='persons')


def create_database(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def open_session():
    load_dotenv()
    driver = 'postgresql+psycopg2'
    path_db = 'localhost:5432'
    DSN = f"{driver}://{os.getenv('USER')}:{os.getenv('PASSWORD')}@{path_db}/v_kinder_db"
    engine = create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


# добавляет юзера в базу
def add_person_to_base(dict_info):
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


# добавляет в черный лист, в таблицу `Person` ничего не пишет
def add_blacklist(user_id, select_id):
    if check_blacklist(user_id, select_id) is True:
        session = open_session()
        blacklist_person = BlackList(user_id=user_id, select_id=select_id)
        session.add(blacklist_person)
        session.commit()
        return True
    else:
        return False


# добавляет в белый лист и записывает выбранного в базу данных
def add_whitelist(user_id, select_id):
    session = open_session()
    if session.query(Person).filter(Person.vk_id == user_id).first() is None:
        add_person_to_base(user.users_info(user_id))
    result = session.query(WhiteList).filter(WhiteList.select_id == select_id and WhiteList.user_id == user_id).first()
    if result is None:
        whitelist_person = WhiteList(user_id=user_id, select_id=select_id)
        add_person_to_base(user.users_info(select_id))
        session.add(whitelist_person)
        session.commit()
    else:
        session.close()
        return False


# выбирает всех фаворитов для выбранного юзера
def choose_favorite(vk_id):
    session = open_session()
    favorite = session.query(Person).join(WhiteList, (WhiteList.select_id == Person.vk_id)).filter(WhiteList.user_id == vk_id).all()
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
    load_dotenv()
    # open_session()
    # использовать только один раз для открытии базы, после строку закомментировать
    # create_database(open_session().bind)
    token = os.getenv('ACCESS_TOKEN_214815089', )
    user = VKcls(os.getenv('ACCESS_TOKEN_214815089'), os.getenv('ACCESS_USER_berson2005@yandex.ru'))
    add_person_to_base(user.users_info(os.getenv('M_VK_ID')))
    # add_blacklist(os.getenv('VK_ID'), os.getenv('N_VK_ID'))
    # add_whitelist(os.getenv('VK_ID'), os.getenv('L_VK_ID'))
    # response = choose_favorite(os.getenv('VK_ID'))
    # for row in response:
    #     print(row.vk_id, row.name)
    # print(check_blacklist(os.getenv('VK_ID'), os.getenv('LL_VK_ID')))


