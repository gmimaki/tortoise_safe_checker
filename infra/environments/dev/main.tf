#module "kinesis" {
#  source = "../../modules/kinesis"
#}

#module "glue" {
#  source = "../../modules/glue"
#}

module "ecr" {
  source = "../../modules/ecr"
}

module "iot_core" {
  source              = "../../modules/iot_core"
  #kinesis_stream_arn  = module.kinesis.stream_arn
  #kinesis_stream_name = module.kinesis.stream_name
}