resource "aws_s3_bucket" "audio_files" {
  bucket = "${var.project_name}-${var.environment}-audio-files"

  tags = {
    Name        = "${var.project_name}-${var.environment}-audio-files"
    Environment = var.environment
    Purpose     = "Audio file storage"
  }
}

resource "aws_s3_bucket_versioning" "audio_files" {
  bucket = aws_s3_bucket.audio_files.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audio_files" {
  bucket = aws_s3_bucket.audio_files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audio_files" {
  bucket = aws_s3_bucket.audio_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "audio_files" {
  bucket = aws_s3_bucket.audio_files.id

  rule {
    id     = "audio_files_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = var.audio_file_retention_days
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# IAM role for ECS to access S3
resource "aws_iam_role" "s3_access_role" {
  name = "${var.project_name}-${var.environment}-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-access-role"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "s3_access_policy" {
  name        = "${var.project_name}-${var.environment}-s3-access-policy"
  description = "Policy for S3 audio files access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.audio_files.arn,
          "${aws_s3_bucket.audio_files.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-s3-access-policy"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.s3_access_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}