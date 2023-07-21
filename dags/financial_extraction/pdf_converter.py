import os 
import pdfplumber


# Iterate over the PDF files in the directory

def pdf_converter(input_directory, output_directory):
    '''Convert PDF files from an input directory and generate TXT files from output directory
        Arguments:
        - input_directory: the directory that contains the PDF files
        - output_directory: the desired directory to contain the TXT files'''
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".pdf"):

            # Construct the full path of the PDF file
            file_path = os.path.join(input_directory, file_name)

            # Specify the output file name for the extracted text 
            output_file = os.path.join(output_directory, os.path.splitext(file_name)[0]+".txt")

        # open pdf file
        with pdfplumber.open(file_path) as pdf:    
            
            
            # extracting text and save it into .txt file 
            with open(output_file,"w", encoding = "utf-8") as file:
                
                # Extract text from each page
                for page in pdf.pages:
                    text = page.extract_text(raw = True)    
                    file.write(text)

        print("Text has been exported to", output_file)

