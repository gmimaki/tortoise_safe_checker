# 参考 https://advancedweb.hu/how-to-manage-iot-core-resources-with-terraform/
resource "random_id" "id" {
    byte_length = 8
}

resource "aws_iot_thing" "thing" {
    name = "thing_${random_id.id.hex}"
}

resource "tls_private_key" "key" {
    algorithm = "RSA"
    rsa_bits = 2048
}

resource "tls_self_signed_cert" "cert" {
    private_key_pem = tls_private_key.key.private_key_pem

    validity_period_hours = 240

    allowed_uses = []

    subject {
        organization = "test"
    }
}

resource "aws_iot_certificate" "cert" {
    certificate_pem = trimspace(tls_self_signed_cert.cert.cert_pem)
    active = true
}

resource "aws_iot_thing_principal_attachment" "attachment" {
    principal = aws_iot_certificate.cert.arn
    thing = aws_iot_thing.thing.name
}

data "aws_arn" "thing" {
    arn = aws_iot_thing.thing.arn
}

resource "aws_iot_policy" "policy" {
    name = "thingpolicy_${random_id.id.hex}"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "iot:Connect",
                ]
                Effect = "Allow"
                #Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:client/$${iot:Connection.Thing.ThingName}"
                Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:client/*"
            },
            {
                Action = [
                    "iot:Publish",
                    "iot:Receive",
                ]
                Effect = "Allow"
                #Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:topic/$aws/things/$${iot:Connection.Thing.ThingName}/*"
                Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:topic/*"
            },
            {
                Action = [
                    "iot:Subscribe",
                ]
                Effect = "Allow"
                #Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:topicfilter/$aws/things/$${iot:Connection.Thing.ThingName}/*"
                Resource = "arn:aws:iot:${data.aws_arn.thing.region}:${data.aws_arn.thing.account}:topicfilter/*"
            }
        ]
    })
}

resource "aws_iot_policy_attachment" "attachment" {
    policy = aws_iot_policy.policy.name
    target = aws_iot_certificate.cert.arn
}

data "aws_iot_endpoint" "iot_endpoint" {
    endpoint_type = "iot:Data-ATS"
}

data "http" "root_ca" {
    url = "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
}

variable "kinesis_stream_arn" {
    type = string
}
variable "kinesis_stream_name" {
    type = string
}

resource "aws_iot_topic_rule" "rule" {
    name = "rule"
    description = "A rule to send message to a Firehose stream"
    sql = "SELECT * FROM topic_temperature"
    sql_version = "2016-03-23"
    enabled = true

    firehose {
        delivery_stream_name = var.kinesis_stream_name
        role_arn = aws_iam_role.topic_role.arn
    }

    # TODO error_actionがあったほうがよい
}

resource "aws_iam_role" "topic_role" {
    name = "iotcore_topic_role"
    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "iot.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

resource "aws_iam_role_policy" "topic_policy" {
    name = "iotcore_topic_policy"
    role = aws_iam_role.topic_role.id

    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "firehose:PutRecord",
                "firehose:PutRecordBatch"
            ],
            "Resource": "${var.kinesis_stream_arn}"
        }
    ]
}
EOF
}