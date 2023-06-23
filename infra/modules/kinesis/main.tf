resource "aws_kinesis_firehose_delivery_stream" "stream" {
  name = "iottopic"
  destination = "s3"

  # TODO extended_s3_configurationも試したい 圧縮とか、Lambdaはさんでparquetとか、パーティショニングとか
  s3_configuration {
    role_arn = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
    error_output_prefix = "error/"

    cloudwatch_logging_options {
      enabled = true
      log_group_name = aws_cloudwatch_log_group.firehose.name
      log_stream_name = aws_cloudwatch_log_stream.firehose.name
    }
  }
}

resource "aws_iam_role" "firehose_role" {
  name = "firehose_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "firehose_policy" {
  name = "firehose_policy"
  role = aws_iam_role.firehose_role.id
  #TODO Action絞るべき
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": ["${aws_s3_bucket.bucket.arn}", "${aws_s3_bucket.bucket.arn}/*"]
    }
  ]
}
EOF
}

resource "aws_s3_bucket" "bucket" {
  bucket = "iotcore-gmimaki"
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.bucket.arn}/*"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.firehose_role.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = aws_s3_bucket.bucket.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}

resource "aws_cloudwatch_log_group" "firehose" {
  name = "/aws/kinesisfirehose/iottopic"
}

resource "aws_cloudwatch_log_stream" "firehose" {
  name = "S3Delivery"
  log_group_name = aws_cloudwatch_log_group.firehose.name
}