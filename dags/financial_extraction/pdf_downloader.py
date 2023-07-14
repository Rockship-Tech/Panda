import pdfkit
import os 
def pdf_downloader(cik,path,period, output_directory):
    '''download PDF of forms'''
    url = "https://www.sec.gov/Archives/edgar/data/{cik}/{path}".format(cik=cik, path=path)
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    output_path = os.path.join(output_directory,'{cik}_{period}.pdf'.format(period=period,cik=cik))
    pdfkit.from_url(url, output_path,configuration=config)

    print('Files are downloaded!')
    

#pdf_downloader(cik = '0001318605', path = '000095017023013890/tsla-20230331.htm', period = '20230331')