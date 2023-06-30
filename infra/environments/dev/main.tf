#module "kinesis" {
#  source = "../../modules/kinesis"
#}

#module "glue" {
#  source = "../../modules/glue"
#}

module "ecr" {
  source = "../../modules/ecr"
}

module "dynamodb" {
  source = "../../modules/dynamodb"
}

module "lambda" {
  source = "../../modules/lambda"
  sender_email = var.sender_email
  receipient_email = var.receipient_email
  ecr_image_uri = module.ecr.repository_url
  ecr_image_arn = module.ecr.repository_arn
  dynamodb_stream_arn = module.dynamodb.dynamodb_stream_arn
}

module "iot_core" {
  source              = "../../modules/iot_core"
  #kinesis_stream_arn  = module.kinesis.stream_arn
  #kinesis_stream_name = module.kinesis.stream_name
  dynamodb_table_arn = module.dynamodb.dynamodb_table_arn
  dynamodb_table_name = module.dynamodb.dynamodb_table_name
}