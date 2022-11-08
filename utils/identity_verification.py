import os

class VerifyCompany:

    API_KEY = os.environ.get("_API_KEY")
    BASE_URL = os.environ.get('_BASE_URL')


    def initialize(self):
        return 

    @staticmethod
    def verify_cac_number(reg_number):
        
        if 'sample' in reg_number:
            return 'XXX SAMPLE COMPANY ORG XXX'
        
        return