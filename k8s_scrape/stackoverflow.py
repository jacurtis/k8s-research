import time
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from k8s_scrape import export


class NoQuestionIdException(Exception):
    """Exception raised when a QuestionId could not be extracted.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="No QuestionId could be extracted from the url."):
        self.url = url
        self.message = message
        super().__init__(self.message)


def _full_url(url, baseurl = "https://stackoverflow.com"):
    if baseurl not in url:
        url = f"{baseurl}{url}"

    return url


def _get_question_id(url):
    """Extract the question id from a url.

    :argument url: The url to extract the question id from.

    :exception NoQuestionId: Raised when no question id could be extracted from the url.

    :returns: The question id.
    """
    try:
        q_id = re.search(r'/questions/(\d*)/', url).group(1)
    except AttributeError:
        raise NoQuestionIdException(url)
    return q_id


def scrape_so(url):
    driver = webdriver.Chrome()
    driver.get(url)

    while True:  # Pause on captcha
        if "nocaptcha" in driver.current_url:
            print("Answer the captcha...")
            time.sleep(15)
        else:
            break

    results = []  # Store findings
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Loop through each post summary
    for element in soup.findAll(attrs={'class': 's-post-summary'}):
        try:
            el_title = element.select_one("h3 a")
            qtitle = el_title.string
            qlink = _full_url(el_title['href'])
            qid = _get_question_id(qlink)
            # qtags = ""
            # qtime = ""
            # qvotes = 0
            # qviews = 0
            # qanswers = ""
            # qaccepted = False
            q = {"QuestionId": qid, "Title": qtitle, "Link": qlink}
            results.append(q)
            print(q)
        except NoQuestionIdException:
            print("No QuestionId could be extracted from the url.")

    return results


def scrape_so_kubernetes_tag():
    url_to_parse = 'https://stackoverflow.com/questions/tagged/kubernetes?tab=newest&pagesize=50'
    results = scrape_so(url_to_parse)

    export.to_csv([x.text for x in results], 'kubernetes.csv')
