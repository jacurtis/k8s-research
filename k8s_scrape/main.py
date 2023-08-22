# import click

import stackoverflow


# @click.Command()
def main():
    stackoverflow.scrape_so_index_page(
        tag="kubernetes",
        filename="../datasources/kubernetes-11.csv",
        pages=50,
        page_start=1,
        page_size=50
    )


if __name__ == '__main__':
    main()  # You might want to run `poetry update` first, to get the latest chromedriver
