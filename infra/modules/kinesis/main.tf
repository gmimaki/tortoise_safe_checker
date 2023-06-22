resource "aws_kinesis_firehose_delivery_stream" "stream" {
  name = "iottopic"
  destination = "s3"

  # TODO extended_s3_configurationも試したい 圧縮とか、Lambdaはさんでparquetとか、パーティショニングとか
  s3_configuration {
    role_arn = aws_iam_role.firehose_role.arn
    bucket_arn = aws_s3_bucket.bucket.arn
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
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:AbortMultipartUpload",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:PutObject"
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