output "thing_name" {
    value = aws_iot_thing.thing.name
}

output "cert" {
    value = tls_self_signed_cert.cert.cert_pem
}

output "key" {
    value = tls_private_key.key.private_key_pem
    sensitive = true
}

output "iot_endpoint" {
    value = data.aws_iot_endpoint.iot_endpoint.endpoint_address
}

output "ca" {
    value = data.http.root_ca.response_body
}