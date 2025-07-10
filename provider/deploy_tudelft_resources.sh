#!/bin/bash

timestamp=$(date +%Y-%m-%d-%H-%M)

(cd lambdas ; zip -r ../tudelft-resources-$timestamp.zip .)

aws s3 cp tudelft-resources-$timestamp.zip s3://tudelft-macro-resources-provider-bucket/ --profile $1

rm tudelft-resources-$timestamp.zip

aws cloudformation deploy --template-file tudelft-resources.yaml --stack-name tudelft-resources --parameter-overrides Timestamp="$timestamp" --capabilities CAPABILITY_NAMED_IAM --region eu-central-1 --profile "$1"

