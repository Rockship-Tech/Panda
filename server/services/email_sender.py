import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

SENDER = os.getenv("RECRUIT_EMAIL")
AWS_REGION = os.getenv("AWS_REGION")


CHARSET = "UTF-8"


def send_email(email):
    email.recipient = "hungbk1100@gmail.com"  # for testing
    client = boto3.client("ses", region_name=AWS_REGION)

    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    email.recipient,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": email.body_html,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": email.body_text,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": email.subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
