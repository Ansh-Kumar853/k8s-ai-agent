variable "aws_region" {
  description = "AWS region for the cluster."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Short project identifier used for resource names."
  type        = string
  default     = "kubesage"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version supported by the selected AWS region."
  type        = string
  default     = "1.31"
}

variable "vpc_cidr" {
  description = "CIDR range for the cluster VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs; use one subnet per availability zone."
  type        = list(string)
  default     = ["10.40.1.0/24", "10.40.2.0/24", "10.40.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs for load balancers and NAT gateways."
  type        = list(string)
  default     = ["10.40.101.0/24", "10.40.102.0/24", "10.40.103.0/24"]
}

variable "node_instance_types" {
  description = "EC2 instance types for the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_size" {
  description = "Desired worker node count."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum worker node count."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum worker node count."
  type        = number
  default     = 4
}
