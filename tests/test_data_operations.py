import pytest
import pandas as pd

from dr_sven.data_ops import exclude_dates, generate_dates, \
     pad_missing_dates, add_day_of_week


@pytest.fixture(scope='module')
def basic_data_indexed():
    df = pd.DataFrame(
        data=[
            ['2020-01-01', '10'],
            ['2020-01-02', '1000'],
            ['2020-01-03', '20'],
            ['2020-01-04', '2000'],
            ['2020-01-05', '100'],
            ['2020-01-06', '10'],
        ],
        columns=['date', 'count'],
    )

    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df


@pytest.fixture(scope='module')
def basic_data_not_indexed():
    df = pd.DataFrame(
        data=[
            ['2020-01-01', '10'],
            ['2020-01-02', '1000'],
            ['2020-01-03', '20'],
            ['2020-01-04', '2000'],
            ['2020-01-05', '100'],
            ['2020-01-06', '10'],
        ],
        columns=['date', 'count'],
    )

    return df


def test_exclude_dates_removes_list_of_dates(basic_data_indexed):
    exclude = ['2020-01-01', '2020-01-03', '2020-01-06']

    filtered_df = exclude_dates(basic_data_indexed, exclude=exclude)

    index_check = filtered_df.index.isin(exclude).tolist()

    print('exclude= ', end='')
    print(exclude)

    print('filtered_df=')
    print(filtered_df)
    print('index_check=')
    print(index_check)

    assert not (True in index_check)


def test_exclude_dates_leaves_non_filtered_dates(basic_data_indexed):
    exclude = ['2020-01-01', '2020-01-03', '2020-01-06']
    should_include = ['2020-01-02', '2020-01-04', '2020-01-05']

    filtered_df = exclude_dates(basic_data_indexed, exclude=exclude)

    index_check = filtered_df.index.isin(should_include).tolist()

    print('exclude= ', end='')
    print(exclude)
    print('should_include= ', end='')
    print(should_include)
    print('filtered_df=')
    print(filtered_df)
    print('index_check=')
    print(index_check)

    assert not (False in index_check)


def test_generate_dates_creates_expected_dates():
    start_date = '2020-01-02'
    end_date = '2020-01-04'
    should_include = ['2020-01-02', '2020-01-03', '2020-01-04']

    dates_df = generate_dates(start=start_date, end=end_date)

    index_check = dates_df.isin(should_include).tolist()

    print('should_include= ', end='')
    print(should_include)
    print('dates_df=')
    print(dates_df)
    print('index_check=')
    print(index_check)

    assert not (False in index_check)


def test_generate_dates_should_not_include_end_plus_1_day():
    start_date = '2020-01-02'
    end_date = '2020-01-04'
    should_not_include = ['2020-01-05']

    dates_df = generate_dates(start=start_date, end=end_date)

    index_check = dates_df.isin(should_not_include).tolist()

    print('should_include= ', end='')
    print(should_not_include)
    print('dates_df=')
    print(dates_df)
    print('index_check=')
    print(index_check)

    assert not (True in index_check)


def test_pad_missing_dates_returns_all_dates(basic_data_not_indexed):
    start = '2019-01-01'
    end = '2020-08-20'

    dates_df = pad_missing_dates(start, end, raw=basic_data_not_indexed)

    print('start = ' + start)
    print('end = ' + end)
    print('dates_df=')
    print(dates_df)
    
    assert '2020-08-20' in dates_df.index


def test_add_day_of_week_adds_correct_day(basic_data_indexed):
    days_df = add_day_of_week(raw=basic_data_indexed)

    print('days_df=')
    print(days_df)

    assert days_df.loc['2020-01-01']['day_of_week'] == 'Wednesday'
