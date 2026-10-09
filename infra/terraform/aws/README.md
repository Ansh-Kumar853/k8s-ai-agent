# AWS EKS infrastructure

This Terraform configuration creates a VPC with public/private subnets, NAT egress, an EKS control plane, and a managed EC2 node group. This is a starter environment, not a production approval: inspect cost, security, region support, and policy requirements before applying.

## Prerequisites

- Terraform 1.6+
- AWS CLI configured for an account where you can create VPC, EKS, IAM, and EC2 resources
- An AWS region with at least three available Availability Zones and support for the configured Kubernetes version

## Plan before creating resources

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan -out=tfplan
```

Review the plan and estimated costs before running `terraform apply tfplan`. EKS control planes, worker nodes, NAT gateways, and data transfer can incur ongoing charges. Run `terraform destroy` only when you intentionally want to remove this environment.

## Production hardening required

- Change `cluster_endpoint_public_access_cidrs` in `main.tf` from the starter open range to trusted operator/VPN CIDRs, or disable public access.
- Use separate NAT gateways per AZ where availability requirements justify the extra cost.
- Add remote state with encryption, locking, and restricted access.
- Pin module/provider versions according to your change-management policy.
- Review node instance sizes, Kubernetes version availability, IAM, audit logging, encryption, and backup requirements.
