from django.utils import timezone
from datetime import datetime
from typing import Union


def greater_than_today(input_date: Union[datetime.date, str] ) -> bool :
    try:

        if isinstance(input_date, str):
            ## convert string to date
            input_date = datetime.strptime(input_date, '%Y-%m-%d').date()

        return input_date > timezone.now().date()

    except Exception as e:
        print(e)
        return False