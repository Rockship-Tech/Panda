# Financial Extraction

This is a Python tool used for getting PDFs of 10-Q forms from the U.S. Securities and Exchange Commission API

## Setup

### wiki.py

Install selenium.

```bash
pip install selenium
```

### pdf_downloader.py
First, download wkhtmltopdf [here](https://wkhtmltopdf.org/downloads.html).

Then install pdfkit 

```bash
pip install pdfkit
```

### pdf_converter.py
Install pdfplumber

```bash
pip install pdfplumber
```

## Usage
### Getting Companies' Symbols and CIKs

```python
# show companies' symbols and CIKs
print(wiki())
```
### Access SEC API to Get PDFs and Convert Them to .txt

```python
# Download PDFs and convert them to .txt
pdf_directory = r"dags\financial_extraction\output\10_Q_pdf"
txt_directory = r"dags\financial_extraction\output\10_Q_text"

# get the 
company_info = sec(cik = "0001652044", form = "10-Q")
for filing_period, filing_path in company_info.items():
    pdf_downloader(cik = "0001652044", 
                   path = filing_path, 
                   period=filing_period, 
                   output_directory=pdf_directory)

pdf_converter(input_directory=pdf_directory,output_directory=txt_directory)
```
