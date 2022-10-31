from django.core.mail import EmailMessage


import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class SendMail:
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