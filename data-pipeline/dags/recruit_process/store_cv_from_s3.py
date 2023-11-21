import os
import shutil

import boto3
import json
import logging
from airflow.decorators import task
from dotenv import load_dotenv
import time
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from common.scripts.cv_handler import extract
from common.model.candidate import create_candidate, list_cv_files
from pendulum import datetime
from airflow import DAG

# load cv from s3 to current dir

# handler cv to cv entity
# store candidate to db

load_dotenv()

# Get the current path of the Python file
current_path = os.path.dirname(os.path.abspath(__file__))

# folder name is prefix's name
# folder_name = os.getenv("CVS_PATH")
folder_name = os.getenv("CVS_TEXT_PATH")
cv_folder_path = os.path.join(current_path, folder_name)

bucket_name = os.getenv("BUCKET_NAME")

default_args = {
    "retries": 0,
}

@task
def download_files_from_s3(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    folder_path = os.path.join(current_path, prefix)
    exited_file = list_cv_files()

    os.makedirs(folder_path, exist_ok=True)
    for obj in response['Contents']:
        key = obj['Key']
        filename = os.path.basename(key)
        file_path = os.path.join(folder_path, filename)

        if filename in exited_file:
            continue

        s3.download_file(Bucket=bucket_name, Key=key, Filename=file_path)

@task
def store_to_db():
    for file_name in os.listdir(cv_folder_path):
        cv_file = os.path.join(cv_folder_path, file_name)
        try:
            candidate = extract(cv_file)
            create_candidate(name=candidate['name'],
                             email=candidate['email'],
                             phone=candidate['mobile_number'],
                             cv_file=file_name,
                             cv_json=json.dumps(candidate))
        except Exception:
            logging.info(f"omitted_file::{file_name}")

    filelist = [f for f in os.listdir(cv_folder_path)]
    for f in filelist:
        os.remove(os.path.join(cv_folder_path, f))


with DAG(
        "stored_candidate_process",
        default_args=default_args,
        start_date=datetime(2023, 1, 1),
        catchup=False,
        tags=["Rockship Recruitment Process"],
) as dag:
    # Task 0: download needed files
    download_task = download_files_from_s3(bucket_name, folder_name)
    store_task = store_to_db()

    download_task >> store_task
