variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "backend_image" {
  description = "Backend Docker image URI"
  type        = string
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
}

variable "vector_database_url" {
  description = "Vector database connection URL"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 bucket name for audio files"
  type        = string
}

variable "s3_access_role_arn" {
  description = "S3 access IAM role ARN"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "task_cpu" {
  description = "ECS task CPU"
  type        = string
  default     = "256"
}

variable "task_memory" {
  description = "ECS task memory"
  type        = string
  default     = "512"
}

variable "service_desired_count" {
  description = "Desired number of ECS service instances"
  type        = number
  default     = 1
}