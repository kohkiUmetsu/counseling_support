variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the bastion will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs"
  type        = list(string)
}

variable "instance_type" {
  description = "EC2 instance type for bastion host"
  type        = string
  default     = "t3.micro"
}

variable "key_pair_name" {
  description = "Name of the EC2 Key Pair for SSH access"
  type        = string
}

variable "db_endpoint" {
  description = "RDS main database endpoint"
  type        = string
}

variable "vector_db_endpoint" {
  description = "Aurora vector database endpoint"
  type        = string
}

variable "db_username" {
  description = "Main database username"
  type        = string
}

variable "vector_db_username" {
  description = "Vector database username"
  type        = string
}