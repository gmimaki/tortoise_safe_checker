terraform {
  backend "s3" {
    # S3バケットとDynamoDBテーブルは手動で作っておく必要あり
    bucket         = "tfstate-mimaki"
    key            = "turtoise_safe_checker/terraform.tfstate"
    region         = "ap-northeast-1"
    encrypt        = true
    dynamodb_table = "terraform_state_lock"
  }
}