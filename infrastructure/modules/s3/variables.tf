variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "audio_file_retention_days" {
  description = "Number of days to retain audio files"
  type        = number
  default     = 2555  # ~7 years
}