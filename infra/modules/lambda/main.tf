resource "aws_lambda_function" "notify_environment" {
  function_name = "notify-environment"
  role = aws_iam_role.notify_environment.arn
  package_type = "Image"
  # TODO パイプラインの中でいい感じにしたい
  image_uri = "${var.ecr_image_uri}:latest"
  timeout = 60

  environment {
    variables = {
      SENDER_EMAIL = var.sender_email
      RECIPIENT_EMAIL = var.receipient_email
      TOPIC_ARN = var.sns_topic_arn
    }
  }

  lifecycle {
    ignore_changes = [image_uri]
  }
}

resource "aws_iam_role" "notify_environment" {
  name = "lambda_notify_environment"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "notify_environment" {
  role = aws_iam_role.notify_environment.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:ListStreams"
      ],
      "Resource": "${var.dynamodb_stream_arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "${var.sns_topic_arn}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability"
      ],
      "Resource": "${var.ecr_image_arn}"
    }
  ]
}
EOF
}

# TODO cloudwatch logsの作成も必要?

resource "aws_lambda_event_source_mapping" "tortoise_environment" {
  event_source_arn = var.dynamodb_stream_arn
  function_name = aws_lambda_function.notify_environment.function_name
  starting_position = "TRIM_HORIZON"
}