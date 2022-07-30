import os
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    vk_id = Column(Integer, primary_key=True)
    name = Column(String(length=60), nullable=False)
    sex = Column(String, nullable=False)
    age = Column(String, nullable=False)
    city = Column(String, nullable=False)


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


def add_person_to_base(dict_info):
    session = open_session()
    new_person = Person(**dict_info)
    try:
        session.add(new_person)
        session.commit()
        return True
    except sq.exc.IntegrityError:
        session.close()
        return False


def add_blacklist(user_id, select_id):
    session = open_session()
    blacklist_person = BlackList(user_id=user_id, select_id=select_id)
    result = session.query(BlackList).filter(BlackList.user_id == user_id and BlackList.select_id == select_id).first()
    if result is None:
        session.add(blacklist_person)
        session.commit()
        return True
    else:
        session.close()
        return False


def add_whitelist(user_id, select_id):
    session = open_session()
    whitelist_person = WhiteList(user_id=user_id, select_id=select_id)
    result = session.query(WhiteList).filter(WhiteList.user_id == user_id and WhiteList.select_id == select_id).first()
    if result is None:
        # token = os.getenv('TOKEN')
        # user = VK(token, select_id)
        # select_dict_info = user.users_info()
        select_dict_info = {'vk_id': os.getenv('SELECT_ID'), 'name': os.getenv('NAME'), 'sex': os.getenv('SEX'),
                            'age': os.getenv('AGE'), 'city': os.getenv('CITY')}
        add_person_to_base(select_dict_info)
        session.add(whitelist_person)
        session.commit()
    else:
        session.close()
        return False


if __name__ == "__main__":
    # open_session()
    # create_database(open_session().bind)
    user_dict_info = {'vk_id': os.getenv('VK_ID'), 'name': os.getenv('NAME'), 'sex': os.getenv('SEX'),
                      'age': os.getenv('AGE'), 'city': os.getenv('CITY')}
    # print(user_dict_info)
    add_person_to_base(user_dict_info)
    add_blacklist(os.getenv('VK_ID'), os.getenv('SELECT_ID'))
    add_whitelist(os.getenv('VK_ID'), os.getenv('SELECT_ID'))
