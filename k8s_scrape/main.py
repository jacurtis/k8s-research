import click

import stackoverflow
from export import export


@click.group()
def scrape():
    pass


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
    """Scrape a Stackoverflow Question Detail page."""
    data = stackoverflow.scrape_so_detailed_page(url)

    export.to_db_row(data, db_driver=database)


@scrape.command(name="update")
def scrape_update():
    """Looks through the existing records to update existing records with new data."""
    pass


if __name__ == '__main__':
    # main()  # You might want to run `poetry update` first, to get the latest chromedriver
    # url = "https://stackoverflow.com/questions/57769487/wordpress-error-establishing-a-database-connection-using-kubernetes"
    # url = "https://stackoverflow.com/questions/76957468/is-there-a-way-to-stagger-workloads-starting-in-a-gke-cluster"
    scrape()
