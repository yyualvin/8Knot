"""
AWS Lambda Deployment Example for 8Knot

This shows how to deploy Lambda functions and integrate them with API Gateway
to replace Celery + Redis + PostgreSQL cache with serverless architecture.

Architecture:
Frontend → API Gateway → Lambda Function → RDS Database → Return JSON
"""

import boto3
import json
from typing import Dict, Any

# Terraform/CloudFormation-style deployment configuration
LAMBDA_CONFIG = {
    "function_name": "eightknot-affiliation-query",
    "runtime": "python3.9",
    "handler": "lambda_affiliation_example.lambda_handler",
    "memory_size": 1024,  # MB
    "timeout": 300,       # 5 minutes (max for most queries)
    "environment_variables": {
        "DB_HOST": "your-rds-endpoint.amazonaws.com",
        "DB_NAME": "augur",
        "DB_PORT": "5432",
        "DB_SECRET_NAME": "augur-db-credentials"  # Secrets Manager
    },
    "vpc_config": {
        "subnet_ids": ["subnet-12345", "subnet-67890"],  # Private subnets
        "security_group_ids": ["sg-database-access"]
    },
    "layers": [
        "arn:aws:lambda:us-east-1:123456789:layer:pandas-plotly:1"  # Pre-built layer
    ]
}

API_GATEWAY_CONFIG = {
    "api_name": "8knot-analytics-api",
    "stage": "prod",
    "endpoints": [
        {
            "path": "/affiliation/chart",
            "method": "POST",
            "lambda_function": "eightknot-affiliation-query",
            "request_body": {
                "repo_ids": [1, 2, 3],
                "operation": "affiliation_chart",
                "min_contributions": 1
            }
        },
        {
            "path": "/affiliation/table", 
            "method": "POST",
            "lambda_function": "eightknot-affiliation-query"
        },
        {
            "path": "/languages/chart",
            "method": "POST", 
            "lambda_function": "eightknot-languages-query"
        }
    ]
}

def create_lambda_deployment_script():
    """Generate AWS CLI deployment script"""
    
    script = f"""#!/bin/bash
# Deploy 8Knot Lambda Functions

echo "🚀 Deploying 8Knot Analytics Lambda Functions..."

# 1. Package Lambda function
echo "📦 Packaging Lambda function..."
zip -r lambda_function.zip lambda_affiliation_example.py requirements.txt

# 2. Create or update Lambda function
echo "☁️ Creating Lambda function..."
aws lambda create-function \\
    --function-name {LAMBDA_CONFIG['function_name']} \\
    --runtime {LAMBDA_CONFIG['runtime']} \\
    --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role \\
    --handler {LAMBDA_CONFIG['handler']} \\
    --zip-file fileb://lambda_function.zip \\
    --memory-size {LAMBDA_CONFIG['memory_size']} \\
    --timeout {LAMBDA_CONFIG['timeout']} \\
    --environment Variables='{json.dumps(LAMBDA_CONFIG["environment_variables"])}' \\
    --vpc-config SubnetIds={','.join(LAMBDA_CONFIG['vpc_config']['subnet_ids'])},SecurityGroupIds={','.join(LAMBDA_CONFIG['vpc_config']['security_group_ids'])}

# 3. Create API Gateway
echo "🌐 Creating API Gateway..."
aws apigateway create-rest-api \\
    --name {API_GATEWAY_CONFIG['api_name']} \\
    --description "8Knot Analytics API"

# 4. Set up permissions
echo "🔐 Setting up permissions..."
aws lambda add-permission \\
    --function-name {LAMBDA_CONFIG['function_name']} \\
    --statement-id apigateway-invoke \\
    --action lambda:InvokeFunction \\
    --principal apigateway.amazonaws.com

echo "✅ Deployment complete!"
echo "📊 Test your API at: https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/affiliation/chart"
"""
    
    return script

def create_requirements_txt():
    """Generate requirements.txt for Lambda Layer"""
    requirements = """
pandas==1.5.3
plotly==5.17.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
boto3==1.34.0
"""
    return requirements.strip()

def create_sam_template():
    """Generate AWS SAM template for easier deployment"""
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Description": "8Knot Analytics Serverless API",
        
        "Parameters": {
            "DatabaseHost": {
                "Type": "String",
                "Description": "RDS database endpoint"
            },
            "DatabaseSecretName": {
                "Type": "String", 
                "Default": "augur-db-credentials",
                "Description": "Secrets Manager secret name for DB credentials"
            }
        },
        
        "Resources": {
            "AffiliationQueryFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "CodeUri": "src/",
                    "Handler": "lambda_affiliation_example.lambda_handler",
                    "Runtime": "python3.9",
                    "MemorySize": 1024,
                    "Timeout": 300,
                    "Environment": {
                        "Variables": {
                            "DB_HOST": {"Ref": "DatabaseHost"},
                            "DB_SECRET_NAME": {"Ref": "DatabaseSecretName"}
                        }
                    },
                    "VpcConfig": {
                        "SecurityGroupIds": ["sg-database-access"],
                        "SubnetIds": ["subnet-12345", "subnet-67890"]
                    },
                    "Policies": [
                        "VPCAccessExecutionRole",
                        {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Action": ["secretsmanager:GetSecretValue"],
                                "Resource": f"arn:aws:secretsmanager:*:*:secret:augur-db-credentials*"
                            }]
                        }
                    ],
                    "Events": {
                        "AffiliationChart": {
                            "Type": "Api",
                            "Properties": {
                                "Path": "/affiliation/chart",
                                "Method": "post"
                            }
                        },
                        "AffiliationTable": {
                            "Type": "Api", 
                            "Properties": {
                                "Path": "/affiliation/table",
                                "Method": "post"
                            }
                        }
                    }
                }
            }
        },
        
        "Outputs": {
            "ApiGatewayEndpoint": {
                "Description": "API Gateway endpoint URL",
                "Value": {"Fn::Sub": "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"}
            }
        }
    }
    
    return json.dumps(template, indent=2)

def create_test_client():
    """Create a test client to call the Lambda API"""
    
    test_script = """
import requests
import json

# Your API Gateway endpoint (replace with actual URL)
API_BASE_URL = "https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod"

def test_affiliation_chart():
    \"\"\"Test the affiliation chart endpoint\"\"\"
    
    payload = {
        "operation": "affiliation_chart",
        "repo_ids": [1, 2, 3],
        "min_contributions": 2,
        "email_filter": ["gmail.com"]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/affiliation/chart",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Generated chart in {result['processing_time_seconds']}s")
        print(f"📊 Data rows: {result['data_rows']}")
        return result['data']  # Plotly JSON
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

def test_affiliation_table():
    \"\"\"Test the affiliation table endpoint\"\"\"
    
    payload = {
        "operation": "affiliation_table", 
        "repo_ids": [25481],  # plotly.py repo
        "min_contributions": 1
    }
    
    response = requests.post(
        f"{API_BASE_URL}/affiliation/table",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Generated table in {result['processing_time_seconds']}s")
        return result['data']  # Plotly JSON
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    print("🧪 Testing 8Knot Lambda API...")
    
    # Test chart endpoint
    chart_data = test_affiliation_chart()
    
    # Test table endpoint
    table_data = test_affiliation_table()
    
    print("🎉 Testing complete!")
"""
    
    return test_script

def compare_architectures():
    """Compare Celery vs Lambda architectures"""
    
    comparison = """
# Architecture Comparison: Celery vs AWS Lambda

## Current 8Knot (Celery + Redis + PostgreSQL)

```
User Request → Dash → Trigger Celery Task → Wait/Poll
                ↓
            Celery Worker → SQL Query → Store in PostgreSQL Cache
                ↓
            Dash Callback → Check Cache → Retrieve → Display
```

**Infrastructure Needed:**
- Redis server (Celery broker)
- PostgreSQL cache database
- Celery worker processes
- Load balancer for workers
- Monitoring for worker health

**Scaling:**
- Manual worker scaling
- Fixed infrastructure costs
- Complex deployment

## AWS Lambda Architecture

```
User Request → API Gateway → Lambda Function → SQL Query → Return JSON
```

**Infrastructure Needed:**
- Lambda function (serverless)
- API Gateway (managed)
- RDS database (existing)
- Secrets Manager (credentials)

**Scaling:**
- Automatic scaling (0-1000+ concurrent)
- Pay-per-use pricing
- Simple deployment

## Performance Comparison

| Metric | Celery | Lambda |
|--------|--------|---------|
| **Cold Start** | None | 1-3 seconds |
| **Warm Request** | 0.5-2s | 0.1-0.5s |
| **Concurrent Users** | Limited by workers | 1000+ automatic |
| **Max Query Time** | No limit | 15 minutes |
| **Cost (100 req/day)** | $50-200/month | $1-5/month |
| **Cost (10k req/day)** | $200-500/month | $20-50/month |

## Lambda Benefits for 8Knot

✅ **Auto-scaling**: Handle traffic spikes automatically
✅ **Cost efficiency**: Pay only for actual usage
✅ **No server management**: AWS handles everything
✅ **Built-in retry**: Automatic error handling
✅ **Easy deployment**: Single zip file upload
✅ **Monitoring**: CloudWatch logs/metrics included
✅ **Security**: VPC + Secrets Manager integration

## Lambda Considerations

⚠️ **Cold starts**: First request takes 1-3 seconds
⚠️ **15-min limit**: Very long queries might timeout
⚠️ **Database connections**: Need connection pooling
⚠️ **Package size**: 50MB limit (use layers for pandas/plotly)

## Migration Strategy

1. **Phase 1**: Convert fastest queries (< 30 seconds)
2. **Phase 2**: Optimize database queries for Lambda
3. **Phase 3**: Replace Dash with React + Lambda API
4. **Phase 4**: Decommission Celery infrastructure

## Cost Savings Example

**Current Celery Infrastructure:**
- EC2 instances: $100/month
- Redis: $30/month  
- PostgreSQL cache: $50/month
- Load balancer: $20/month
- **Total: $200/month**

**Lambda Alternative:**
- Lambda executions: $10/month
- API Gateway: $5/month
- **Total: $15/month**

**Savings: 92% reduction in infrastructure costs!**
"""
    
    return comparison

if __name__ == "__main__":
    print("🏗️ AWS Lambda Deployment Example for 8Knot")
    print("=" * 50)
    
    # Generate deployment files
    with open("deploy_lambda.sh", "w") as f:
        f.write(create_lambda_deployment_script())
    print("✅ Created deploy_lambda.sh")
    
    with open("requirements.txt", "w") as f:
        f.write(create_requirements_txt())
    print("✅ Created requirements.txt")
    
    with open("template.yaml", "w") as f:
        f.write(create_sam_template())
    print("✅ Created SAM template.yaml")
    
    with open("test_lambda_api.py", "w") as f:
        f.write(create_test_client())
    print("✅ Created test_lambda_api.py")
    
    with open("LAMBDA_VS_CELERY.md", "w") as f:
        f.write(compare_architectures())
    print("✅ Created LAMBDA_VS_CELERY.md")
    
    print("\n🚀 Ready to deploy!")
    print("1. Configure AWS credentials")
    print("2. Run: chmod +x deploy_lambda.sh && ./deploy_lambda.sh")
    print("3. Test with: python test_lambda_api.py") 