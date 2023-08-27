import json
#import os
import boto3
import requests

"""
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
"""

ssm_client = boto3.client('ssm')
parameter_store_name = '/line/access_token'
parameter_store_res = ssm_client.get_parameter(
    Name=parameter_store_name,
    WithDecryption=True
)
line_access_token = parameter_store_res['Parameter']['Value']
def send_line(body: str):
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {line_access_token}'
    }
    data = {
        "messages": [
            {
                "type": "text",
                "text": body
            }
        ]
    }

    res = requests.post(url, json=data, headers=headers)
    res.raise_for_status()


"""
sns = boto3.client('sns')
def publish_topic(subject: str, body: str):
    TOPIC_ARN = os.environ["TOPIC_ARN"]

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=body
    )
"""

def lambda_handler(event, context):
    for record in event['Records']:
        print(record["body"])
        environment = json.loads(record["body"])
        humidity = int(environment["humidity"])
        temperature = int(environment["temperature"])

        if not (25 <= temperature <= 35) or humidity <= 10:
            #subject = "[アラート] とねのケージの温度・湿度を確認してください！"
            body = f"""とねのケージの温度または湿度が不適切な状態です！
確認してください！

温度: {temperature} C
湿度: {humidity} %"""

            #publish_topic(subject, body)
            send_line(body)