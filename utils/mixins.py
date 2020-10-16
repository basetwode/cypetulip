import threading
import time

from django.core.checks import translation
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class EmailMixin:
    email_template = ''

    def get_template(self):
        return self.email_template

    def send_mail(self, receiver_user, content, subject, context):
        EmailThread(receiver_user, content, subject, context, self.get_template()).start()


class EmailThread(threading.Thread):
    def __init__(self, receiver_user, content, subject, context, email_template):
        self.subject = subject
        self.context = context
        self.content = content
        self.email_template = email_template
        self.receiver_user = receiver_user
        threading.Thread.__init__(self)

    def run(self):

        result = None
        tries = 0
        while (result is None or result is not 1) and tries < 5:
            try:
                print("Sending new email to " + self.receiver_user.email)
                self.context['content'] = self.content
                html_content = render_to_string(self.email_template, context=self.context)
                print(self.content)

                email = EmailMultiAlternatives('Subject', self.subject)
                email.subject = self.subject
                email.attach_alternative(html_content, "text/html")
                email.to = [self.receiver_user.email]
                print("from " + email.from_email)
                print("Sending mail")
                tries += 1
                result = email.send()
                print(result)
            except Exception as e:
                print(e)
                print("Error when sending mail... retrying")
                time.sleep(15)
        return result