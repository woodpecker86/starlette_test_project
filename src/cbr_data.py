from typing import Dict, List
from datetime import datetime

from xml.etree import ElementTree

import httpx

from .config import CURRENCY_RATE_SOURCE


async def get_cbr_data(date: datetime) -> List[Dict[str, str]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(CURRENCY_RATE_SOURCE, params={'date_req': date.strftime('%d/%m/%Y')})
        response.raise_for_status()
    return parse_response(response.content)


def parse_response(content: bytes) -> List[Dict[str, str]]:
    currencies = ElementTree.fromstring(content)
    data = []
    for node in currencies:
        currency = get_currency_data(node)
        data.append(currency)
    return data


def get_currency_data(node: ElementTree.Element) -> Dict[str, str]:
    data = dict()
    for elem in node:
        if elem.tag not in ('NumCode',):
            data[change_tag_to_correct_key(elem.tag)] = elem.text.replace(',', '.')
    return data


def change_tag_to_correct_key(tag_name: str) -> str:
    correct_keys = {'NumCode': 'num_code',
                    'CharCode': 'char_code'}
    return correct_keys[tag_name] if tag_name in correct_keys else tag_name.lower()
