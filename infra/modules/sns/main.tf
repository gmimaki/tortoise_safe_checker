resource "aws_sns_topic" "tortoise_safe_checker" {
  name = "tortoise_safe_checker"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "tortoise_safe_checker_sms" {
  topic_arn = aws_sns_topic.tortoise_safe_checker.arn
  protocol = "sms"
  endpoint = var.phone_number
}

resource "aws_sns_topic_subscription" "tortoise_safe_checker_sqs" {
  topic_arn = aws_sns_topic.tortoise_safe_checker.arn
  protocol = "sqs"
  endpoint = var.sqs_queue_arn
}

resource "aws_sns_sms_preferences" "tortoise_safe_checker" {
  delivery_status_iam_role_arn = aws_iam_role.SNS_SMS_tortoise_safe_checker.arn
}

resource "aws_iam_role" "SNS_SMS_tortoise_safe_checker" {
  name = "SNS_SMS_tortoise_safe_checker"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "SNS_SMS_tortoise_safe_checker" {
  name = "SNS_SMS_tortoise_safe_checker"
  role = aws_iam_role.SNS_SMS_tortoise_safe_checker.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}