import os
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    vk_id = Column(Integer, primary_key=True)
    name = Column(String(length=60))
    sex = Column(String, nullable=False)
    age = Column(String, nullable=False)
    city = Column(String, nullable=False)


class WhiteList(Base):
    __tablename__ = 'whitelist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('persons.vk_id'), nullable=False)
    select_id = Column(Integer)


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


def add_person_to_base(vk_id, name, sex, age, city):
    session = open_session()
    new_person = Person(vk_id=vk_id, name=name, sex=sex, age=age, city=city)
    try:
        session.add(new_person)
        session.commit()
    except sq.exc.IntegrityError:
        session.close()


# def add_person_to_base1(vk_id, **kwargs):
#     session = open_session()
#     data_key = 'vk_id=vk_id,'
#     for key, value in kwargs.items():
#         print (key, value)
#         data_key += f' {key}={value},'
#     data_key.strip(',')
#     print(data_key)
#     new_person = Person(kwargs)
#     try:
#         session.add(new_person)
#         session.commit()
#     except sq.exc.IntegrityError:
#         session.close()

def add_blacklist(user_id, select_id):
    session = open_session()
    blacklist_person = BlackList(user_id=user_id, select_id=select_id)
    session.add(blacklist_person)
    session.commit()


def add_whitelist(user_id, select_id, name, sex, age, city):
    session = open_session()
    whitelist_person = WhiteList(user_id=user_id, select_id=select_id)
    add_person_to_base(select_id, name, sex, age, city)
    session.add(whitelist_person)
    session.commit()


if __name__ == "__main__":
    # open_session()
    create_database(open_session().bind)
    # kwargs = {}
    # vk_id = os.getenv('VK_ID')
    # kwargs['name'] = os.getenv('NAME')
    # kwargs['gender'] = os.getenv('SEX')
    # kwargs['birth_year'] = os.getenv('AGE')
    # kwargs['town_residence'] = os.getenv('CITY')
    # add_person_to_base1(vk_id, **kwargs)

    add_person_to_base(os.getenv('VK_ID'), os.getenv('NAME'), os.getenv('SEX'), os.getenv('AGE'), os.getenv('CITY'))
    add_blacklist(os.getenv('VK_ID'), os.getenv('SELECT_ID'))
    add_whitelist(os.getenv('VK_ID'), os.getenv('SELECT_ID'), os.getenv('NAME'), os.getenv('SEX'), os.getenv('AGE'), os.getenv('CITY'))

