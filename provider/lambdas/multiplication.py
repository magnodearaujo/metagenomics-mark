import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def multiply_template(template, count, key, placeholder, context=None):
    logger.info("Processing template to multiply resources based on 'Multiply' property...")
    logger.debug(f"Template type: {type(template)}, Template content: {template}")  
    logger.debug(f"Count: {count}")
    logger.debug(f"Context type: {type(context)}, Context content: {context}")
    new_template = {}

    for name, resource in template.items():
        logger.debug(f"Processing resource '{name}' with content: {resource}")   
        logger.debug(f"MultiplyKey: {resource.get('MultiplyKey', 'Not specified')}")
        if 'MultiplyKey' in resource and resource['MultiplyKey'] == key:
            resource.pop('MultiplyKey')  # Remove MultiplyKey from the resource
            resourcesAfterMultiplication = multiply(name, resource, count, placeholder)
            if not set(resourcesAfterMultiplication.keys()) & set(new_template.keys()):
                new_template.update(resourcesAfterMultiplication)
            else:
                status = 'failure'
                return { 
                    'status': status, 
                    'template': template,
                    'message': f"Resource '{name}' after multiplication conflicts with existing resources in the new template."
                }
        else:
            logger.debug(f"Resource '{name}' does not match MultiplyKey '{key}', skipping multiplication.")
            if name not in new_template:
                # If the resource does not match the MultiplyKey, just copy it as is
                logger.debug(f"Copying resource '{name}' without multiplication.")
                # Copy the resource without modification
                new_template[name] = resource.copy()
            else:
                logger.warning(f"Resource '{name}' already exists in the new template, failing template to avoid duplication.")
                status = 'failure'
                return { 
                    'status': status,
                    'template': template,
                    'message': f"Resource '{name}' already exists in the new template, failing to avoid duplication." 
                }
        
    return_status = 'success'
    logger.debug(f"New template after processing: {new_template}")
    return_fragment = new_template
    #return_fragment = template

    return { 'status': return_status, 'template': return_fragment }

def multiply(resource_name, resource_structure, count, placeholder):
    resources = {}
    logger.info(f"Multiplying resource '{resource_name}' {count} times.")
    #Loop according to the number of times we want to multiply, creating a new resource each time
    for iteration in range(1, (count + 1)):
        logger.debug(f"Iteration {iteration}: Processing resource '{resource_name}' with content: {resource_structure}")
        multipliedResourceStructure = update_placeholder(resource_structure,iteration, placeholder)
        resources[resource_name+str(iteration)] = multipliedResourceStructure
    return resources

def update_placeholder(resource_structure, iteration, placeholder='%d'):
    """
    Recursively replace all occurrences of `placeholder` in both keys and values within obj with the string value of iteration.
    Works for dicts, lists, and strings.
    """
    if isinstance(resource_structure, dict):
        new_dict = {}
        for k, v in resource_structure.items():
            # Replace in key
            new_key = k.replace(placeholder, str(iteration)) if isinstance(k, str) else k
            # Replace in value (recursive)
            new_dict[new_key] = update_placeholder(v, iteration, placeholder)
        return new_dict
    elif isinstance(resource_structure, list):
        return [update_placeholder(item, iteration, placeholder) for item in resource_structure]
    elif isinstance(resource_structure, str):
        return resource_structure.replace(placeholder, str(iteration))
    else:
        return resource_structure

def handler(event, context):
    print(f"Received event: {json.dumps(event, indent=2)} ")
    print(f"Context: {context}")
          
    multiply_value = event.get('params', {}).get('Multiply', 1)
    logger.debug(f"Multiply value extracted: {multiply_value}")
    multiply_key = event.get('params').get('MultiplyKey')
    placeholder = event.get('params', {}).get('Placeholder', '%d')
    count = int(multiply_value)
    logger.debug(f"Count for multiplication: {count}")
    result = multiply_template(event['fragment'], count, multiply_key, placeholder, context)

    print(f"Returning result: {result}")
    returnvalue = {
        'requestId': event['requestId'],
        'status': result['status'],
        'fragment': result['template'],
    }
    if 'message' in result:
        returnvalue['message'] = result['message']

    logger.debug(f"Final returning value: {returnvalue}")

    return returnvalue
