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

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID"
  type        = string
}

variable "bastion_security_group_id" {
  description = "Bastion host security group ID"
  type        = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "RDS max allocated storage"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "counseling_db"
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

variable "vector_db_name" {
  description = "Vector database name"
  type        = string
  default     = "counseling_vector_db"
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

variable "aurora_instance_class" {
  description = "Aurora instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "aurora_instance_count" {
  description = "Number of Aurora instances"
  type        = number
  default     = 1
}

variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}