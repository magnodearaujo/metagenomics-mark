#!/bin/bash

aws cloudformation deploy --template-file mvdb.yaml --stack-name mvdb-example --capabilities CAPABILITY_NAMED_IAM --region eu-central-1 --profile $1
