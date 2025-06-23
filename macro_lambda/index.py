import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event, indent=2))
    
    try:
        request_id = event['requestId']
        fragment = event['fragment']
        template_parameters = event.get('templateParameterValues', {})

        # Ensure format version
        fragment.setdefault("AWSTemplateFormatVersion", "2010-09-09")
        parameters = fragment.setdefault('Parameters', {})
        resources = fragment.setdefault('Resources', {})

        # Ensure Parameters
        if 'KeyName' not in parameters:
            parameters['KeyName'] = {
                "Type": "AWS::EC2::KeyPair::KeyName",
                "Default": "genomics",
                "Description": "EC2 KeyPair for SSH access"
            }

        if 'InstanceCount' not in parameters:
            parameters['InstanceCount'] = {
                "Type": "Number",
                "Default": 2,
                "Description": "Number of EC2 instances to create"
            }

        # Determine instance count (from param values or default)
        instance_count = int(template_parameters.get('InstanceCount', 2))
        key_name_ref = {"Ref": "KeyName"}

        # Create EC2 instances
        for i in range(1, instance_count + 1):
            instance_name = f"EC2Instance{i}"
            if instance_name not in resources:
                resources[instance_name] = {
                    "Type": "AWS::EC2::Instance",
                    "Properties": {
                        "InstanceType": "t3.large",
                        "ImageId": "ami-01179af425b2ee025",
                        "KeyName": key_name_ref,
                        "Tags": [
                            {"Key": "Name", "Value": f"clouduser-{i}"},
                            {"Key": "CreatedBy", "Value": "MacroFunction"}
                        ]
                    }
                }

        logger.info("Returning successful macro transformation.")
        return {
            "requestId": request_id,
            "status": "success",
            "fragment": fragment
        }

    except Exception as e:
        logger.exception("Macro failed with error")
        return {
            "requestId": event.get("requestId", "unknown"),
            "status": "failure",
            "errorMessage": str(e)
        }
