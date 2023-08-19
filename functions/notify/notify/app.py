import json
import os
import boto3

def send_email(subject, body):
    SENDER = os.environ["SENDER_EMAIL"]
    RECIPIENT = os.environ["RECIPIENT_EMAIL"]
    REGION = "ap-northeast-1"
    CHARSET = "UTF-8"

    client = boto3.client('ses', region_name=REGION)
    client.send_email(
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

sns = boto3.client('sns')
def publish_topic(subject, body):
    TOPIC_ARN = os.environ["TOPIC_ARN"]

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=body
    )

def lambda_handler(event, context):
    for record in event['Records']:
        print(record)
        environment = json.loads(record["body"])
        humidity = int(environment["humidity"])
        temperature = int(environment["temperature"])

        subject = "[アラート] とねのケージの温度・湿度を確認してください！"
        body = f"""とねのケージの温度または湿度が不適切な状態です！
確認してください！

温度: {temperature} C
湿度: {humidity} %
"""

        publish_topic(subject, body)
        send_email(subject, body)