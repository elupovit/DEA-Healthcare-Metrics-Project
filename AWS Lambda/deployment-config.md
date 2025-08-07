# Lambda Deployment Configuration

## Runtime Configuration
- **Runtime**: Python 3.9+
- **Handler**: lambda_function.lambda_handler
- **Timeout**: 15 minutes
- **Memory**: 512MB

## Environment Variables
- Set up AWS Secrets Manager for Google API credentials
- Configure S3 bucket permissions
- Set appropriate IAM role

## Trigger
- CloudWatch Events: Daily at 2:00 AM EST
- Cron expression: `cron(0 7 * * ? *)`

## Dependencies
Install packages listed in requirements.txt before deployment.
