from typing import List, Dict
import toml
import pandas as pd
import boto3

# small trick (hack) so that imports work for both pytest and aws lambda
try:
    from .helpers import gen_checkup_id, get_filename, \
     RULE_SUMMARY, get_date_as_string
except ImportError:
    from helpers import gen_checkup_id, get_filename, \
     RULE_SUMMARY, get_date_as_string

try:
    from .data_ops import run_query, prepare_data, exclude_dates, exclude_days
except ImportError:
    from data_ops import run_query, prepare_data, exclude_dates, exclude_days


def start_checkup(config_string: str):
    checkup_id = gen_checkup_id()
    print('************ starting checkup #{} ************'

          .format(checkup_id))

    print('************ reading config ************')
    print(config_string)
    config = toml.loads(config_string)
    print('************ config read complete ************')
    print(config)

    query = config['datasource']['query']
    start = get_date_as_string(config['datasource']['start_date'])
    end = get_date_as_string(config['datasource']['end_date'])
    query = query.format(start_date=start, end_date=end)
    print(start)
    print(end)
    db = config['datasource']['database']

    print('running query: {}', query)
    data = run_query(query, db)
    print('query done, data size: {} rows'.format(len(data.index)))
    prepared_data = prepare_data(start, end, data)
    print('data prep done, data size {} rows'.format(len(data.index)))

    results, summary = run_rules(config, prepared_data)

    output_loc = config['general']['output_location']
    output_reg = config['general']['output_region']
    checkup_name = config['general']['title']

    output_results(results, summary, output_loc,
                   output_reg, checkup_id, checkup_name)


def output_results(results: pd.DataFrame, summary: List[str], location: str,
                   region: str, checkup_id: str, checkup_name: str):

    s3 = boto3.resource(
        's3',
        region_name=region)

    results_file = get_filename(checkup_id,
                                'dr-sven_results_' + checkup_name, '.csv')
    summary_file = get_filename(checkup_id,
                                'dr-sven_summary_' + checkup_name, '.md')

    concat_summary = ''.join(summary)
    results_csv = results.to_csv()

    s3.Object(location, results_file).put(Body=results_csv)
    s3.Object(location, summary_file).put(Body=concat_summary)


def run_rules(config: Dict, data: pd.DataFrame):
    final_summary: List[str] = []
    results: pd.DataFrame = pd.DataFrame()
    rules = config['rules']['min_records']
    for rule in rules:
        result, summary = check_rule(data, rule)
        print('************ Got result ************')
        final_summary.append(summary)
        results = pd.concat([results, result])

    print('************ All rules processed ************')
    print(results)

    return results, final_summary


def check_rule(raw: pd.DataFrame, rule: Dict) -> pd.DataFrame:
    """Filters a dataframe on count field where count is less than
    min records. Adds symptom and failed rule information to dataframe"""

    rule_name = rule['name']
    ignore_dates = rule['ignore_dates']
    ignore_days = rule['ignore_days']
    explain = rule['explanation']
    min_records = rule['min_records']

    rule_text = 'Expected at least {} records but found {}'
    rule_text = rule_text.format(min_records, '{}')
    filtered = exclude_dates(raw, ignore_dates)
    filtered = exclude_days(filtered, ignore_days)
    ignored_count = len(raw.index) - len(filtered.index)
    filtered = filtered[filtered['count'] < min_records]
    filtered['symptom'] = filtered['count'].map(rule_text.format)
    filtered['failed_rule'] = rule_name
    passed_count = len(raw.index) - len(filtered.index) - ignored_count
    failed_count = len(filtered.index)
    summary = RULE_SUMMARY.format(name=rule_name, description=explain,
                                  total=len(raw.index), ignored=ignored_count,
                                  passed=passed_count, failed=failed_count)
    print('************ Rule complete ************')

    return filtered, summary
