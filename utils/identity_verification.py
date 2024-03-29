import os
from random import randint
from difflib import SequenceMatcher

class VerifyCompany:

    API_KEY = os.environ.get("_API_KEY")
    BASE_URL = os.environ.get('_BASE_URL')


    def initialize(self):
        return 

    @staticmethod
    def verify_cac_number(reg_number):

        if 'sample' in reg_number:
            return f'SAMPLE COMPANY {randint(1,1000)}'
        
        return ""

    @staticmethod
    def isSimilarCompanyName(a, b):
        a= a.lower()
        b= b.lower()
        ratio = SequenceMatcher(None, a, b).ratio()
        return ratio >= 0.9
