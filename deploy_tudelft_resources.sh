#!/bin/bash

aws cloudformation deploy \
  --template-file tudelft-resources.yaml \
  --stack-name tudelft-resources \
  --capabilities CAPABILITY_NAMED_IAM




zip tudelft-resources.zip macro_lambda/*
aws s3 cp tudelft-resources.zip s3://tudelft-macro-resources/

