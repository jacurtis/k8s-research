# import click

import stackoverflow


# @click.Command()
def main():
    stackoverflow.scrape_so_index_page(
        tag="kubernetes",
        filename="../datasources/kubernetes-10.csv",
        pages=100,
        page_start=700,
        page_size=50
    )


if __name__ == '__main__':
    main()
