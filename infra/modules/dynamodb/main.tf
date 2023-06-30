resource "aws_dynamodb_table" "tortoise_environment" {
  name = "TortoiseEnvironment"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "Time"
  stream_enabled = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "Time"
    type = "N"
  }
}