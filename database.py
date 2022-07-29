import os
from dotenv import load_dotenv
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class Person(Base):
    __tablename__ = 'persons'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
    name = sq.Column(sq.String(length=60))
    href = sq.Column(sq.String(length=60))


class WhiteList(Base):
    __tablename__ = 'whitelist'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('persons.vk_id'), nullable=False)
    select_id = sq.Column(sq.Integer, sq.ForeignKey('persons.vk_id'), nullable=False)

    white_relation = relationship(Person, backref='whitelist')


class BlackList(Base):
    __tablename__ = 'blacklist'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('persons.vk_id'), nullable=False)
    select_id = sq.Column(sq.Integer)

    black_relation = relationship(Person, backref='blacklist')


def create_database():
    load_dotenv()
    driver = 'postgresql'
    path_db = 'localhost:5432'

    DSN = f"{driver}://{os.getenv('USER')}:{os.getenv('PASSWORD')}@{path_db}/vkinder_db"
    engine = sq.create_engine(DSN)
    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    session.close()


if __name__ == "__main__":
    create_database()
