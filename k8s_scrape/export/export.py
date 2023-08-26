import pandas
import peewee

from ast import literal_eval

from k8s_scrape.models import mysql, sqlite


def to_csv(data: pandas.DataFrame, filename: str) -> None:
    """Export Pandas DataFrame to a CSV file.

    :param data: The DataFrame to export (must be a Pandas DataFrame).
    :param filename: The name and path where to save the file as

    :returns: None
    """
    data.to_csv(filename, index=False, encoding='utf-8')


def to_db_row(data, db_driver="mysql") -> any:
    """Create or update a row in the database.

    :param data: The data to insert or update.
    :param db_driver: The database driver to use (default: mysql).

    :returns: The row that was inserted or updated.
    """
    if db_driver == "sqlite":
        Post = sqlite.StackoverflowPost
        Tag = sqlite.StackoverflowTag
        PostTag = sqlite.StackoverflowPostTag
        db = sqlite.db
    else:  # default to mysql
        Post = mysql.StackoverflowPost
        Tag = mysql.StackoverflowTag
        PostTag = mysql.StackoverflowPostTag
        db = mysql.db

    post, created = Post.get_or_create(url=data["url"], defaults=data)
    if not created:
        Post.update(**data).where(Post.id == data['id']).execute()

    for t in literal_eval(post.tag_array):
        tag, _ = Tag.get_or_create(name=t)
        PostTag.get_or_create(post_id=post.id, tag_id=tag.id)

    return post
