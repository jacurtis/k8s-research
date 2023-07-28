import stackoverflow
import headers


def main():
    stackoverflow.scrape_so_index_page(
        tag="kubernetes",
        filename="../datasources/kubernetes.csv",
        pages=50,
        page_start=150,
        page_size=50
    )


if __name__ == '__main__':
    main()
    # headers.scrape_getheaders()
