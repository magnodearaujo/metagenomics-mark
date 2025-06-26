# Consumer Directory

This directory contains example CloudFormation templates that demonstrate how to use the **TUCountMacro** macro.

## What is TUCountMacro?

**TUCountMacro** is a CloudFormation macro that allows you to use a `Count` property in your resource definitions. This makes it easy to create multiple identical AWS resources (such as EC2 instances, SQS queues, etc.) without duplicating code in your template.

## How to Use

1. **Add the Transform**

   At the top of your CloudFormation template, add:
   ```yaml
   Transform: TUCountMacro
   ```

2. **Use the `Count` Property**

   For any resource you want to replicate, add a `Count` property:
   ```yaml
   Resources:
     SQS:
       Type: AWS::SQS::Queue
       Count: 2
   ```

   The macro will automatically expand this into two separate SQS queue resources.

3. **Deploy Your Template**

   Deploy your template as usual with the AWS CLI or CloudFormation Console.  
   The macro will process your template and expand the resources before stack creation.

## Example

See [`example.yaml`](example.yaml):

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Register TU Delft's Macro's. You only need to run this once in your account.
Transform: TUCountMacro

Resources:
  SQS:
    Type: AWS::SQS::Queue
    Count: 2
```

## Notes

- You must have the TUCountMacro macro registered in your AWS account. You can use the register.sh script which deploys the registration.yaml stack that performs this registration (see the provider directory for details). This needs to be done only once in your account.
- The macro works with any resource type that can be duplicated.
-  Intrinsic functions (`!Ref`, `!Sub`, etc.) in properties are preserved and resolved by CloudFormation after macro processing. **This particularly means that you cannot use parameters for the `Count` value.**

For a more elaborate real-life example see the [mvdb.yaml](mvdb.yaml) file. The count value is defined on line 120.

---

For more advanced usage or troubleshooting, see the [provider README](../provider/README.md).