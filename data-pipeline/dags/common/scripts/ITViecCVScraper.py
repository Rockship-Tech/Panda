import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import cfscrape
import os
import urllib.parse
import unicodedata
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


class ITViecCVScraper:

    def __init__(self):
        self.session = requests.Session()
        self.s3_hook = S3Hook(aws_conn_id='aws_default')
        self.base_url = 'https://itviec.com'

    def login(self, login_url, username, password):
        """
        Logs in to the ITviec website.

        Input:
        - login_url: URL of the login page.
        - username: Username or email.
        - password: Password for the account.

        Logic:
        - Sends a GET request to the login page to fetch the authenticity_token.
        - Extracts the authenticity_token from the response HTML.
        - Sends a POST request with the login credentials and authenticity_token.
        - Checks if the login was successful based on the response status code.

        Output:
        - Returns True if the login was successful, False otherwise.
        """
        scraper = cfscrape.create_scraper()
        soup = BeautifulSoup(scraper.get(login_url).content, 'html.parser')
        self.session=scraper
        authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'})['value']

        payload = {
            'authenticity_token': authenticity_token,
            'customer[email]': username,
            'customer[password]': password,
            'customer[remember_me]': '0'
        }

        login_response = self.session.post(login_url, data=payload)

        if login_response.status_code == 200:
            print("Login successful.")
            return True
        else:
            print("Login failed.")
            return False

    def download_cv(self, cv_url, folder_name, name, email, job, submitted_date, CVs_path):
        """
        Downloads a CV file.

        Input:
        - cv_url: URL of the CV download page.
        - folder_name: Name of the folder to save the CV file.
        - name: Name of the applicant.
        - email: Email of the applicant.
        - job: Job title the applicant applied for.
        - submitted_date: Date the application was submitted.

        Logic:
        - Sends a GET request to the CV download page to fetch the download link.
        - Extracts the download link from the response HTML.
        - Sends a GET request to download the CV file.
        - Saves the CV file in the specified folder in S3.
        - Renames the CV file with a formatted filename.

        Output:
        - None
        """
        cv_response = self.session.get(cv_url, allow_redirects=False)
        cv_soup = BeautifulSoup(cv_response.content, 'html.parser')
        a_tag = cv_soup.find('a', attrs={'class': 'btn btn-danger'})['href']
        cv_response = self.session.get(a_tag)

        filename = a_tag.split('/')[-1]
        file_path = os.path.join(folder_name, filename)

        with open(file_path, 'wb') as f:
            f.write(cv_response.content)

        print(f"Downloaded file for {name} - {email}")

        new_filename = f"{unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()}_{email}_{job}_{submitted_date}.pdf"
        new_filename = new_filename.replace("/", "_")
        decoded_new_filename = urllib.parse.unquote(new_filename)
        new_file_path = os.path.join(folder_name, decoded_new_filename)

        os.rename(file_path, new_file_path)

        # Upload the CV file to S3
        s3_key = os.path.join(CVs_path, os.path.basename(new_file_path))
        if self.s3_hook.check_for_key(s3_key, bucket_name='rockship-recruitment-process'):
            print(f"File {s3_key} already exists. Skipping download.")
            return  # Skip the download and continue with the next CV

        self.s3_hook.load_file(
            filename=new_file_path,
            key=s3_key,
            bucket_name='rockship-recruitment-process',
        )

    def get_max_page(self, applications_url):
        """
        Retrieves the maximum page number from the job applications.

        Input:
        - applications_url: URL of the job applications page.

        Logic:
        - Sends a GET request to the job applications page.
        - Parses the HTML response to find the pagination element.
        - Extracts the maximum page number from the pagination links.

        Output:
        - Returns the maximum page number as an integer.
        """
        applications_response = self.session.get(applications_url)
        soup = BeautifulSoup(applications_response.content, 'html.parser')
        pagination = soup.find('ul', attrs={'class': 'pagination'})

        if not pagination:
            return 1

        last_page = 1
        for page_link in pagination.find_all('a'):
            page_number = int(page_link.text)
            last_page = max(last_page, page_number)

        return last_page

    def download_all_cvs(self, applications_url, per_page=100, CVs_path='CVs'):
        """
        Downloads all CVs from the job applications.

        Input:
        - applications_url: URL of the job applications page.
        - per_page: Number of applications to display per page (default is 100).

        Logic:
        - Retrieves the maximum page number using the get_max_page method.
        - Iterates over each page and sends a GET request to the page URL.
        - Parses the HTML response to find the table rows.
        - Extracts the applicant information and CV download URL from each row.
        - Creates a folder to save the CV files if it doesn't exist.
        - Calls the download_cv method to download and save each CV to S3.

        Output:
        - None
        """
        max_page = self.get_max_page(applications_url)

        for page in range(1, max_page + 1):
            page_url = f"{applications_url}?page={page}&per={per_page}"
            applications_response = self.session.get(page_url)

            soup = BeautifulSoup(applications_response.content, 'html.parser')
            with open('output.html', 'w') as file:
                file.write(str(applications_response.content))


            rows = soup.find_all('tr')

            for row in rows:
                if row.find('th'):
                    continue
                cells = row.find_all('td')
                name = cells[0].text.strip()
                email = cells[1].text.strip()
                print(email)
                job = cells[2].text.strip()
                submitted_date = cells[3].text.strip()
                cv_url = self.base_url + cells[4].find('a')['href']

                folder_name = 'CV'
                if not os.path.exists(folder_name):
                    os.makedirs(folder_name)

                self.download_cv(cv_url, folder_name, name, email, job, submitted_date, CVs_path)

    def get_cv_url(self, cv_page_url):
        """
        Retrieves the CV download URL from the CV page.

        Input:
        - cv_page_url: URL of the CV page.

        Logic:
        - Sends a GET request to the CV page.
        - Parses the HTML response to find the CV download URL.

        Output:
        - Returns the CV download URL as a string or None if not found.
        """
        cv_page_response = self.session.get(cv_page_url)
        cv_soup = BeautifulSoup(cv_page_response.content, 'html.parser')
        cv_download_link = cv_soup.find('a', attrs={'class': 'btn btn-danger'})['href'] if cv_soup.find('a', attrs={
            'class': 'btn btn-danger'}) else None
        return cv_download_link
