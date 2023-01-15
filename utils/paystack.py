from os import environ
import requests
from random import randint
from rest_framework.exceptions import ParseError

from transactions.models import CHOICES_FOR_STATUS, CHOICES_FOR_PAYMENT_METHOD
from users.models import User


PAYSTACK_SECRET_KEY = environ.get('PAYSTACK_SECRET_KEY', '')
PAYSTACK_BASE_URL = environ.get('PAYSTACK_BASE_URL', '')


def chargeCard():
    try:

        # data={}
        # headers = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}
        # url = f'{PAYSTACK_BASE_URL}/charge'

        # requests.post(
        #     url,
        #     data,
        #     headers,
        # )
        index = randint(0,2)
        return {
            "status": CHOICES_FOR_STATUS[index][0], 
            "payment_method": CHOICES_FOR_PAYMENT_METHOD[0][0]}
    
    except Exception as e:
        raise ParseError(e.args)

def generateTransactionReference():
    try:
        token = User.objects.make_random_password(
            length=10, 
            allowed_chars=f'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz')

        return f'rfb_{token}'

    except Exception as e:
        raise ParseError(e.args)
