#!/bin/bash

aws cloudformation deploy \
  --template-file registration.yaml \
  --stack-name tudelft-resources-consumer \
  --capabilities CAPABILITY_NAMED_IAM