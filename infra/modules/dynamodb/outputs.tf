output dynamodb_table_arn {
    value = aws_dynamodb_table.tortoise_environment.arn
}
output dynamodb_stream_arn {
    value = aws_dynamodb_table.tortoise_environment.stream_arn
}