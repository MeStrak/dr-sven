from typing import List
import pandas as pd
import awswrangler as wr


def run_query(query, db) -> pd.DataFrame:
    df = wr.athena.read_sql_query(query, database=db)
    return df


def prepare_data(start: str, end: str, data: pd.DataFrame):
    data = pad_missing_dates(start, end, data)
    data = add_day_of_week(data)
    return data


def generate_dates(start, end) -> pd.DataFrame:
    """Returns a dataframe filled with date range.
    Date range is start to end inclusive."""

    dates = pd.date_range(start=start, end=end)
    return dates


def pad_missing_dates(start, end, raw: pd.DataFrame) -> pd.DataFrame:
    """Creates an index on a dataframe using the 'date' column,
    then pads the dataframe to create an index for all dates within
    expected range"""

    expected = generate_dates(start, end)
    raw.set_index('date', inplace=True)
    padded = raw.reindex(expected, fill_value=0)
    return padded


def exclude_dates(raw: pd.DataFrame, exclude: List[str]) -> pd.DataFrame:
    """Filters a dataframe (raw) to remove a list of dates (exclude).
    Returns the filtered dataframe."""

    filtered = raw[~raw.index.isin(exclude)]
    return filtered


def exclude_days(raw: pd.DataFrame, exclude: List[str]) -> pd.DataFrame:
    """Filters a dataframe (raw) to remove a list of dates (exclude).
    Returns the filtered dataframe."""

    print('************ Filtering out days ************')
    print(exclude)
    if 'Weekend' in exclude or 'Weekends' in exclude:
        exclude += ['Saturday', 'Sunday']

    if 'Weekday' in exclude or 'Weekdays' in exclude:
        exclude += ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    print(exclude)

    filtered = raw[~raw['day_of_week'].isin(exclude)]
    return filtered


def add_day_of_week(raw: pd.DataFrame) -> pd.DataFrame:
    raw['day_of_week'] = pd.to_datetime(raw.index)
    raw['day_of_week'] = raw['day_of_week'].dt.day_name()
    return raw
