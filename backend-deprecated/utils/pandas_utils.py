import pandas as pd

def _convert_date_columns(df, columns: list, suffix: str="_dt"):
    for col in columns:
        if col in df.columns:
            df[col + suffix] = pd.to_datetime(df[col], errors='coerce')
    return df

def _round_columns(df, columns, decimals=2):
    for col in columns:
        if col in df.columns:
            df[col] = df[col].round(decimals)
    return df