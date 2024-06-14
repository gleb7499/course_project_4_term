import pytest
import requests
from bs4 import BeautifulSoup


@pytest.fixture(scope='class')
def soup():
    soup = BeautifulSoup(requests.get('https://shop.mts.by/phones/').text, 'lxml')
    yield soup
