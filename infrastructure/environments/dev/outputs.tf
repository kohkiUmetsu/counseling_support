output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.ecs.alb_dns_name
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.db_instance_endpoint
}

output "aurora_endpoint" {
  description = "Aurora cluster endpoint"
  value       = module.rds.aurora_cluster_endpoint
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.s3_bucket_name
}

output "migration_task_definition_arn" {
  description = "ARN of the migration task definition"
  value       = module.ecs.migration_task_definition_arn
}

# Direct database connection info (bastion host removed)
output "direct_db_connection" {
  description = "Direct database connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${module.rds.db_instance_endpoint}/counseling_db"
  sensitive   = true
}