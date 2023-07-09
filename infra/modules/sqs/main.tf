resource "aws_sqs_queue" "tortoise_safe_checker" {
  name = "tortoise-safe-checker"
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tortoise_safe_checker_dlq.arn,
    maxReceiveCount = 4
  })
}

resource "aws_sqs_queue" "tortoise_safe_checker_dlq" {
  name = "tortoise-safe-checker-dlq"
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    sourceQueueArns = ["arn:aws:sqs:ap-northeast-1:${var.account_id}:tortoise-safe-checker"]
  })
}

resource "aws_sns_topic_subscription" "tortoise_safe_checker_sqs" {
  topic_arn = var.sns_topic_arn
  protocol = "sqs"
  endpoint = aws_sqs_queue.tortoise_safe_checker.arn
}

resource "aws_sqs_queue_policy" "tortoise_safe_checker" {
  queue_url = aws_sqs_queue.tortoise_safe_checker.id

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "MyQueuePolicy",
  "Statement": [
    {
      "Sid": "Allow-SNS-Messages",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "${aws_sqs_queue.tortoise_safe_checker.arn}",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "${var.sns_topic_arn}"
        }
      }
    }
  ]
}
POLICY
}