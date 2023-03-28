import pandas as pd

def cleanDF(df):
    """
    Removes suprious columns from a DataFrame.

    Parameters
    ----------
    df: DataFrame

    Returns
    -------
    DataFrame
    """
    new_df = df.copy()
    names = ["Unnamed", "level_", "index"]
    for column in new_df.columns:
        for name in names:
            if name in column:
                del new_df[column]
    return new_df
