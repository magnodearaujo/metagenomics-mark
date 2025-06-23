#!/bin/bash

aws cloudformation deploy \
  --template-file example.yaml \
  --stack-name tu-count-example \
  --capabilities CAPABILITY_NAMED_IAM