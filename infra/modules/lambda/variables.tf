variable "sender_email" {
    type = string
}
variable "receipient_email" {
    type = string
}
variable "sns_topic_arn" {
    type = string
}
variable "ecr_image_uri" {
    type = string
}
variable "ecr_image_arn" {
    type = string
}
variable "sqs_queue_arn" {
    type = string
}
#variable "dynamodb_stream_arn" {
#    type = string
#}