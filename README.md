# boundaries_congress
Code to download, merge, and clean congressional data. 

### Project Overview
The purporse of this project is to build a text extraction parser to generate data from daily congress speaches for a given time period. This data will then be used to investigate how, when, and why immigration-related boundary rhetoric has changed over a period of time. Congress session speaches are recorded in a PDF and HTML document, and for this boundary rhetoric analysis, we are interested in mostly getting details around which days the congress session occurs, the speaker who speaks, the congress session (Senate/House) where the speech occurs, and the raw text that was spoken in the session. This dataset will also contain metadata on speeches and their speakers such as party affiliation, state, gender, location. The data will be downloaded by building a scraper software in python, which will go through the given congress session or date, and builds an JSON output form the HTML input. The JSON output will have a key-value pair relationship with the list of characters generated based on the needs.

In summary, the base code aims to perform the below key steps:

1. **Get files** Scrape files from Congressional Record for the given congress session or session date.
    * This step builds a modeule to pull a specified congressional day and parses the HTML document using Beautiful Soup package. The html document is then read as an xml file to get the list of child sessions with data and metadata containing the list of sections, pages, the text in each section.
2. **Parse the generated tags** with in the data from each Congressional Record, XML tags are read using python and NLP techniques to generate a metrics to get: 
		* The Congress session Title
		* The generated session URL 
		* List of pages in the HTML Document
		* RAW text that was used in the congress session
		* Cleaned Text to remove special characters, and stop words
		* Speaker details of the name of the speaker speaking in the session
		* Speaker Role and affiliation details
3. **EDA on Generated data** The purpose of this EDA analysis is to generate a summary of the parsed congress speach text generated through the developed code repo! This process opens the JSON file outpu generated for a particular date, reads the inputs as a data frame, transforms the data by cleaning up and removing a set of stop words, and then generates statistics around the number of pages in a given congress speach date, number of speakers, along with character, and word counts. The input to this analysis is a set of input dates on which to perform the analysis. These results are then compared with the stanford data, to compare the results.


### Output Details
	This project goes through the scraper and build the below outputs:

    * content folder: This folder will have all the raw data downloaded as a zip file from congress website, and extracted into a folder
    * json_output: This folder will have the parsed and generated results in a json format. Json data will be in a key:value pair, with key as the parsed section title, and value as parsed text value. example: Speakers is the key for all speaker names, and the values will be the congress member speaking in a particular session
    * metadata: This folder will have a json output with metadata of the parsed results. This metadata will include the input key and value as in html, and can be used for any further analysis
    * tmp: This is a tmp director, and is used throughout the process to to extract zip files and to transform text to html and pdf

### Next Steps:
	This is a work in progress project, and the logical next steps would be to build a stop word repository to remove stop words from the cleaned text for further modelling.