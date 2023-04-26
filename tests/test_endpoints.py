from datetime import datetime

from src.main import finance_app as app

from . import samples_for_tests as sft


def test_start_page(client):
    url = app.url_path_for('start_page')
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['date'] == datetime.now().strftime('%Y-%m-%d')
    assert not len(response.json()['currencies']) == 0


def test_get_data_from_prev_date(client):
    response = client.get('/2002-04-22')
    assert response.status_code == 200
    assert response.json()['date'] == '2002-04-22'
    assert response.json()['currencies'] == sft.DATA_FROM_2002_04_22


def test_incorrect_date(client):
    response = client.get('/2002-12-222')
    assert response.status_code == 404


def test_get_currency_codes(client):
    url = app.url_path_for('get_currency_codes')
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['currencies'] == sft.CURRENCY_CODES


def test_get_rates(client):
    url = app.url_path_for('get_currency_rates')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()['rates']) == 60


def test_get_rates_pagination(client):
    url = app.url_path_for('get_currency_rates') + '?limit=20&offset=1'
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.json()['rates']) == 20
    assert response.json()['rates'] == sft.PAGINATION_SET


def test_delete_rates_without_char_code(client):
    url = app.url_path_for('delete_currency_rates')
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['Msg'] == 'not specified currency char_code'


def test_delete_rates(client):
    url = app.url_path_for('delete_currency_rates') + '?char_code=USD'
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['Number of deleted rates'] == 2


def test_repeat_delete_rates(client):
    url = app.url_path_for('delete_currency_rates') + '?char_code=USD'
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['Number of deleted rates'] == 0
