"""
Author: Sundar Jayaraman
Date: Jun/15/2021

Core module to test the download of data in a zip format!
"""

test_url='https://www.govinfo.gov/content/pkg/CREC-2017-02-02/pdf/CREC-2017-02-02.pdf'

import urllib.request

download_url = 'www.govinfo.gov/content/pkg/CREC-2017-02-02/pdf/CREC-2017-02-02.pdf'
# pdf_path=

def download_file(download_url, filename):
    resp = urllib.request.urlretrieve(download_url, "filename.pdf")
    # response = urllib.request.urlopen(download_url)
    # file = open(filename + ".pdf", 'wb')
    # file.write(response.read())
    # file.close()


download_file(download_url, "Test")