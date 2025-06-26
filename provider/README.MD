# TUCountMacro Provider

This directory contains the resources and deployment scripts for the **TUCountMacro** CloudFormation macro.

## What is TUCountMacro?

**TUCountMacro** is a CloudFormation macro that enables consumers to use a `Count` property in their AWS CloudFormation templates. This allows you to easily create multiple identical resources (such as EC2 instances, SQS queues, etc.) by specifying a single resource with a `Count` property, rather than duplicating resource definitions.

## How does it work?

- The macro is implemented as an AWS Lambda function, packaged and deployed using the scripts in this directory.
- When a consumer includes `Transform: TUCountMacro` at the top of their CloudFormation template, the macro is invoked during stack creation or update.
- The macro scans the template for resources with a `Count` property and automatically expands them into multiple resources, each with unique logical IDs.

## Example Usage (Consumer Template)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Example using TUCountMacro
Transform: TUCountMacro

Resources:
  MyQueue:
    Type: AWS::SQS::Queue
    Count: 3
```

The above template will be transformed by the macro into three separate SQS queue resources.

## How to Deploy the Macro

1. **Package the Lambda function and dependencies:**
   - Run `deploy_tudelft_resources.sh` to zip the Lambda code, upload it to S3, and deploy the macro stack.


## How to Use as a Consumer

- **Register the macro in the consumer's AWS account:**
  
  Please see the corresponding script in the consumer directory. This action needs to be run only once for an account.


- In the consumer's CloudFormation templates, add `Transform: TUCountMacro` at the top.
- Use the `Count` property in any resource you want to replicate.
- Deploy your stack as usual; the macro will handle the expansion.

## Benefits

- **Simplifies templates:** No need to manually duplicate resource definitions.
- **Reusable:** Works for any resource type that supports duplication.

## Limitations

- The macro only processes resources with a `Count` property.
- Logical IDs are automatically generated based on the original resource name and index.
- Intrinsic functions (`!Ref`, `!Sub`, etc.) in properties are preserved and resolved by CloudFormation after macro processing. **This particularly means that you cannot use parameters for the `Count` value.**


---

For more details or troubleshooting, see the comments in the deployment script or the Lambda