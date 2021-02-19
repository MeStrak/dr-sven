# Hello from Dr. Sven!
Dr Sven is a **data health checker** which performs a checkup on your data to  give you a simple indication of whether it's in good shape or not.

> **Get out clause**
>
> I have no idea if this will actually be useful for anyone else, I just thought I'd release it and find out. Also please consider this an alpha version only.

## Motivation
Dr. Sven is designed with a data lake type situation in mind where data is transferred from one data source to another repositoriy. Most data ingestion monitoring tools I've seen focus on whether individual processes have run without error at the expected time. In some complex scenarios they also try  to check that elements of the source data match the finally processed data which can be very difficult to do.

Imagine this situation ... all dashboards are green, logs contain no errors and all appears well with the world. Then a pesky human looks at the data and says *"but there are no records from Sunday, that's not right"* or *"there's something weird - it looks like there's a hole in this data from 1 month ago"*.

Dr. Sven aims to reduce dependence on that human by providing a naive yet effective way to detect data issues. Specify some data rules defining what you expect to see, then let our kind doctor check if the processed data meets the criteria.

## Dr. Sven sounds amazing. Wait ... what is it, and what does it actually do?

Dr. Sven is a simple lambda function written in Python that does the following:
1. Queries a data source (currently limited to AWS Athena) with a query that you provide to return records grouped by date
2. Checks the returned dataset complies with data guidelines defined in your Dr. Sven config file
3. Outputs a .md summary of the checkup
4. Outputs a .csv with a list of all rules that failed so you can check in more detail
 
 ## Features
 - Define a rule for minimum records per day
 - Define different rules per day (e.g. different record count for weekends and weekdays)
 - Ignore specific dates
 - Query AWS Athena
 - Read configuration from S3
 - Output checkup reports (.csv and .md) to S3

## What Dr. Sven is not
 Data health is complex, just like human health. I have deliberately avoided saying that Dr. Sven checks or guarantees data consistency, integrity or that it is a data quality checker. Dr. Sven is a KISS doctor. Not the hyopcratic oath breaking kind of kiss, but the one that reminds us that sometimes simple is a good thing.

 # Using Dr. Sven
 ## Installation
 Installation is currently a bit too manual, I'll work on automating that. Even though it's manual the process is still pretty simple.
 1. Zip application files

    cd to project folder then `zip function.zip *.py`

 2. Create a lambda function using that zip file
 
    Create a lambda dunction in the AWS console and upload the zip. The lambda must have an execution role with Athena and S3 access.

 3. Attach layers for Dr. Sven and AWS-Wrangler dependencies

    This part is messy for now, I'll make it better. For now create lambda layers using the S3 URLs below. Use Python 3.8 runtime.
    - https://dr-sven.s3-eu-west-1.amazonaws.com/awswrangler-layer-1.8.1-py3.8.zip
    - https://dr-sven.s3-eu-west-1.amazonaws.com/dr-sven_lambda-layer.zip

 4. Create rule configuration files and upload them to an S3 bucket

    See configuration section.


 ## Configuration
 Configuration files are in TOML format. Refer to sample.toml to see this file. Create a separte configuration  file for each data table you want to check.

### [general]
This table contains config settings that are general to the whole checkup.
- **title**: your title for the checkup, will appear in the checkup summary
- **output_location**: AWS S3 bucket name
- **output_region**: AWS S3 bucket region

### `[datasource]`
The datasource table is used to specify query parameters, datasource name and date range to be used for the full checkup.
- **query** = The query to get the data grouped by day, with the date field named **date**, column containing count of records for each day named **count** For example `"SELECT date_field as date, count(*) as count FROM my_table where {start_date} <= date >= {end_date group_by date_field} group by date"`. Date must be returned in the format **YYYY-mm-dd**
- **database** = database you want to check
- **start_date** = start of date range to check
- **end_date** = end of date range to check

### `[rules]`
All data guideline rules are defined in this section. Currently only the min_records rule is defined.
### `[[rules.min_records]]`
 The **min_records** rule checkes that each day of data contains at least the specified number of records. Specify min_records rules in this table. Repeat the table heading and contents for each rule (e.g. if you want a different data rule for weekends and weekdays).

- **name** = "Weekends must have a few records"
- **ignore_dates** = Array of specific dates to ignore in format `yyyy-mm-dd`
- **ignore_days** = Array of day names as strings to ignore. Accepts full day names, and friendly naming for Weekends, and Weekdays - e.g. `["Tuesday", "Weekends", "Weekdays"]` (although don't define exactly that ignore list as everything will be ignored!)
- **min_records** = the minimum number of records (int) that each day should have
- **explanation** = A friendly explanation for why the rule exists, will appear in checkup report

 ### Available rules
 Currently only the 'minimum records' rule type has been implemented.

 ## Running Dr. Sven
 Launch Dr. Sven with a cloudwatch event with the following input format.
 {
  "s3": {
    "bucket": {
      "name": "your-bucket-name"
    },
    "object": {
      "key": "your-config-file.toml"
    }
  }
}

 ## Development
 Dr. Sven uses Poetry for dependency management. Install Poetry according to the documentation: https://python-poetry.org/docs/.

 Once installed cd to the project folder and run
 `poetry shell` to start the shell.

 Then `poetry install` to install dependencies.


