"""
Author: Sundar Jayaraman
Date: Jul/29/2021

Core module to scrape data from the congress website for a given date.
This module will go through and build the below outputs:
    1. content folder: This folder will have all the raw data downloaded as a zip file from congress website, and extracted into a folder
    2. json_output: This folder will have the parsed and generated results in a json format. Json data will be in a key:value pair, with key as the parsed section title, and value as parsed text value. example: Speakers is the key for all speaker names, and the values will be the congress member speaking in a particular session
    3. metadata: This folder will have a json output with metadata of the parsed results. This metadata will include the input key and value as in html, and can be used for any further analysis
    4. tmp: This is a tmp director, and is used throughout the process to to extract zip files and to transform text to html and pdf
"""

import os
import errno
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.request
import zipfile as  zp
import shutil
import io

# an array of dates to generate the CREC data for.
# This array can be substituted with an output from "generate_date.py"script: which generates a list of all the dates in a given congress session
dateString = ['1994-12-01', '1996-10-04', '1998-07-23', '2000-06-07', '2002-07-26', '2003-06-05', '2005-06-23', '2008-11-17', '2010-12-22', '2021-02-24', '2021-06-07', '2021-06-08']
# dateString = ['2021-06-08']

# Function to the get the Zip file from the govinfo API. The input value is the date sting in the format (YYYY-MM-DD).
# This function gets the zip containing PDF and HTML output, and saves the html output in the path "content/pkg/CREC-/html"
def get_zip_file_and_extract(dateString):

    urlOfZipFile = 'https://www.govinfo.gov/content/pkg/CREC-' + dateString + '.zip'

    fileSavePath = urlOfZipFile[24:len(urlOfZipFile)]

    print(fileSavePath)

    headers = {
                    'User-Agent': 'My Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
                }
    req = urllib.request.Request(urlOfZipFile, headers=headers)
    zipfileHandle = urllib.request.urlopen(req)
    zipfile = zipfileHandle.read()
    print(zipfile)

    try:
        os.makedirs(os.path.dirname(fileSavePath))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
                # fileExists('Tried to create a directory that later existed. This is probably a race condition where another instance Zip file finished first.')
        # else:
        #     raise fileExists('Tried to create a directory that did not exist and now exists. Something is wrong in requestHTMLFile.')
    with open(fileSavePath, "wb") as f:
        f.write(zipfile)


    file_cr_zip = io.BytesIO(zipfile)
    pyZipHandle = zp.ZipFile(file_cr_zip,mode='r')
    try:
        os.makedirs(os.path.dirname('tmp'))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            pass # this is okay
        else:
            pass
            # probably handle this
    pyZipHandle.extractall(path='tmp')
    try:
        shutil.rmtree('content/pkg/'+'CREC-'+dateString+'/html/')
    except FileNotFoundError as exc:
        try:
            os.makedirs(os.path.dirname('content/pkg/'+'CREC-'+dateString+'/'))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                pass # probably ok
            else:
                pass
                # probably handle this
    try:
        os.makedirs(os.path.dirname('metadata/pkg/'+'CREC-'+dateString+'/'))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            pass # this is okay
        else:
            pass
            # probably handle this
    shutil.move('tmp/CREC-'+dateString+'/html', 'content/pkg/'+'CREC-'+dateString+'/html/')
    shutil.move('tmp/CREC-'+dateString+'/mods.xml', 'metadata/pkg/'+'CREC-'+dateString+'/mods.xml')


# This function gets the html outputs for all the input urls.
# URLs are generated from the CREC web scrape
def Gather_HTML(url):

    urlSplit = url.split('/')
    if urlSplit[2] != 'www.govinfo.gov':
        raise
            # WrongWebsiteException('htm file is not from govinfo.gov. Aborting.')
    fileSavePath = url[24:len(url)]
    # Check to see if we've already created this file path
    if os.path.exists(os.path.dirname(fileSavePath)) and os.path.exists(fileSavePath):
        # handle getting cached file
        cachedHTMLFile = open(fileSavePath, "r")
        cachedHTML = cachedHTMLFile.read()
        cachedHTMLFile.close()
        return cachedHTML
    else:
        # handle caching new file
        downloadHTML = requests.get(url)
        try:
            os.makedirs(os.path.dirname(fileSavePath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
                    # fileExists('Tried to create a directory that later existed. This is probably a race condition where another instance downloading CR data finished first.')
        with open(fileSavePath, "w") as f:
            f.write(downloadHTML.text)
        return downloadHTML.content

# this function takes the datestring, and retuns the core metadata from the given html file.
# This function uses BeautifulSoup to scrape the html/xml, and returns the document content.
def Gather_Metadata(dateString, returnFullDateString = False):
    fullDateString = 'CREC-' + dateString
    urlString = 'https://www.govinfo.gov/metadata/pkg/' + fullDateString + '/mods.xml'
    cr_xml_data = Gather_HTML(urlString)
    parsed_cr = BeautifulSoup(cr_xml_data, "xml")
    mods = list(parsed_cr.children)[0]
    if returnFullDateString == True:
        return mods, fullDateString
    return mods


# %% Clean section text
# function to process individual session by removing the extraneous page numbers, headers, white spaces, and newlines from the input string
def Process_Individual_Section(section):
    '''
    This function takes a section of text and:
        1. Removes extraneous page numbers
        2. Removes everything in the header
        3. Removes some newline spaces
        4. Replace some newlines with newline + tab
    Parameters
    ----------
    section : string
        string of text representing a section in the congressional crecord
    Returns
    -------
    cleaned_section : string
        Condensed text without new lines and such
    '''

    # Remove extraneous page #'s, which appear either as [H123] or [S123]
    page_pattern = re.compile(r"""
                        \n\n            # identify preceeding newlines to the pages.
                        \[+             # Start with one or more open brackets
                        Page            # Our string ends with something like [Page H123]]
                        \s              # Whitespace
                        [HS]            # Either 'H' or 'S'
                        \d+             # At least one digit
                        \]+             # Ending bracket(s)
                        \s              # Any remaining whitespace before the start of our text
                         """,
                              re.VERBOSE | re.MULTILINE)
    cleaned_section = re.sub(page_pattern, ' ', section)  # replace above with space.

    # Remove everything in the header (Congressional Record Volume all the way up to
    #  www.gpo.gov
    header_pattern = re.compile(r"""
                        \[             # Start with an open bracket
                        Congressional   # Then theterm Congressional Record Volume
                        \s              # Include this in case reading the PDF gives us extra white spaces in between words
                        Record          # Continuation of Congressional Record Volume
                        \s              # More undetermined whitespace
                        Volume          # End of Congressional Record Volume
                        .*              # Find everything between the beginning and end
                        \[              # Our string ends with something like [www.gpo.gov]
                        www.gpo.gov     # The URL
                        \]              # Closing bracket
                        \n+             # tack on extra newlines
                        \s+             # Any final whitespace
                        """,
                                re.VERBOSE | re.MULTILINE | re.DOTALL)

    cleaned_section = re.sub(header_pattern, '', cleaned_section)

    # Remove some newline spaces
    # remove formatting newlines that do not start new paragraph
    new_line_pattern = re.compile("\n(?=\S)")
    cleaned_section = re.sub(new_line_pattern, '', cleaned_section)

    # address new paragraph newlines... replace with newline and tab
    new_line_pattern2 = re.compile("\n\s{2}(?=[A-Z])")
    cleaned_section = re.sub(new_line_pattern2, '\n\t', cleaned_section)

    # remove initial space that "centers" the title text and any extra
    # newlines at the end
    return cleaned_section.strip()

# This function is designed to get a basic basic parser to generate any individual session.
# The input is the soup html tag of the given child element, and the output is an json key value pair of key fields extracted.
# Key parsed outputs are: CR session, title of document, url, page number, datetime, raw_text, cleaned_text, speaker, speaker affiliation, speaker role, and citations
# since there are multiple speakers in a session, this function get the data in a nested dictionary with multiple speaker data.

def Generate_Individual_Section(child_element):
    parsedSection = {}
    try:
        print(child_element)
        parsedSection['CR_Section'] = child_element.partName.text
        parsedSection['title'] = child_element.title.text
        urlOfReferencedText = child_element.location.find('url',{'displayLabel':"HTML rendition"}).text
        parsedSection['url'] = urlOfReferencedText
        parsedSection['Pages'] = child_element.start.text + ' - ' + child_element.end.text
        # print(child_element.volume.text)
        # print(child_element.accessId.text)
        # print(child_element.issue.text)
        # print(child_element.dateIssued.text)
        # print(child_element.extension.volume.text)
        # print(child_element.partName.text)
        # print(child_element.title.text)
        # print(child_element.extent)
        # print(child_element.start)
        # print(child_element.end)
        cong_mem = child_element.congMember
        # print((cong_mem))
        # print(child_element.find_all('congMember',{'type':"personal"}))
        # wrap the below function in some kind of cached file checker which will cache the html files it pulls
        html_rend_pull = Gather_HTML(urlOfReferencedText)
        bs4_html_rend_pull = BeautifulSoup(html_rend_pull, 'html.parser')
        parsedSection['raw_text'] = bs4_html_rend_pull.body.pre.text
        parsedSection['cleaned_text'] = Process_Individual_Section(parsedSection['raw_text'])
        parsedSection['Speakers'] = [name.namePart.text for name in child_element.find_all('name',{'type':"personal"})]
        parsedSection['Speaker Affiliation'] = child_element.affiliation.text
        parsedSection['Speaker Role'] = child_element.roleTerm.text
    except AttributeError:
        return None
    try:
        parsedSection['citation'] = child_element.find('identifier',{'type':'preferred citation'}).text
    except AttributeError: #probably should be done in a cleaner way so that if the citation is missing code still runs.
        raise
            # CitationError('Missing Preferred Citation in parseSection')
    return parsedSection

# parse the metadata and return the list of parsed sections
def GenerateHierarchyMetadata(mods):
    listOfParsedSections = []
    for child in mods:
        name = getattr(child, "name", None)
        if name is not None:
            temp = Generate_Individual_Section(child)
            if temp is not None:
                listOfParsedSections.append(temp)
    return listOfParsedSections

# this function stores the json file path, and document metadata path
def StoreMetadata(listAsJSON, jsonSavePath):
    try:
        os.makedirs(os.path.dirname(jsonSavePath))
    except FileExistsError:
        #ignore the fact the file exists and overwrite it below
        pass
    with open(jsonSavePath, "w") as f:
        f.write(listAsJSON)
    return

# this function converts the core data into a json file from the parsed output.
# the json output is saved in the directory, with datesting as a prefix: 'json_output/Cleaned-'
def GenerateJSON(listOfParsedSections):
    listAsJSON = json.dumps(listOfParsedSections)
    return listAsJSON

# This function runs the code for all the given input dates, and generates HTML, and JSON output in the given path
for dte in dateString:
    print("Processing for the date: ", dte)
    mods, fullDateString = Gather_Metadata(dte, returnFullDateString = True)

    # print(mods)
    jsonSavePath = 'json_output/Cleaned-' + fullDateString + '.json'
    listOfParsedSections = GenerateHierarchyMetadata(mods)
    listAsJSON = GenerateJSON(listOfParsedSections)
    StoreMetadata(listAsJSON,jsonSavePath)
    # print(listAsJSON)
    # print(listOfParsedSections)