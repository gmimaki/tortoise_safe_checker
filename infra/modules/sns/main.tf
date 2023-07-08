resource "aws_sns_topic" "tortoise_safe_checker" {
  name = "tortoise_safe_checker"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "tortoise_safe_checker" {
  topic_arn = aws_sns_topic.tortoise_safe_checker.arn
  protocol = "sms"
  endpoint = var.phone_number
}