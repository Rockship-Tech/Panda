import requests


def convert_path(path_string):
    # Remove hyphens and colon using the replace() method
    split_string = path_string.split(':')
    split_string[0] = split_string[0].replace('-','')

    converted_string = split_string[0]+'/'+split_string[1]

    return converted_string

def sec(cik, form):
    '''
        Access SEC API and URL to get the required paths to the necessary forms
        Arguments:
            cik (string): Companies' CIK code 
            form_type (string): The form type needed (10-Q, 10-K, etc.)
    '''
    
    # Accessing SEC API and URL

    url = "https://efts.sec.gov/LATEST/search-index?category=custom&forms={form_type}&ciks={cik}&startdt=2018-07-05&enddt=2023-07-05".format(cik = cik, form_type = form)
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67"}
    response = requests.get(url, headers=header)
    
    # Get the filings 
    filings = response.json()['hits']['hits']
    
    filing_info = {}
    filing_path = []
    filing_period = []

    for filing in filings:
        filing_path = convert_path(filing['_id'])
        filing_period = filing['_source']['period_ending'].replace('-','')
        filing_info[filing_period] = filing_path

    return filing_info


#print(sec(cik = "0001652044", form = "10-Q"))


