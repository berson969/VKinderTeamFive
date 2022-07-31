import pytest
import os
from sqlalchemy.orm import session

from database import Person, WhiteList, BlackList, open_session
from database import add_person_to_base


@pytest.mark.parametrize(
    'dict_info',
    [{'vk_id': '123456789', 'name': 'New Client', 'sex': 'Male',
      'age': '33', 'city': 'Moscow'},
    {'vk_id': '987654321', 'name': 'Old Client', 'sex': 'Female',
     'age': '18', 'city': 'Kirov'}]
)
def test_add_person_to_base(dict_info):
    session = open_session()
    dl = session.query(Person).filter(Person.vk_id == '123456789')
    session.delete(dl)
    session.commit()
    # r = session.query(Person).filter(Person.vk_id == dict_info['vk_id']).first()
    if session.query(Person).filter(Person.vk_id == dict_info['vk_id']).first() is None:
        assert add_person_to_base(dict_info) is True
    assert add_person_to_base(dict_info) is False



