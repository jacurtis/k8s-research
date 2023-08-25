import pandas

from k8s_scrape.export import sqlite_models as sqlite
from k8s_scrape.export import mysql_models as mysql


def to_csv(data: pandas.DataFrame, filename: str) -> None:
    """Export Pandas DataFrame to a CSV file.

    :param data: The DataFrame to export (must be a Pandas DataFrame).
    :param filename: The name and path where to save the file as

    :returns: None
    """
    data.to_csv(filename, index=False, encoding='utf-8')


def to_sqlite_row(data) -> any:
    Post = sqlite.StackoverflowPost

    sqlite.db.connect()
    row = Post.update(**data).where(Post.id == data['id']).execute()
    sqlite.db.close()
    return row


def to_mysql_row(data) -> None:
    Post = mysql.StackoverflowPost

    mysql.db.connect()
    row = Post.update(**data).where(Post.id == data['id']).execute()
    mysql.db.close()
    return row
