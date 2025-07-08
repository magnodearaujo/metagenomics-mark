#!/bin/bash

aws cloudformation deploy \
  --template-file example.yaml \
  --stack-name tu-count-example \
  --parameter-overrides InstanceCount=2 \
  --capabilities CAPABILITY_NAMED_IAM