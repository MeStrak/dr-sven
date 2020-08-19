from checkup import start_checkup
import boto3
import json
from http import HTTPStatus


s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("Starting [d r - s v e n]")
    print("Received event: " + json.dumps(event, indent=2))
    bucket = event['s3']['bucket']['name']
    key = event['s3']['object']['key']

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        config = str(response['Body'].read().decode('utf-8'))
        print('************ read config to string from s3 ************')
        print(config)

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist \
               and your bucket is in the same region as this function.'
              .format(key, bucket))
        raise e

    start_checkup(config)

    return {
        'statusCode': HTTPStatus.OK.value,
        'body': json.dumps('[d r - s v e n] ... "thanks - call again!"')
    }
