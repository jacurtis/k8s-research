from ast import literal_eval

import peewee
from k8s_scrape.models import mysql, sqlite


def get_recordset(key: str = "id", count: int = 10, page: int = 1, newest: bool = True,
                  fetch_all: bool = False, detailed=False, database: str = "mysql") -> list[any]:
    """Get a recordset (list) of Stackoverflow Posts from our Database. Collecting "key" values only
    Useful for scraping the detail pages. Passing in "url" as the key will return a list of urls,
    defaults to "id" which will return a list of ids.

    :param key: The column to return from the database (default: id).
    :param count: The number of records to fetch (default: 10).
    :param page: The page number to start from, useful for skipping records by the value of `count` (default: 1).
    :param newest: Whether to sort by newest or oldest records first (default: True).
    :param fetch_all: Whether to fetch all records or only those that have never had a detailed scrape (default: False).
    :param detailed: Whether to fetch only records that have been detailed scraped or not (default: False).
    :param database: The database driver to use (default: mysql).

    :returns: A recordset list of Stackoverflow Post values from the column requested as the "key" value.
    """
    Post = _models_and_connection_for_db(database)[0]

    if fetch_all:
        posts = (Post.select(getattr(Post, key))
                 .order_by((Post.created_at.desc() if newest else Post.created_at.asc()))
                 .paginate(page, count))
    else:
        posts = (Post.select(getattr(Post, key))
                 .where(Post.detailed == detailed)
                 .order_by((Post.created_at.desc() if newest else Post.created_at.asc()))
                 .paginate(page, count))

    return [getattr(post, key) for post in posts]


def delete_record_by_id(id, database="mysql") -> bool:
    """Delete a record from the database by the given URL.

    :param id: The ID of the record to delete.
    :param database: The database driver to use (default: mysql).

    :returns: True if the record was deleted, False if not.
    """
    Post, PostTag, _, _ = _models_and_connection_for_db(database)

    PostTag.delete().where(PostTag.post_id == id).execute()

    return True if Post.delete().where(Post.id == id).execute() == 1 else False


def create_tag_relations_from_post(id, db_driver="mysql") -> None:
    """Create tag relations for a given post. Mostly used to backfill the database with tag relations, when loaded from
    a csv file

    :param id: The ID of the post to create tag relations for.
    :param db_driver: The database driver to use (default: mysql).
    """
    Post, PostTag, Tag, _ = _models_and_connection_for_db(db_driver)

    post = Post.get_by_id(id)
    print(f"Post: {post.id}  " + "=" * 50)

    for tag_name in literal_eval(post.tag_array):
        tag, _ = Tag.get_or_create(name=tag_name)
        _, created = PostTag.get_or_create(post_id=post.id, tag_id=tag.id)
        if created:
            print(f"-- Added Tag: {tag.name} to Post: {post.id}")
        else:
            print(f"-- Tag: {tag.name} already exists on Post: {post.id}")


def _models_and_connection_for_db(db_driver) -> tuple[peewee.Model, peewee.Model, peewee.Model, peewee.Database]:
    """Returns the appropriate models and database connection for the given database driver.

    :param db_driver: The database driver to use (default: mysql).

    :returns: A tuple of the PostModel, PostTagModel, TagModel, and DbConnection.
    """
    if db_driver == "sqlite":
        PostModel = sqlite.StackoverflowPost
        TagModel = sqlite.StackoverflowTag
        PostTagModel = sqlite.StackoverflowPostTag
        DbConnection = sqlite.db
    else:  # default to mysql
        PostModel = mysql.StackoverflowPost
        TagModel = mysql.StackoverflowTag
        PostTagModel = mysql.StackoverflowPostTag
        DbConnection = mysql.db
    return PostModel, PostTagModel, TagModel, DbConnection
