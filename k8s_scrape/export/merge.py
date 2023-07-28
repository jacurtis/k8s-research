import pandas as pd


def with_existing_csv(dataframe: pd.DataFrame, filename: str) -> pd.DataFrame:
    # Import old data
    try:
        df_existing = pd.read_csv(filename, index_col='QuestionId')

        # Preference is given to the new data to override old data, hence the order is important in this merge
        # df_merged = pd.merge(dataframe, df_existing, how="outer")
        df_merged = pd.concat([df_existing, dataframe], axis=0, ignore_index=True, sort=False)
    except FileNotFoundError:
        print("No existing CSV file found. Creating new CSV file...")
        df_merged = dataframe

    df_merged.drop_duplicates(subset=["QuestionId"], inplace=True)
    return df_merged
