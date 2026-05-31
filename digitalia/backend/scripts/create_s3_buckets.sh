#!/usr/bin/env bash
set -e
echo "Starting LocalStack S3 initialization..."
awslocal s3 mb s3://digitalia-portfolios
echo "List of current S3 buckets in LocalStack:"
awslocal s3 ls
echo "S3 initialization completed successfully!"
