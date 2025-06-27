# TUMultiply Provider

This directory contains the resources and deployment scripts for the **TUMultiply** CloudFormation transformation function.

## What is TUMultiply?

**TUMultiply** is a CloudFormation transformation function (macro) that enables consumers to easily create multiple identical resources (such as EC2 instances, SQS queues, etc.) by specifying a single resource and using a `Fn::Transform` block in their template.  
With this approach, you use macro parameters (such as the number of copies and a key to select resources) and can leverage CloudFormation parameters and intrinsic functions for dynamic resource multiplication.  
This makes your templates more flexible and maintainable.

## How does it work?

- The transformation is implemented as an AWS Lambda function, packaged and deployed using the scripts in this directory.
- Consumers use the `Fn::Transform` macro block in their CloudFormation templates to specify which resources to multiply and with what parameters.
- The macro processes all resources on the same level as the `Fn::Transform` block whose `MultiplyKey` matches the one specified in the transform parameters. It will expand these according to the provided parameters (such as a parameterized count).
- **You can use parameters and intrinsic functions for the count value and other macro parameters.**
- **You can specify `Multiply` and `MultiplyKey` as either single values or as lists to perform multiple, independent multiplications in one template.**

## Example Usage (Consumer Template)

### Single Value Example

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Example using TUMultiply with Fn::Transform

Parameters:
  InstanceCount:
    Type: Number
    Default: 3

Resources:
  Fn::Transform:
    Name: TUMultiply
    Parameters:
      Multiply: !Ref InstanceCount
      MultiplyKey: Instances

  SQS:
    Type: AWS::SQS::Queue
    MultiplyKey: Instances
```

In this example, all resources with `MultiplyKey: Instances` will be multiplied by the value of `InstanceCount`.

### List Value Example

```yaml
Resources:
  Fn::Transform:
    Name: TUMultiply
    Parameters:
      Multiply:
        - !Ref InstanceCount
        - 3
      MultiplyKey:
        - Instances
        - Tester

  SQS:
    Type: AWS::SQS::Queue
    MultiplyKey: Instances

  MyBucket:
    Type: AWS::S3::Bucket
    MultiplyKey: Tester
    Properties:
      BucketName: "bucket-%d-test"
```

In this example:
- All resources with `MultiplyKey: Instances` (here, `SQS`) will be multiplied by the value of `InstanceCount`.
- All resources with `MultiplyKey: Tester` (here, `MyBucket`) will be multiplied 3 times.

**How does the list mode work?**
- When using lists, each entry in `MultiplyKey` is paired with the corresponding entry in `Multiply` (and optionally `Placeholder`).
- This allows you to multiply different sets of resources with different counts in a single macro invocation.
- The lists for `Multiply`, `MultiplyKey`, and `Placeholder` (if used) must all be the same length.

## How to Deploy the Function

1. **Package the Lambda function and dependencies:**
   - Run `deploy_tudelft_resources.sh` to zip the Lambda code, upload it to S3, and deploy the stack.

## How to Use as a Consumer

- **Register the transformation function in your AWS account:**  
  Please see the corresponding script in the consumer directory. This action needs to be run only once per account.
- In your CloudFormation templates, use the `Fn::Transform` block to specify which resources to multiply and with what parameters.
- Tag any resource you want to replicate by adding the correct `MultiplyKey`.
- Deploy your stack as usual; the transformation will handle the expansion.

## Benefits

- **Simplifies templates:** No need to manually duplicate resource definitions.
- **Reusable:** Works for any resource type that supports duplication.
- **Parameterized:** The `Multiply` parameter for the transformation can be set through a stack parameter or intrinsic function.
- **Flexible:** Supports both single and multiple (list) multiplications in one template.

## Limitations

- The macro only processes resources with a `MultiplyKey` property whose value matches that of the transformation's parameter `MultiplyKey`.
- Logical IDs are automatically generated based on the original resource name and index. Beware that automatic generation of IDs can cause collisions with other IDs in the stack. In that case, the stack deployment will fail in the review phase.
- When using lists for `Multiply`, `MultiplyKey`, and `Placeholder`, all lists must be of the same length.

---

For more details or troubleshooting, see the comments in the deployment script or the Lambda source