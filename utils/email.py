from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import  get_current_site
from django.urls import reverse
from mailjet_rest import Client
import os
import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class SendMail:
    API_KEY = os.environ.get("MAILJET_PUBLIC_KEY")
    SECRET_KEY = os.environ.get("MAILJET_PRIVATE_KEY")
    
    def initialize(self):
        mailjet = Client(auth=(self.API_KEY, self.SECRET_KEY))
        
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()

    @staticmethod
    def send_email_verification_mail(data):
        message = f'Hello {data["firstname"]},\nYour securely generated token is avalable below.\n\n{data["token"]}'
        data['email_body'] = message
        data['email_subject']= 'Verify Your Email'
        SendMail.send_email(data)

    @staticmethod
    def send_password_reset_mail(data, request):

        current_site = get_current_site(request=request).domain

        # construct url
        relativeLink = reverse(
            'password-reset-confirm', kwargs={'uid64': data["uid64"], 'token': data["token"]})

        # redirect_url = request.data.get('redirect_url', '')
        absurl = 'http://'+current_site + relativeLink

        email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
        data = {'email_body': email_body, 'to_email': data["email"],
                'email_subject': 'Reset your passsword'}
        SendMail.send_email(data)
