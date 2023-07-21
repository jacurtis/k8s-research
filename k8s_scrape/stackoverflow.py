import time

from bs4 import BeautifulSoup
from selenium import webdriver
from k8s_scrape import export


def scrape_so(url):
    driver = webdriver.Chrome()
    driver.get(url)

    print("Answer the captcha...")
    # time.sleep(60)  # Answer the captcha

    results = []
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    for element in soup.findAll(attrs={'class': 's-post-summary'}):
        question = element.find('a')
        if question not in results:
            results.append(question)
            print(question.text)

    return results


def scrape_so_kubernetes_security_tag():
    url_to_parse = 'https://stackoverflow.com/questions/tagged/kubernetes+security'
    results = scrape_so(url_to_parse)

    export.to_csv([x.text for x in results], 'kubernetes-security.csv')
