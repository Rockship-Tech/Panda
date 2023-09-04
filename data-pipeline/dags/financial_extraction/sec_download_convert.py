from sec import sec
from pdf_downloader import pdf_downloader
from pdf_converter import pdf_converter

# set directory path where the pdf files are located
pdf_directory = r"panda\dags\financial_extraction\output\10_Q_pdf"
txt_directory = r"panda\dags\financial_extraction\output\10_Q_text"

# get the 
company_info = sec(cik = "0001652044", form = "10-Q")
# print(company_info)
for filing_period, filing_path in company_info.items():
    pdf_downloader(cik = "0001652044", path = filing_path, period=filing_period, output_directory=pdf_directory)

pdf_converter(input_directory=pdf_directory,output_directory=txt_directory)