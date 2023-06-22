output "stream_arn" {
    value = aws_kinesis_firehose_delivery_stream.stream.arn
}

output "stream_name" {
    value = aws_kinesis_firehose_delivery_stream.stream.name
}