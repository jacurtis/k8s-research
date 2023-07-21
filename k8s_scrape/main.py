import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

URL_TO_PARSE = 'https://stackoverflow.com/search?tab=relevance&q=kubernetes&searchOn=3'

driver = webdriver.Chrome()
driver.get(URL_TO_PARSE)
time.sleep(60) # Answer the captcha

results = []
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

for element in soup.findAll(attrs={'class': 's-post-summary'}):
    question = element.find('a')
    if question not in results:
        results.append(question)
        print(question.text)

# print(results)