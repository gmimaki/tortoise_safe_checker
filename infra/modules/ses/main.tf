resource "aws_ses_email_identity" "name" {
  email = var.email
}