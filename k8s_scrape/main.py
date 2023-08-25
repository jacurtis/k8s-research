# import click

import stackoverflow
from export import export


# @click.Command()
def main():
    stackoverflow.scrape_so_index_page(
        tag="kubernetes",
        filename="../datasources/kubernetes-11.csv",
        pages=50,
        page_start=1,
        page_size=50
    )


def detail(detail_url):
    data = stackoverflow.scrape_so_detailed_page(detail_url)

    export.to_mysql_row(data)


if __name__ == '__main__':
    # main()  # You might want to run `poetry update` first, to get the latest chromedriver
    url = "https://stackoverflow.com/questions/57768656/use-ephemeral-volumes-in-k8s-cluster"
    # url = "https://stackoverflow.com/questions/76957468/is-there-a-way-to-stagger-workloads-starting-in-a-gke-cluster"
    detail(url)
