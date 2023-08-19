resource "aws_sqs_queue" "tortoise_safe_checker" {
  name = "tortoise-safe-checker"
  visibility_timeout_seconds = 60
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.tortoise_safe_checker_dlq.arn
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

#resource "aws_sns_topic_subscription" "tortoise_safe_checker_sqs" {
#  topic_arn = var.sns_topic_arn
#  protocol = "sqs"
#  endpoint = aws_sqs_queue.tortoise_safe_checker.arn
#}

data "aws_iam_policy_document" "sqs_policy" {
  statement {
    actions = ["sqs:SendMessage"]
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = ["iot.amazonaws.com"]
    }
    resources = [aws_sqs_queue.tortoise_safe_checker.arn]
  }
}

resource "aws_sqs_queue_policy" "tortoise_safe_checker" {
  queue_url = aws_sqs_queue.tortoise_safe_checker.id
  policy = data.aws_iam_policy_document.sqs_policy.json
}