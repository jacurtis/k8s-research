import pandas as pd


def to_csv(data, filename):
    df = pd.DataFrame({'Titles': data})
    df.to_csv(f"~/Desktop/{filename}", index=False, encoding='utf-8')
