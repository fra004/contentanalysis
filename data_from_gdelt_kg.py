#this is the old file...
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
import re
import os
import requests
import zipfile
import csv
from urllib.parse import urlparse
import get_news
import kg_import
import time
import util

extract_dir = "./extracted_contents"
extract_dir_temp = "./extracted_contents_temp"

# Provide the name of news provider sites URLs in the whitelistUrls. 
# Please make sure to comply with the robot exclusion protocol as specified in robots.txt files of news provider sites 
# And comply with the terms and conditions. 
whitelistUrls = []

# Leave the following array empty as it is now
processedUrls = []

def create_directory_if_not_exists(directory_path):
    try:
        # Check if the directory already exists
        if not os.path.exists(directory_path):
            # Create the directory and its parents if they don't exist
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        else:
            print(f"Directory '{directory_path}' already exists.")
    except OSError as e:
        print(f"Error: {e}")


def delete_files_in_directory(directory_path):
    try:
        # Verify if the given path is a valid directory
        if os.path.isdir(directory_path):
            # Get a list of all files in the directory
            files = os.listdir(directory_path)
            for file in files:
                file_path = os.path.join(directory_path, file)
                # Check if the current item is a file and not a subdirectory
                if os.path.isfile(file_path):
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
            print("All files have been deleted successfully.")
        else:
            print("Invalid directory path.")
    except Exception as e:
        print(f"Error occurred: {e}")

def parse_urls_from_csv(csv_file_path):
    urls = []

    with open(csv_file_path, "r", newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        #next(reader)  # Skip the header row if it exists

        for row in reader:
            if row:  # Skip empty rows
                last_column = row[-1].strip()  # Get the last column and remove leading/trailing spaces
                #print(last_column)

            if last_column in urls: 
                continue

            for pattern in whitelistUrls:
                if last_column.startswith(pattern):
                    # Check if the last column is a valid URL
                    parsed_url = urlparse(last_column)
                    if parsed_url.scheme and parsed_url.netloc:
                        urls.append(last_column)
                        
    return urls




def download_and_extract_zip(zip_url, theDir):
    # Make sure the extraction directory exists
    os.makedirs(theDir, exist_ok=True)

    # Download the zip file
    response = requests.get(zip_url)

    # Check if the request was successful
    if response.status_code == 200:
        zip_file_path = os.path.join(theDir, "temp.zip")
        print("Printing zip file path:")
        print(zip_file_path)

        # Save the downloaded zip file
        with open(zip_file_path, "wb") as f:
            f.write(response.content)

        # Extract the contents of the zip file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(theDir)

        # Remove the temporary zip file
        os.remove(zip_file_path)
        print("Extraction complete.")
    else:
        print(f"Failed to download the zip file. Status Code: {response.status_code}")



def extract_file_location(input_string):
    # Define the regular expression pattern to match a file location
    # This pattern assumes the file path can contain any characters except whitespaces
    pattern = r"http://.*\.zip"

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    if match:
        return match.group(0)


try:    
    util.print_current_time()
    html = urlopen('http://data.gdeltproject.org/gdeltv2/lastupdate.txt')
    text = html.read().decode("utf-8") 
    zip_url = extract_file_location(text )
    delete_files_in_directory(extract_dir_temp)

    download_and_extract_zip(zip_url, extract_dir_temp)
        
    create_directory_if_not_exists(extract_dir)

    existing_file_names = os.listdir(extract_dir)
    current_file_names = os.listdir(extract_dir_temp)
    existingFile = ""
    currentFile = ""

    if len(existing_file_names) > 0:
        existingFile = existing_file_names[0]
    
    currentFile = current_file_names[0]

    print("Existing file: "+existingFile)
    print("Current file: "+currentFile)

    if currentFile != existingFile:
        # Copy paste the current file to existing file...
        delete_files_in_directory(extract_dir)
        download_and_extract_zip(zip_url, extract_dir)

        
        existing_file_names = os.listdir(extract_dir)
        csv_file_path = extract_dir + "/" + existing_file_names[0]
        parsed_urls = parse_urls_from_csv(csv_file_path)
        
        if parsed_urls:
            print("\n"*3)
            print("Parsed URLs:")
            for url in parsed_urls:
                print(url)
                print("-------------------------------------")
                try:
                    get_news.parseNewsArticle(url)
                    print("\n"*2)
                    #break
                except Exception as e:
                    print(f"Error occurred while processing the url: {e}")
        else:
            print("No valid URLs found in the CSV file.")
                
    else:
        print("Nothing to process...")

    print("\n"*2)
        
except HTTPError as e:
    print(e)
except URLError as e:
    print(e)
