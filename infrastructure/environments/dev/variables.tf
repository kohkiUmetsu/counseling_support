variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "backend_image" {
  description = "Backend Docker image URI"
  type        = string
  default     = "counseling-support-backend:latest"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "vector_db_password" {
  description = "Vector database password"
  type        = string
  sensitive   = true
}