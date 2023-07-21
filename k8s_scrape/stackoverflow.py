import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def scrape_so(url):
    driver = webdriver.Chrome()
    driver.get(url)

    print("Answer the captcha...")
    time.sleep(60)  # Answer the captcha

    results = []
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    for element in soup.findAll(attrs={'class': 's-post-summary'}):
        question = element.find('a')
        if question not in results:
            results.append(question)
            print(question.text)


def scrape_so_kubernetes_security_tag():
    url_to_parse = 'https://stackoverflow.com/questions/tagged/kubernetes+security'
    scrape_so(url_to_parse)
