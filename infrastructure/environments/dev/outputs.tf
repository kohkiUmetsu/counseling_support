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

# Bastion Host outputs
output "bastion_public_ip" {
  description = "Public IP address of the bastion host"
  value       = module.ec2.bastion_public_ip
}

output "bastion_ssh_command" {
  description = "SSH command to connect to bastion host"
  value       = module.ec2.ssh_command
}

output "bastion_db_connect_info" {
  description = "Database connection information via bastion"
  value = {
    main_db_command    = "ssh -i ~/.ssh/${var.key_pair_name}.pem ec2-user@${module.ec2.bastion_public_ip} -t './connect-db.sh'"
    direct_ssh_command = module.ec2.ssh_command
  }
}