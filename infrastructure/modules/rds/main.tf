resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-${var.environment}-rds-"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  # Allow access from bastion host
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.bastion_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
  }
}

# Main PostgreSQL database
resource "aws_db_instance" "main" {
  identifier             = "${var.project_name}-${var.environment}-db"
  engine                 = "postgres"
  engine_version         = "15.8"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  max_allocated_storage  = var.db_max_allocated_storage
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-db"
    Environment = var.environment
  }
}

# Aurora PostgreSQL cluster for vector operations
resource "aws_rds_cluster" "aurora_vector" {
  cluster_identifier      = "${var.project_name}-${var.environment}-aurora-vector"
  engine                 = "aurora-postgresql"
  engine_version         = "15.8"
  database_name          = var.vector_db_name
  master_username        = var.vector_db_username
  master_password        = var.vector_db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.backup_retention_period
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "prod"
  deletion_protection = var.environment == "prod"
  
  tags = {
    Name        = "${var.project_name}-${var.environment}-aurora-vector"
    Environment = var.environment
  }
}

resource "aws_rds_cluster_instance" "aurora_vector_instances" {
  count              = var.aurora_instance_count
  identifier         = "${var.project_name}-${var.environment}-aurora-vector-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora_vector.id
  instance_class     = var.aurora_instance_class
  engine             = aws_rds_cluster.aurora_vector.engine
  engine_version     = aws_rds_cluster.aurora_vector.engine_version

  tags = {
    Name        = "${var.project_name}-${var.environment}-aurora-vector-${count.index}"
    Environment = var.environment
  }
}