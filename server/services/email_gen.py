import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


class Email:
    def __init__(self, sender, recipient, subject, body_text, body_html):
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.body_text = body_text
        self.body_html = body_html


class Welcome_email(Email):
    def __init__(self, recipient, name, job_title):
        super().__init__(
            sender=os.getenv("RECRUIT_EMAIL"),
            recipient=recipient,
            subject="Welcome to Rockship",
            body_text=f"Hello{name}\r\n"
            "Congratulations on becoming our new {job_title}!\r\n"
            "We are excited to have you on our team. You're going to do great things!\r\n",
            body_html=f"""<html>
<head></head>
<body>
  <h1>Hello {name},</h1>
  <p>Congratulations on becoming our new {job_title}!</p>
  <p> We are excited to have you on our team. You're going to do great things!</p>
</body>
</html>
            """,
        )


class Appointment_email(Email):
    def __init__(self, recipient, name, job_title, schedule_url, survey_url):
        super().__init__(
            sender=os.getenv("RECRUIT_EMAIL"),
            recipient=recipient,
            subject="Set up an interview",
            body_text=f"Hello {name},\r\n"
            f"Congratulations on becoming our new {job_title}!\r\n"
            "We are excited to have you on our team. You're going to do great things!\r\n"
            f"Please use the following link to schedule your interview: {schedule_url}\r\n"
            f"Additionally, we would appreciate if you could take a moment to fill out a survey: {survey_url}\r\n",
            body_html=f"""<html>
<head></head>
<body>
  <h1>Hello {name},</h1>
  <p>Congratulations on becoming our new {job_title}!</p>
  <p>We are excited to have you on our team. You're going to do great things!</p>
  <p>Please use the following link to schedule your interview: <a href="{schedule_url}">{schedule_url}</a></p>
  <p>Additionally, we would appreciate if you could take a moment to fill out a survey: <a href="{survey_url}">{survey_url}</a></p>
</body>
</html>""",
        )
