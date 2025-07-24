# Migration task definition
resource "aws_ecs_task_definition" "migration" {
  family                   = "${var.project_name}-${var.environment}-migration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = var.s3_access_role_arn

  container_definitions = jsonencode([
    {
      name      = "migration"
      image     = var.backend_image
      essential = true
      
      # Migrationコマンドを実行
      command = ["python", "migrate.py"]
      
      environment = [
        {
          name  = "DATABASE_URL"
          value = var.database_url
        },
        {
          name  = "VECTOR_DATABASE_URL"
          value = var.vector_database_url
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_name
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.backend.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "migration"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-migration-task"
    Environment = var.environment
    Purpose     = "Database Migration"
  }
}

