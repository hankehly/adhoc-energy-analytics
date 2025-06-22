import numpy as np
import pandas as pd


def trim_by_index(df: pd.DataFrame, trim_col: str, lower_pct=0.1, upper_pct=0.1):
    """
    Remove the lowest and highest fractions of rows from a pandas DataFrame
    based on sorting by a value column.
    df         : a pandas DataFrame
    trim_col   : column name to sort and trim by
    lower_pct  : fraction to trim from the bottom (default 0.1)
    upper_pct  : fraction to trim from the top    (default 0.1)
    """
    vals = df.dropna(subset=[trim_col]).sort_values(by=trim_col)
    n = len(vals)
    lo = int(n * lower_pct)
    hi = int(n * (1 - upper_pct))
    return vals.iloc[lo:hi]


def freedman_diaconis_bins(data):
    iqr = np.percentile(data, 75) - np.percentile(data, 25)
    bin_width = 2 * iqr / len(data) ** (1 / 3)
    bins = int((np.max(data) - np.min(data)) / bin_width)
    return bins
