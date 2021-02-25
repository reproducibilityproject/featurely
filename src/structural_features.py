# This Source Code Form is subject to the terms of the MIT
# License. If a copy of the same was not distributed with this
# file, You can obtain one at
# https://github.com/reproducibilityproject/featurely/blob/main/LICENSE

import os
import sys, getopt
from io import StringIO
from tabula import wrapper
from PyPDF2 import PdfFileReader
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

# function for checking if a pdf has tables or not
def check_tables(file_name):
    df = wrapper.read_pdf(str(file_name), pages='all')
    if len(df) == 0:
        return False
    else:
        return True

# function for checking if equations exist in a file
def get_references(text):
    # get the list of refs first
    list_of_refs = re.findall(r"\[(\d+)\]", text)

    # apply lamba and convert them to numbers
    list_of_refs = list(map(lambda x: int(x), list_of_refs))

    # return the max of the refs
    if len(list_of_refs) != 0:
        if not max(list_of_refs) > 200:
            return max(list_of_refs)
        else:
            return 0
    else:
        return 0

# function for getting the conference/journal rank
def get_conf_journ_rank(name):
    # add the URL
    url = 'http://www.conferenceranks.com/?searchall=' + name.split("'")[0] +'#data'

    # call obtain_content and init soup
    content = obtain_content(url)
    soup = BS(content, "html.parser")

    # return the rank of the journal/conf
    return soup.select('div tbody td')[2].get_text()

# function for getting the presence of intro sections
def is_intro_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'INTRODUCTION' in f.read() or 'Introduction' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of intro sections
def is_test_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'Implementation' in f.read() or 'METHODOLOGY' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of methodology sections
def is_meth_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'METHODOLOGY' in f.read() or 'Implementation' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of results sections
def is_res_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'RESULTS' in f.read() or 'EVALUATION RESULTS' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of results sections
def is_alg_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'Algorithm' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of results sections
def is_img_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'Figure' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of results sections
def is_hyp_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'http' in f.read() or 'https' in f.read():
            return 1
        else:
            return 0

# function for getting the presence of results sections
def is_table_pres(number):
    with open('/Users/akhil/Downloads/brown_unv_text/' + number + '.pdf.txt') as f:
        if 'Table' in f.read() or 'TABLE' in f.read():
            return 1
        else:
            return 0

# get number of pages
def no_of_pages(number):
    # read the pdf file
    pdf = PdfFileReader(open('/Users/akhil/Downloads/brown_unv/'+ number +'.pdf','rb'))

    # return the number of pages
    return pdf.getNumPages()

# get number of algorithms present
def no_alg(full_text):
    return len(Counter(re.findall('Algorithm\s[0-9]{0,2}', full_text)).keys())

# get number of images present
def no_images(full_text):
    return len(Counter(re.findall('Figure\s[0-9]{0,2}', full_text)).keys())

# get number of tables present
def no_tables(full_text):
    return len(Counter(re.findall('Table\s[0-9]{0,2}', full_text)).keys())

#converts pdf, returns its text content as a string
def convert(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text

#converts all pdfs in directory to text
def convert_to_pdf(pdf_dir, txt_dir):
    if pdf_dir == "": pdf_dir = os.getcwd() + "~/" #if no pdfDir passed in
    for pdf in tqdm(os.listdir(pdf_dir)): #iterate through pdfs in pdf directory
        fileExtension = pdf.split(".")[-1]
        if fileExtension == "pdf":
            pdf_file_name = pdf_dir + pdf
            text = convert(pdf_file_name)
            text_file_name = txt_dir + pdf + ".txt"
            text_file = open(text_file_name, "w") #make text file
            text_file.write(text)

