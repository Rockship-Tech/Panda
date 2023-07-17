import os
import sys
from airflow import DAG
from airflow.decorators import task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from pendulum import datetime
import logging

# Add the common module to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
common_dir = os.path.join(current_dir, '..', 'common')
sys.path.append(common_dir)

from common.scripts.ITViecCVScraper import ITViecCVScraper
from common.scripts.pdf_converter import pdf_converter
from dotenv import load_dotenv



# Load environment variables from .env file
load_dotenv()

AWS_CONN_ID = os.getenv('AWS_CONN_ID')
bucket_name = os.getenv('BUCKET_NAME')
CVs_path = os.getenv('CVs_path')
CVs_text_path = os.getenv('CVs_text_path')

default_args = {
    "retries": 2,
}

@task
def crawl_cvs_task():
    # Task 0: Crawl all CVs from itviec.com
    # ITviec.com login info
    # later save in airflow variable for more security
    login_url = os.getenv('ITVIEC_LOGIN_URL')
    applications_url = os.getenv('ITVIEC_APPLICATIONS_URL')
    username = os.getenv('ITVIEC_USERNAME')
    password = os.getenv('ITVIEC_PASSWORD')

    downloader = ITViecCVScraper()
    if downloader.login(login_url, username, password):
        downloader.download_all_cvs(applications_url, per_page=10)

    # Check if CVs have been downloaded
    if os.path.exists("CV"):
        cv_files = os.listdir("CV")
        cv_files = cv_files[:10]  # Select only the first 10 CVs for testing
        for filename in cv_files:
            if filename.endswith(".pdf"):
                pdf_file_path = os.path.join("CV", filename)
                print(f"Downloaded {pdf_file_path}")

@task
def download_pdf_file(s3_file):
    # Task 1: Download the PDF file from S3 to local
    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    local_pdf_path = f"/tmp/{os.path.basename(s3_file)}"
    s3_hook.download_file(bucket_name, s3_file, local_pdf_path)
    return local_pdf_path

@task
def convert_pdf_to_text_task(pdf_file_path):
    # Task 2: Convert PDF to text using pdfplumber
    text = pdf_converter(pdf_file_path)
    return text

@task
def upload_text_file(text, s3_file):
    # Task 3: Upload the text file to S3
    text_file_name = os.path.splitext(os.path.basename(s3_file))[0] + ".txt"
    local_text_path = f"/tmp/{text_file_name}"

    # Save the text to a local file
    with open(local_text_path, 'w') as text_file:
        text_file.write(text)

    # Upload the text file to S3
    s3_hook = S3Hook(aws_conn_id=AWS_CONN_ID)
    s3_hook.upload_file(local_text_path, bucket_name, s3_file)
    return local_text_path

@task
def remove_local_files(pdf_file_path, text_file_path):
    # Task 4: Remove the local PDF and text files
    os.remove(pdf_file_path)
    os.remove(text_file_path)


with DAG(
    'cv_processing_dag',
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["Rockship Recruitment Process"]
) as dag:
    # Task 0: Crawl all CVs from itviec.com
    crawl_cvs = crawl_cvs_task()

    # Task 1: Retrieve and convert PDFs to text
    cv_files = S3Hook(aws_conn_id=AWS_CONN_ID).list_keys(bucket_name=bucket_name, prefix=CVs_path)
    retrieve_and_convert_pdfs = []
    for cv_file in cv_files:
        if cv_file.lower().endswith(".pdf"):
            pdf_file_path = download_pdf_file(cv_file)
            text = convert_pdf_to_text_task(pdf_file_path)
            text_file_path = upload_text_file(text, cv_file)
            logging.info(f"Converted PDF to text: s3://{bucket_name}/{cv_file}")
            retrieve_and_convert_pdfs.append((pdf_file_path, text_file_path))
    
    # Set task dependencies
    crawl_cvs >> retrieve_and_convert_pdfs >> remove_local_files
