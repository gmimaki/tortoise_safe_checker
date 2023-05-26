terraform {
    backend "s3" {
        bucket = "tfstate-mimaki"
        key = "turtoise_safe_checker/terraform.tfstate"
        region = "ap-northeast-1"
        encrypt = true
        dynamodb_table = "terraform_state_lock"
    }
}