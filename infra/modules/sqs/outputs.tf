output "sqs_queue_arn" {
    value = aws_sqs_queue.tortoise_safe_checker.arn
}