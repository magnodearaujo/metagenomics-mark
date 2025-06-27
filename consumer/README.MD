# Consumer Directory

This directory contains example CloudFormation templates that demonstrate how to use the **TUMultiply** transformation function (macro).

## What is TUMultiply?

**TUMultiply** is a CloudFormation macro that allows you to easily create multiple identical AWS resources (such as EC2 instances, SQS queues, etc.) by specifying a single resource and using a `Fn::Transform` block in your template.  
With this approach, you can use CloudFormation parameters and intrinsic functions for dynamic resource multiplication, making your templates more flexible and maintainable.

## How to Use

### 1. Add the Transform Block

In your CloudFormation template, add a `Fn::Transform` block inside the `Resources` section.  
You can specify `Multiply` and `MultiplyKey` as **single values** (for one multiplication) or as **lists** (to perform multiple, independent multiplications in one template):

#### **Single Value Example**

```yaml
Resources:
  Fn::Transform:
    Name: TUMultiply
    Parameters:
      MultiplyKey: Instances
      Multiply: !Ref InstanceCount
```

#### **List Value Example**

```yaml
Resources:
  Fn::Transform:
    Name: TUMultiply
    Parameters:
      MultiplyKey:
        - Instances
        - Tester
      Multiply: 
        - !Ref InstanceCount
        - 3
```

- When using lists, each entry in `MultiplyKey` is paired with the corresponding entry in `Multiply` (and optionally `Placeholder`).
- This allows you to multiply different sets of resources with different counts in a single function invocation.

### 2. Tag Resources to Multiply

For any resource you want to replicate, add a `MultiplyKey` property that matches one of the keys in your transform parameters:

```yaml
Resources:
  SQS:
    Type: AWS::SQS::Queue
    MultiplyKey: Instances

  MyBucket:
    Type: AWS::S3::Bucket
    MultiplyKey: Tester
```

- In the single-value case, all resources with `MultiplyKey: Instances` will be multiplied by the value of `Multiply`.
- In the list case, resources with `MultiplyKey: Instances` will be multiplied by the first value in `Multiply`, and those with `MultiplyKey: Tester` by the second value, and so on.

### 3. Deploy Your Template

Deploy your template as usual with the AWS CLI or CloudFormation Console.
The macro will process your template and expand the resources before stack creation.

## Example

See [`example.yaml`](example.yaml):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Example using TUMultiply with Fn::Transform

Parameters:
  InstanceCount:
    Type: Number
    Default: 2

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
- The 3 created buckets will have bucketsnames `bucket-1-test`, `bucket-2-test` and `bucket-3-test`. The `%d` is replaced by the iteration number. Note that without this the stack would fail since it would try to create three buckets with the same bucketname

## Notes

- You must have the TUMultiply macro registered in your AWS account. You can use the `register.sh` script which deploys the `registration.yaml` stack that performs this registration (see the provider directory for details). This needs to be done only once in your account.
- The macro works with any resource type that can be duplicated.
- Intrinsic functions (`!Ref`, `!Sub`, etc.) in properties are preserved and resolved by CloudFormation after macro processing.
- You can use parameters and intrinsic functions for the `Multiply` value and other macro parameters.
- If you use lists for `Multiply`, `MultiplyKey`, and optionally `Placeholder`, they must all be the same length.

For a more elaborate real-life example see the [mvdb.yaml](mvdb.yaml) file.

---

For more advanced usage or troubleshooting, see