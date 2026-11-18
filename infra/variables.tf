variable "aws_region" {
  description = "AWS region"
  default     = "eu-west-3"
}

variable "dockerhub_user" {
  description = "DockerHub username"
  default     = "ellkinox"
}

variable "backend_count" {
  description = "Number of backend containers"
  default     = 2
}
