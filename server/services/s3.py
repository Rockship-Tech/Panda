import boto3
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)  # Load env before run powerpaint


def upload_file_to_s3(file_data, bucket, s3_filename):
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).put_object(Key=s3_filename, Body=file_data)
