import pandas


def to_csv(data: pandas.DataFrame, filename: str) -> None:
    """Export Pandas DataFrame to a CSV file.

    :param data: The DataFrame to export (must be a Pandas DataFrame).
    :param filename: The name and path where to save the file as

    :returns: None
    """
    data.to_csv(filename, index=False, encoding='utf-8')