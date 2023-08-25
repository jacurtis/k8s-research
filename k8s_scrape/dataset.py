import peewee
from k8s_scrape.models import mysql, sqlite


def get_recordset_urls(count=10, page=1, database="mysql", newest=True, fetch_all=False) -> list:
    """Get a recordset of Stackoverflow Posts from our Database. Collecting urls only
    Useful for scraping the detail pages.

    :param count: The number of records to return.
    :param page: The page number to start from.
    :param database: The database driver to use (default: mysql).
    :param newest: Whether to sort by newest or oldest records first.
    :param fetch_all: Whether to fetch all records or only those that have never had a detailed scrape.

    :returns: A recordset of Stackoverflow Post urls.
    """
    Post = sqlite.StackoverflowPost if database == "sqlite" else mysql.StackoverflowPost

    if fetch_all:
        posts = (Post.select(Post.url)
                 .order_by((Post.created_at.desc() if newest else Post.created_at.asc()))
                 .paginate(page, count))
    else:
        posts = (Post.select(Post.url)
                 .where(Post.detailed == False)
                 .order_by((Post.created_at.desc() if newest else Post.created_at.asc()))
                 .paginate(page, count))
    # db.close()
    return [post.url for post in posts]


def delete_record_by_url(url, database="mysql"):
    Post = sqlite.StackoverflowPost if database == "sqlite" else mysql.StackoverflowPost

    return Post.delete().where(Post.url == url).execute()

