from django.utils import timezone
from datetime import datetime
from typing import Union


def greater_than_today(input_date: Union[datetime, str] ) -> bool :
    try:

        if isinstance(input_date, str):
            ## convert string to date
            input_date = datetime.strptime(input_date, '%Y-%m-%d %H:%M:%S')

        return input_date > timezone.now()

    except Exception as e:
        return False


def convert_datetime_to_readable_date(input_date: Union[datetime.date, str]) -> str:
    try:

        if isinstance(input_date, str):
            # convert string to date
            input_date = datetime.strptime(input_date, '%Y-%m-%d %H:%M:%S')


        x_time = input_date.time()
        formatted_date = input_date.strftime("%a,%d %b, %Y")
        formatted_time =  x_time.strftime("%H-%M-%S")

        return f'{formatted_time} {formatted_date}'

    except Exception as e:
        raise e
