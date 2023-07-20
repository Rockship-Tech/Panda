import logging
import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from main_celery import celery

CHARSET = "UTF-8"

FORGET_PASSWORD_TEMPLATE = """Hi {staff.first_name},
Click here to confirm: {link_reset_pw}
Your reset_password_token is : {staff.reset_password_token}
"""


def send_mail_forgot_password(staff, subject, link_reset_pw):
    message = FORGET_PASSWORD_TEMPLATE.format(staff=staff, link_reset_pw=link_reset_pw)
    send_email.delay(staff._email, subject, message)


def message_formatter(from_email, to_email, subject, message):
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg_body = MIMEMultipart('alternative')
    html_part = MIMEText(message.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(html_part)
    msg.attach(msg_body)
    return msg


@celery.task(name='tasks.mail.send_mail')  
def send_email(to_email, subject, message):    
    from_email = os.getenv("NO_REPLY_MAIL")
    s = smtplib.SMTP(os.getenv("AWS_SMTP_HOST"))
    try :
        s.connect(os.getenv("AWS_SMTP_HOST"), 587)
        s.starttls()
        s.login(os.getenv("AWS_SMTP_USERNAME"), os.getenv("AWS_SMTP_PASSWORD"))
        message = message_formatter(from_email, to_email, subject, message)
        s.sendmail(from_email, to_email, message.as_string())
        logging.debug("Email sent.")
    except Exception as e:
        logging.debug(e)
    finally:
        s.quit()
