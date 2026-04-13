import argparse

import pandas as pd


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    return df


def prep_raw_data(raw_data: str, save_path: str):
    df = pd.read_csv(raw_data)
    df = preprocess_data(df)
    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_data", type=str, help="Raw data folder")
    parser.add_argument("--save_path", type=str, help="Prepared data folder")
    args = parser.parse_args()
