import random
import time
import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from k8s_scrape.export import export, merge


class NoQuestionIdException(Exception):
    """Exception raised when a QuestionId could not be extracted.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="No QuestionId could be extracted from the url."):
        self.url = url
        self.message = message
        super().__init__(self.message)


def _full_url(url, baseurl="https://stackoverflow.com"):
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


def _get_post_meta_tags(element):
    """Extract the meta tags from a post summary element.

    :argument element: The post summary element to extract the meta tags from.

    :returns: The meta tags.
    """
    tags = []
    ul = element.select(".s-post-summary--meta-tags > ul")
    for li in ul:
        tags.append(li.text)


def scrape_so_index_page(tag: str = "kubernetes", filename: str = "../datasources/kubernetes.csv", pages: int = 1,
                         page_start: int = 1, page_size: int = 50) -> pd.DataFrame:
    """Scrape Stack Overflow search index pages by passing in an url

    :param tag: The tag to search for on StackOverflow. Default is "kubernetes".
    :param filename: The name and path where to save the file as. Default is "../datasources/kubernetes.csv".
    :param pages: The number of pages to scrape. Default is 1.
    :param page_start: The page number to start scraping from. Default is 1.
    :param page_size: The number of results per page. Default is 50.

    :returns: A Pandas DataFrame containing the scraped data.
    """
    url_to_parse = f"https://stackoverflow.com/questions/tagged/{tag}?tab=newest&page={page_start}&pagesize={page_size}"

    results = []  # Store findings
    driver = webdriver.Chrome()
    driver.get(url_to_parse)

    for page in range(1, pages + 1):
        # Pause on captcha
        while True:
            if "nocaptcha" in driver.current_url:
                print("Answer the captcha...")
                time.sleep(15)
            else:
                break

        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')

        # Loop through each post summary
        for element in soup.findAll(attrs={'data-post-id': True}):
            try:
                el_title = element.select_one("h3 a")
                qtitle = el_title.string
                qlink = _full_url(el_title['href'])
                qid = _get_question_id(qlink)
                qtags = [li.text for li in element.select(".s-post-summary--meta-tags > ul > li")]
                qcontent = element.find_next("div", {"class": "s-post-summary--content-excerpt"}).text.strip()
                qtime = element.select_one("time.s-user-card--time > span")["title"]
                qvotes = element.select(".s-post-summary--stats-item-number")[0].text
                qanswers = element.select(".s-post-summary--stats-item-number")[1].text.strip()
                qviews = element.select(".s-post-summary--stats-item-number")[2].text.strip()
                qaccepted = True if element.select(".s-post-summary--stats-item.has-accepted-answer") else False
                qdetailed = False  # All of these results are from the search index, so they are not detailed
                qdefinitive = True if re.search(r'wiki', element.select_one(".s-user-card--link").text.strip(),
                                                re.IGNORECASE) else False
                q = {
                    "QuestionId": qid,
                    "Title": qtitle,
                    "Link": qlink,
                    "Tags": qtags,
                    "Content": qcontent,
                    "Time": qtime,
                    "Votes": qvotes,
                    "Answers": qanswers,
                    "Views": qviews,
                    "Accepted": qaccepted,
                    "Detailed": qdetailed,
                    "Definitive": qdefinitive
                }
                results.append(q)
                # print(q)
            except NoQuestionIdException:
                print("No QuestionId could be extracted from the url.")

        # If there are no more pages to click, then break the (outer) pager loop
        print(f"Page {page + (page_start - 1)} of {pages + (page_start - 1)} scraped.")
        print(f"-- {len(results)} results so far --")
        if page >= pages:
            print("\nAll pages scraped. Exiting...")
            break
        else:
            # Click the next page button
            # Adding some random scrolling effects and clicking in order to avoid bot detection
            next_button = driver.find_element(By.XPATH, "//a[@rel='next']")
            action = webdriver.ActionChains(driver)
            action.scroll_to_element(next_button).perform()
            time.sleep(random.randint(1, 3))
            action_click = webdriver.ActionChains(driver)
            action_click.click(next_button).perform()
            time.sleep(random.randint(3, 10))

    df = pd.DataFrame(results, index=[q["QuestionId"] for q in results])
    # df = merge.with_existing_csv(df, filename)
    export.to_csv(df, filename)
    return df


def scrape_so_detailed_page(url: str, filename: str) -> pd.DataFrame:
    """Scrape Stack Overflow detailed pages by passing in an url

    :param url: The url to scrape. Default is "https://stackoverflow.com/questions/64475608/how-to-configure-nginx-ingress-controller-to-serve-static-files-from-a-pvc-in-kub".
    :param filename: The name and path where to save the file as. Default is "../datasources/kubernetes.csv".

    :returns: A Pandas DataFrame containing the scraped data.
    """
    url_to_parse = url

    results = []  # Store findings
    driver = webdriver.Chrome()
    driver.get(url_to_parse)

    # Pause on captcha
    while True:
        if "nocaptcha" in driver.current_url:
            print("Answer the captcha...")
            time.sleep(15)
        else:
            break

    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # 1) Grab post defailts
    #       post = .postcell > .s-prose
    # 2) Update answer count
    # 3) Update vote count
    # 4) Update view count
    #   convert 10k to 10000
    # 5) Update tags


    # Loop through each post summary
    for element in soup.findAll(attrs={'data-answerid': True}):
        try:
            acontent = element.find_next("div", {"class": "s-post-body"}).text.strip()
            aaccepted = True if element.select(".s-post-summary--stats-item.has-accepted-answer") else False
            a = {
                "AnswerId": element["data-answerid"],
                "Content": acontent,
                "Accepted": aaccepted
            }
            results.append(a)
            # print(a)
        except NoQuestionIdException:
            print("No QuestionId could be extracted from the url.")

    df = pd.DataFrame(results, index=[a["AnswerId"] for a in results])
    # df = merge.with_existing_csv(df, filename)
    export.to_csv(df, filename)
    return df
