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


def detail(url):
    stackoverflow.scrape_so_detailed_page(url)


if __name__ == '__main__':
    # main()  # You might want to run `poetry update` first, to get the latest chromedriver
    url = "https://stackoverflow.com/questions/76951362/pod-to-pod-communication-across-namespace-in-the-same-cluster"
    # url = "https://stackoverflow.com/questions/76957468/is-there-a-way-to-stagger-workloads-starting-in-a-gke-cluster"
    detail(url)
