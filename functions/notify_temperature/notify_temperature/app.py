import json
import os
import boto3
from botocore.exceptions import ClientError

def send_email(subject, body):
    SENDER = os.environ["SENDER_EMAIL"]
    RECIPIENT = os.environ["RECIPIENT_EMAIL"]
    REGION = "ap-northeast-1"
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=REGION)
    try:
        response = client.send_email(
            Destination={
                'ToAddress': [RECIPIENT]
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': subject
                    }
                }
            },
            Source=SENDER
        )
    except ClientError as e:
        print(e.response(['Error']['Message'])) # TODO エラー通知
    else:
        print(response['MessageId'])

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            table = record['dynamodb']['NewImage']
            temperature = table['Temperature']['N']
            humidity = table['Humidity']['N']
            if not (25 <= 35) or 10 <= humidity:
                subject = "[ALERT] Temperature of Humid out of range"
                body = f"Temperature: {temperature}, Humidity: {humidity}"
                send_email(subject, body)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "result":True,
        }),
    }
