# Consumer Directory

This directory contains example CloudFormation templates that demonstrate how to use the **TUMultiply** transformation function (macro).

## What is TUMultiply?

**TUMultiply** is a CloudFormation macro that allows you to easily create multiple identical AWS resources (such as EC2 instances, SQS queues, etc.) by specifying a single resource and using a `Fn::Transform` block in your template.  
With this approach, you can use CloudFormation parameters and intrinsic functions for dynamic resource multiplication, making your templates more flexible and maintainable.

## How to Use

1. **Add the Transform Block**

   In your CloudFormation template, add a `Fn::Transform` block inside the `Resources` section:
   ```yaml
   Resources:
     Fn::Transform:
       Name: TUMultiply
       Parameters:
         Multiply: !Ref InstanceCount
         MultiplyKey: Instances
   ```

2. **Tag Resources to Multiply**

   For any resource you want to replicate, add a `MultiplyKey` property that matches the key in your transform parameters:
   ```yaml
   Resources:
     SQS:
       Type: AWS::SQS::Queue
       MultiplyKey: Instances
   ```

   The macro will automatically expand this into as many resources as specified by the `Multiply` parameter.

3. **Deploy Your Template**

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
      Multiply: !Ref InstanceCount
      MultiplyKey: Instances

  SQS:
    Type: AWS::SQS::Queue
    MultiplyKey: Instances
```

## Notes

- You must have the TUMultiply macro registered in your AWS account. You can use the `register.sh` script which deploys the `registration.yaml` stack that performs this registration (see the provider directory for details). This needs to be done only once in your account.
- The macro works with any resource type that can be duplicated.
- Intrinsic functions (`!Ref`, `!Sub`, etc.) in properties are preserved and resolved by CloudFormation after macro processing.
- You can use parameters and intrinsic functions for the `Multiply` value and other macro parameters.

For a more elaborate real-life example see the [mvdb.yaml](mvdb.yaml) file.

---

For more advanced usage or troubleshooting, see the [provider README](../provider/README.md).