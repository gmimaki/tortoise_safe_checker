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