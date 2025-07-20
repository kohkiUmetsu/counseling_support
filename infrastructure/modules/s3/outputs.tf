output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.audio_files.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.audio_files.arn
}

output "s3_access_role_arn" {
  description = "ARN of the S3 access IAM role"
  value       = aws_iam_role.s3_access_role.arn
}