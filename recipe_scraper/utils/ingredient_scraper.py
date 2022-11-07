#%%
from bs4 import BeautifulSoup

import time

from selenium import webdriver

from dotenv import load_dotenv
import re
import os
import string

import numpy as np
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.service import Service
import json
load_dotenv()

from os import listdir

#%%




# %%
import requests

x=requests.get('https://world.openfoodfacts.org/entry-date/2016-08/ingredients')

soup=BeautifulSoup(x.content,'html.parser')

# %%
[i.getText() for i in soup.find_all(class_="tag known")]
# %%

#https://stackoverflow.com/questions/20831612/getting-the-bounding-box-of-the-recognized-words-using-python-tesseract