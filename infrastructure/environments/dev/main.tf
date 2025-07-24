terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "counseling-support-dev-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "counseling-support-dev-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  project_name = "counseling-support"
  environment  = "dev"
  
  availability_zones = ["${var.aws_region}a", "${var.aws_region}c"]
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
}

# VPC
module "vpc" {
  source = "../../modules/vpc"
  
  project_name           = local.project_name
  environment            = local.environment
  vpc_cidr              = "10.0.0.0/16"
  availability_zones    = local.availability_zones
  public_subnet_cidrs   = local.public_subnet_cidrs
  private_subnet_cidrs  = local.private_subnet_cidrs
  nat_gateway_count     = 1  # Dev環境では1つに削減
}

# S3
module "s3" {
  source = "../../modules/s3"
  
  project_name = local.project_name
  environment  = local.environment
}

# RDS
module "rds" {
  source = "../../modules/rds"
  
  project_name           = local.project_name
  environment            = local.environment
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  ecs_security_group_id = module.ecs.ecs_security_group_id
  
  db_username        = var.db_username
  db_password        = var.db_password
  vector_db_username = var.vector_db_username
  vector_db_password = var.vector_db_password
  
  # Development settings
  db_instance_class      = "db.t3.micro"
  aurora_instance_class  = "db.t3.medium"
  backup_retention_period = 1
}

# ECS
module "ecs" {
  source = "../../modules/ecs"
  
  project_name       = local.project_name
  environment        = local.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  
  backend_image        = var.backend_image
  database_url         = "postgresql://${var.db_username}:${var.db_password}@${module.rds.db_instance_endpoint}/counseling_db"
  vector_database_url  = "postgresql://${var.vector_db_username}:${var.vector_db_password}@${module.rds.aurora_cluster_endpoint}/counseling_vector_db"
  s3_bucket_name      = module.s3.s3_bucket_name
  s3_access_role_arn  = module.s3.s3_access_role_arn
  aws_region          = var.aws_region
  
  # Development settings
  task_cpu             = "256"
  task_memory          = "512"
  service_desired_count = 1
}