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

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "counseling_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "vector_db_username" {
  description = "Vector database username"
  type        = string
  default     = "vector_user"
}

variable "vector_db_password" {
  description = "Vector database password"
  type        = string
  sensitive   = true
}

variable "key_pair_name" {
  description = "Name of the EC2 Key Pair for SSH access to bastion host"
  type        = string
  default     = "counseling-support-dev-key"
}