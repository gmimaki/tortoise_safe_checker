#module "kinesis" {
#  source = "../../modules/kinesis"
#}

#module "glue" {
#  source = "../../modules/glue"
#}

#module "ecr" {
#  source = "../../modules/ecr"
#}

#module "dynamodb" {
#  source = "../../modules/dynamodb"
#}

#module "sns" {
#  source        = "../../modules/sns"
#  phone_number  = var.phone_number
#}

module "sqs" {
  source     = "../../modules/sqs"
  account_id = var.account_id
  #sns_topic_arn = module.sns.topic_arn
}

#module "ses" {
#  source = "../../modules/ses"
#  email = var.sender_email
#}

module "lambda" {
  source = "../../modules/lambda"
  #sender_email = var.sender_email
  #receipient_email = var.receipient_email
  #sns_topic_arn       = module.sns.topic_arn
  #ecr_image_uri       = module.ecr.repository_url
  #ecr_image_arn       = module.ecr.repository_arn
  sqs_queue_arn = module.sqs.sqs_queue_arn
  #dynamodb_stream_arn = module.dynamodb.dynamodb_stream_arn
}

module "iot_core" {
  source = "../../modules/iot_core"
  sqs_queue_arn = module.sqs.sqs_queue_arn
  sqs_queue_url = module.sqs.sqs_queue_url
  #kinesis_stream_arn  = module.kinesis.stream_arn
  #kinesis_stream_name = module.kinesis.stream_name
  #dynamodb_table_arn  = module.dynamodb.dynamodb_table_arn
  #dynamodb_table_name = module.dynamodb.dynamodb_table_name
}