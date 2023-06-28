resource "aws_dynamodb_table" "tortoise_environment" {
  name = "TortoiseEnvironment"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "Time"
  stream_enabled = true
  stream_view_type = "NEW_IMAGE"

  attribute {
    name = "Time"
    Type = "N"
  }
}

resource "aws_lambda_event_source_mapping" "tortoise_environment" {
  event_source_arn = aws_dynamodb_table.tortoise_environment.stream.arn
  function_name = "TODO"
  starting_position = "TRIM_HORIZON"
}