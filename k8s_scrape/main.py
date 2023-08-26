import click

import stackoverflow
import dataset
from export import export


@click.group()
def scrape():
    pass  # Empty method is used as a grouping command for the CLI


@scrape.command(name="index")
@click.option('--start', 'page_start', default=1, help="The page number to start scraping from.")
@click.option('--pages', default=1, help="The number of pages to scrape.")
@click.option('--per-page', 'page_size', default=50, help="The number of results per page.")
@click.option('--tag', default="kubernetes", help="The tag to search for on StackOverflow.")
def scrape_index(page_start, pages, page_size, tag):
    """Scrape a Stackoverflow Question Index page."""
    stackoverflow.scrape_so_index_page(
        tag=tag,
        filename="../datasources/kubernetes-11.csv",
        pages=pages,
        page_start=page_start,
        page_size=page_size
    )


@scrape.command(name="detail")
@click.option('--url', help="The URL of the Stackoverflow Question Detail page to scrape.")
@click.option('--database', default="mysql", help="The database driver to use when saving")
def scrape_detail(url, database):
    """Scrape a Stackoverflow Question Detail page. Saves the updated details to the database"""
    data = stackoverflow.scrape_so_detailed_page(url)

    export.to_db_row(data, db_driver=database)


@scrape.command(name="update")
@click.option('-c', '--count', default=10, help="The number of records to update.")
@click.option('--database', default="mysql", help="The database driver to use when saving")
@click.option('--newest/--oldest', default=True, help="Whether to update the newest or oldest records.")
@click.option('-p', '--page', default=1, help="The page number to start scraping from.")
@click.option('--new/--all', 'detailed_only', default=True, help="Whether to update all records or just new ones.")
def scrape_update(count=10, database="mysql", page=1, newest=True, detailed_only=True):
    """Looks through the existing records to update existing records with new data."""
    urls = dataset.get_recordset(key="url",
                                 count=count,
                                 database=database,
                                 newest=newest,
                                 page=page,
                                 fetch_all=not detailed_only)
    click.secho(f"Found {len(urls)} urls to update.", fg="blue")
    processed = 0
    for url in urls:
        processed += 1
        try:
            data = stackoverflow.scrape_so_detailed_page(url, simulate=True)
            export.to_db_row(data, db_driver=database)
            click.echo(f"{processed}/{count} | Updated: {data['id']} - {data['title']}")
        except (stackoverflow.PostRemovedByAuthorException, stackoverflow.PostRemovedByModerationException) as e:
            dataset.delete_record_by_url(e.url, database=database)
            click.secho(f"▼ ▼ ▼ {e.message} ▼ ▼ ▼", fg="white", bg="red")
            click.secho(f"{processed}/{count} | Deleted: {e.id} - {e.url}", fg="red")
        except stackoverflow.ScrapeDetailPageException as e:
            click.echo(f"{processed}/{count} | Skipped: {e.id} - {e.url}")


@scrape.command(name="tag-relations")
@click.option('-c', '--count', default=10, help="The number of posts to update.")
@click.option('--database', default="mysql", help="The database driver to use when saving")
@click.option('-p', '--page', default=1, help="The page number to start scraping from.")
@click.option('--detailed/--not-detailed', default=False, help="Whether to update all records or just new ones.")
def update_existing_tags(count=10, database="mysql", page=1, detailed=False) -> None:
    """Looks through existing posts to create tag relations. Useful for backfilling the database with tag relations."""
    posts = dataset.get_recordset(key="id", count=count, database=database, page=page, detailed=detailed)
    for post in posts:
        dataset.create_tag_relations_from_post(post, db_driver=database)


if __name__ == '__main__':
    scrape()
