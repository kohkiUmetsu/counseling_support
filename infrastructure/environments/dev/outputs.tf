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