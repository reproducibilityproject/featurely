# This Source Code Form is subject to the terms of the MIT
# License. If a copy of the same was not distributed with this
# file, You can obtain one at
# https://github.com/reproducibilityproject/featurely/blob/main/LICENSE

import os
import re
import sys
import time
import random
import urllib
import numpy as np
import pandas as pd
from tqdm import tqdm
from ast import literal_eval
from bs4 import BeautifulSoup
from collections import Counter

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from openpyxl import Workbook, load_workbook

# function for highlighting the user to solve CAPTCHA
def solve_captcha():
    """
    Post the user a message asking to solve for CAPTCHA
    Parameters
    ----------
    None
    Returns
    -------
    Nothing
    """
    raw_input('Please, solve the CAPTCHA and press ENTER: ')

# function for obtaining the altmetric id from the DOI
def obtain_altmetric_id(dataframe, url):
    """
    Obtain the altmetric id by parsing the DOI
    from the given dataframe
    Parameters
    ----------
    arg1 | dataframe: pandas.DataFrame
        The pandas dataframe object
    arg2 | url: str
        The google scholar URL of the scholarly article
    Returns
    -------
    Integer
        int
    """
    try:
        # use the url to capture the doi
        doi = url.split('=')[1]

        # return the altmetric id
        return dataframe.loc[dataframe.doi.apply(lambda x: x) == doi].altmetric_id.values[0]
    except:
        # return an NA value
        return np.nan

# function for obtaining the citations from the parsed html
def obtain_citation(file_name):
    """
    Obtain the citation from the soup elements
    Parameters
    ----------
    arg1 | file_name: str
        The name of the file name
    Returns
    -------
    String
        str
    """
    try:
        # open and read the file
        f = open(file_name).readlines()

        # read the contents of the file
        with open(file_name, 'r') as f:
            # read the soup elements
            contents = f.read()

            # read the file contents as BS4 object
            soup = BeautifulSoup(contents, 'lxml')

            # identify all the div elements
            divs = soup.findAll("div", {"class": "gs_fl"})

            # identify all the hrefs
            if len(divs) > 1:
                href = divs[1].find_all('a')[2]
            else:
                href = divs[0].find_all('a')[2]

        # return the text
        return href.text
    except:
        # return NA
        return np.nan

# function for preparing the URL's text file
def prepare_urls(dataframe, outfile_name, write=False):
    """
    Prepare the google scholar urls with DOI's
    of the scholarly articles added at the end
    Parameters
    ----------
    arg1 | dataframe: pandas.DataFrame
        The pandas dataframe object
    arg2 | outfile_name: str
        The output file name to write the URLS
    arg3 | write: bool
        Flag to decide if the file is to be written to disk
    Returns
    -------
    Array
        list
    """
    # read the dataframe
    dois = dataframe.doi.values.tolist()

    # add the scholarly url
    scholarly_url = 'https://scholar.google.com/scholar_lookup?doi='

    # add the url to every doi
    urls = list(map(lambda x: scholarly_url + x, tqdm(dois)))

    # write to a file
    if write:
        # write one line at a time
        for url in tqdm(urls):
            # open an empty file
            f = open(outfile_name, 'a')

            # add the urls
            f.write(url)

            # add a line break
            f.write('\n')

            # close the file
            f.close()

    # retun the urls
    return urls

# function for detecting and solving the captcha
def checkload(url, element_id):
    """
    Function that attempts to solve the
    given CAPTCHA for the URL
    Parameters
    ----------
    arg1 | url: str
        The google scholar URL of the scholarly article
    arg1 | element_id: bs4.
        The google scholar URL of the scholarly article
    Returns
    -------
    Integer
        int
    """
    # set the flag for checking if the page loaded
    loaded_correctly = False

    # set the attempt rate to 1
    attempt = 1

    # until the page has loaded continue
    while loaded_correctly == False:
        try:
            # obtain the url using bs4 object
            br.get(url)

            # find the element by XPATH
            html = br.find_element_by_xpath('//html').get_attribute('innerHTML').encode('utf-8')

            # condition 1 for checking the captcha
            if html.find("Please show you're not a robot") > 0:
                # post the message
                solve_captcha()
            elif html.find("your computer or network may be sending automated queries") > 0:
                # post the message
                solve_captcha()
            elif html.find("Demuestra que no eres un robot") > 0:
                # post the message
                solve_captcha()
            elif html.find("inusual procedente de tu red de ordenadores") > 0:
                # post the message
                solve_captcha()
            elif html.find("Our systems have detected unusual traffic from your computer") > 0:
                # post the message
                solve_captcha()

            # identify the correct element ID
            doc_list = br.find_element_by_class_name(element_id)

            # set the flag to false notifying the end of the loop
            loaded_correctly = True
        except:
            # check if this is the first attempt
            if attempt == 1:
                # pipe out message highlighting
                print('THE FOLLOWING URL COULDN\'T BE DOWNLOADED:')
                print(url)
                break
            loaded_correctly = False
            print('Trying again ' + url)
            attempt += 1
            time.sleep(2)


