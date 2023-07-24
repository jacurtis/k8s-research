from bs4 import BeautifulSoup
from selenium import webdriver

def scrape_getheaders():
    driver = webdriver.Chrome()
    driver.get("https://httpbin.org/headers")

    content = driver.page_source
    # soup = BeautifulSoup(content, 'html.parser')
    #
    # for element in soup.findAll(attrs={'class': 's-post-summary'}):
    #     question = element.find('a')
    #     if question not in results:
    #         results.append(question)
    #         print(question.text)

    print(content)

