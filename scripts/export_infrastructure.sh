#!/bin/bash

# AWS Infrastructure Export Script
# This script exports AWS infrastructure to JSON format

set -e

# Create timestamp for unique directory
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
EXPORT_DIR="exports/aws-infrastructure-export-${TIMESTAMP}"

echo "Creating export directory: ${EXPORT_DIR}"
mkdir -p "${EXPORT_DIR}"

# Export EC2 instances
echo "Exporting EC2 instances..."
aws ec2 describe-instances > "${EXPORT_DIR}/ec2-instances.json"

# Export VPCs
echo "Exporting VPCs..."
aws ec2 describe-vpcs > "${EXPORT_DIR}/vpcs.json"

# Export Security Groups
echo "Exporting Security Groups..."
aws ec2 describe-security-groups > "${EXPORT_DIR}/security-groups.json"

# Export Subnets
echo "Exporting Subnets..."
aws ec2 describe-subnets > "${EXPORT_DIR}/subnets.json"

# Export Route Tables
echo "Exporting Route Tables..."
aws ec2 describe-route-tables > "${EXPORT_DIR}/route-tables.json"

# Export Internet Gateways
echo "Exporting Internet Gateways..."
aws ec2 describe-internet-gateways > "${EXPORT_DIR}/internet-gateways.json"

# Export NAT Gateways
echo "Exporting NAT Gateways..."
aws ec2 describe-nat-gateways > "${EXPORT_DIR}/nat-gateways.json"

# Export Load Balancers (ALB/NLB)
echo "Exporting Load Balancers..."
aws elbv2 describe-load-balancers > "${EXPORT_DIR}/load-balancers.json" 2>/dev/null || echo "No ELBv2 load balancers found"

# Export RDS instances
echo "Exporting RDS instances..."
aws rds describe-db-instances > "${EXPORT_DIR}/rds-instances.json" 2>/dev/null || echo "No RDS instances found"

# Export S3 buckets
echo "Exporting S3 buckets..."
aws s3api list-buckets > "${EXPORT_DIR}/s3-buckets.json"

# Export IAM roles
echo "Exporting IAM roles..."
aws iam list-roles > "${EXPORT_DIR}/iam-roles.json"

# Export Lambda functions
echo "Exporting Lambda functions..."
aws lambda list-functions > "${EXPORT_DIR}/lambda-functions.json" 2>/dev/null || echo "No Lambda functions found"

echo "Export completed successfully!"
echo "Export directory: ${EXPORT_DIR}"

