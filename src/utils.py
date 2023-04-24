from datetime import datetime

from starlette.convertors import Convertor, register_url_convertor


class DateConvertor(Convertor):
    regex = "[0-9]{4}-[0-9]{2}-[0-9]{2}?"

    def convert(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d")

    def to_string(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d")


register_url_convertor("datetime", DateConvertor())
