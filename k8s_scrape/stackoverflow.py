import random
import time
import re

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from k8s_scrape.export import export, merge


class WebDriverSingleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(WebDriverSingleton, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.chrome = webdriver.Chrome()


class NoQuestionIdException(Exception):
    """Exception raised when a QuestionId could not be extracted.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="No QuestionId could be extracted from the url."):
        self.url = url
        self.message = message
        super().__init__(self.message)


class ScrapeDetailPageException(Exception):
    """Exception raised when the detail page could not be scraped.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="The Question detail page could not be scraped."):
        self.url = url
        self.id = _get_question_id(url)
        self.message = message
        super().__init__(self.message)


class PostRemovedByAuthorException(Exception):
    """Exception raised when a page is scrape that has been since removed by its author.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="This post has been voluntarily removed by its author."):
        self.url = url
        self.id = _get_question_id(url)
        self.message = message
        super().__init__(self.message)


class PostRemovedByModerationException(Exception):
    """Exception raised when a page is scrape that has been since removed by its author.

    :argument url: url that was attempted to be parsed
    :argument message: explanation of the error
    """

    def __init__(self, url, message="This post has been removed by moderators."):
        self.url = url
        self.id = _get_question_id(url)
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


def _print_so_detail_results(q_title, q_tags, q_text, q_text_clean, q_html, q_votes, q_views, q_created_time,
                             q_updated_time, q_answers, q_accepted) -> None:
    print(f"Title: {q_title}")
    print(f"Tags: {q_tags}")
    print(f"Text:\n{q_text}")
    print(f"Text (Cleaned):\n{q_text}")
    print(f"HTML:\n{q_html}")
    print(f"Votes: {q_votes}")
    print(f"Views: {q_views}")
    print(f"Created At: {q_created_time}")
    print(f"Updated At: {q_updated_time}")
    print(f"Answers: {q_answers}")
    print(f"Accepted: {q_accepted}")
    return


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
                q_title = el_title.string
                q_link = _full_url(el_title['href'])
                qid = _get_question_id(q_link)
                q_tags = [li.text for li in element.select(".s-post-summary--meta-tags > ul > li")]
                q_content = element.find_next("div", {"class": "s-post-summary--content-excerpt"}).text.strip()
                q_time = element.select_one("time.s-user-card--time > span")["title"]
                q_votes = element.select(".s-post-summary--stats-item-number")[0].text
                q_answers = element.select(".s-post-summary--stats-item-number")[1].text.strip()
                q_views = element.select(".s-post-summary--stats-item-number")[2].text.strip()
                q_accepted = True if element.select(".s-post-summary--stats-item.has-accepted-answer") else False
                q_detailed = False  # All of these results are from the search index, so they are not detailed
                q_definitive = True if re.search(r'wiki', element.select_one(".s-user-card--link").text.strip(),
                                                 re.IGNORECASE) else False
                q = {
                    "QuestionId": qid,
                    "Title": q_title,
                    "Link": q_link,
                    "Tags": q_tags,
                    "Content": q_content,
                    "Time": q_time,
                    "Votes": q_votes,
                    "Answers": q_answers,
                    "Views": q_views,
                    "Accepted": q_accepted,
                    "Detailed": q_detailed,
                    "Definitive": q_definitive
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


def scrape_so_detailed_page(url: str, debug: bool = False, simulate: bool = False) -> dict:
    """Scrape Stack Overflow detailed pages by passing in an url

    :param url: The url to scrape.
    :param debug: Whether to output debug information. Default is False.

    :returns: A Pandas DataFrame containing the scraped data.
    """
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option("detach", True)
    driver = WebDriverSingleton().chrome
    driver.get(url)

    # Pause on captcha
    while True:
        if "nocaptcha" in driver.current_url:
            print("Answer the captcha...")
            time.sleep(15)
        else:
            break

    # Setup BeautifulSoup
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    # Get the html elements for parsing
    element = soup.find(class_="inner-content")
    if not element:
        time.sleep(5)
        element = soup.select_one('span.revision-comment')
        if element and element.text == "voluntarily removed by its author":
            raise PostRemovedByAuthorException(url)
        elif element and element.text == "removed from Stack Overflow for reasons of moderation":
            raise PostRemovedByModerationException(url)
        raise ScrapeDetailPageException(url)
    question = element.select_one("#question>.post-layout")
    # answers = element.select("#answers>.answer")

    # Parse the html elements for data
    q_title = element.select_one("#question-header h1 a").string
    q_tags = [li.text for li in element.select(".post-taglist ul.js-post-tag-list-wrapper li")]
    q_content_raw = question.select_one(".js-post-body")
    q_content_html = str(q_content_raw)  # Core post content in HTML
    q_content_text = q_content_raw.text.strip()  # Core post content in text form
    for pre in q_content_raw.find_all('pre'):
        pre.decompose()
    q_content_clean = q_content_raw.text.strip()  # Core post text content in text form with code removed
    q_votes = question.select_one(".js-vote-count").text.strip()
    el_q_meta = element.select(".d-flex.fw-wrap.pb8.mb16.bb.bc-black-075 .flex--item")
    q_created_time = el_q_meta[0].select_one("time")["datetime"]
    q_updated_time = el_q_meta[1].select_one("a")["title"]
    views_string = el_q_meta[2].attrs['title']
    views_match = re.search(r'([\d,]+)\stimes$', views_string)
    q_views = int(views_match.group(1).replace(',', '')) if views_match else 0
    q_answers = element.select_one("#answers-header h2").attrs['data-answercount']
    q_accepted = True if len([el for el in element.select(".js-accepted-answer-indicator") if
                              "d-none" not in el.attrs[
                                  'class']]) > 0 else False  # Looks through all instances of the answer indicator and checks if any of them are not hidden

    # Print debug information if debug is True
    if debug:
        _print_so_detail_results(q_title, q_tags, q_content_text, q_content_clean, q_content_html, q_votes, q_views,
                                 q_created_time,
                                 q_updated_time, q_answers, q_accepted)
    if simulate:
        time.sleep(random.randint(1, 5))

    # Return the results of the scrape
    return {
        "id": _get_question_id(url),
        "title": q_title,
        "url": url,
        "tag_array": q_tags,
        "content": q_content_text,
        "content_clean": q_content_clean,
        "content_html": q_content_html,
        "votes": q_votes,
        "views": q_views,
        "created_at": q_created_time,
        "updated_at": q_updated_time,
        "answers": q_answers,
        "accepted": q_accepted,
        "detailed": True,  # Always True after we have scraped a detailed page (as opposed to the search index)
    }
