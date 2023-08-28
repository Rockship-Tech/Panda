from selenium.webdriver import Edge
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By


def wiki():
# Browsing Wikipedia of SP500 companies
# driver_path = r"C:\Users\thanh\OneDrive\Desktop\Scraper\Finance Data Extraction\edgedriver_win64\msedgedriver.exe"
    options = webdriver.EdgeOptions()
    options.add_experimental_option("detach", True)
    driver = Edge(options=options)
    driver.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")

    # Find the table containing the desired data
    table = driver.find_element(By.CSS_SELECTOR, 'table.wikitable')

    # find all rows in the table (excluding header)
    rows = table.find_elements(By.TAG_NAME, 'tr')

    # Skip the header row
    header_row = rows[0]
    rows = rows[1:]

    # Create an empty dictionary to store the symbol and CIK values
    data = {}

    # Iterate over the table rows
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, 'td')
        if len(cells) >= 2:
            symbol = cells[0].text
            cik = cells[6].text
            data[symbol] = cik

    # Close the driver
    driver.quit()

    return data

# Print the resulting dictionary
companies = wiki()
print(companies)

 






