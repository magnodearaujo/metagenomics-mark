import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def multiply_template(template, count, key, context=None):
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
            resourcesAfterMultiplication = multiply(name, resource, count)
            if not set(resourcesAfterMultiplication.keys()) & set(new_template.keys()):
                new_template.update(resourcesAfterMultiplication)
            else:
                status = 'failed'
                return status, template
        else:
            logger.debug(f"Resource '{name}' does not match MultiplyKey '{key}', skipping multiplication.")
            if name not in new_template:
                # If the resource does not match the MultiplyKey, just copy it as is
                logger.debug(f"Copying resource '{name}' without multiplication.")
                # Copy the resource without modification
                new_template[name] = resource.copy()
            else:
                logger.warning(f"Resource '{name}' already exists in the new template, failing template to avoid duplication.")
                status = 'failed'
                return status, template
        
    return_status = 'success'
    logger.debug(f"New template after processing: {new_template}")
    return_fragment = new_template
    #return_fragment = template

    return return_status, return_fragment

def multiply(resource_name, resource_structure, count):
    resources = {}
    logger.info(f"Multiplying resource '{resource_name}' {count} times.")
    #Loop according to the number of times we want to multiply, creating a new resource each time
    for iteration in range(1, (count + 1)):
        logger.debug(f"Iteration {iteration}: Processing resource '{resource_name}' with content: {resource_structure}")
        multipliedResourceStructure = update_placeholder(resource_structure,iteration)
        resources[resource_name+str(iteration)] = multipliedResourceStructure
    return resources

def update_placeholder(resource_structure, iteration):
    #Convert the json into a string
    resourceString = json.dumps(resource_structure)
    #Count the number of times the placeholder is found in the string
    placeHolderCount = resourceString.count('%d')

    #If the placeholder is found then replace it
    if placeHolderCount > 0:
        logger.debug(f"Found {placeHolderCount} occurrences of decimal placeholder in JSON, replacing with iterator value {iteration}")
        #Make a list of the values that we will use to replace the decimal placeholders - the values will all be the same
        placeHolderReplacementValues = [iteration] * placeHolderCount
        #Replace the decimal placeholders using the list - the syntax below expands the list
        resourceString = resourceString % (*placeHolderReplacementValues,)
        #Convert the string back to json and return it
        return json.loads(resourceString)
    else:
        logger.debug("No occurrences of decimal placeholder found in JSON, therefore nothing will be replaced")
        return resource_structure

def handler(event, context):
    print(f"Received event: {json.dumps(event, indent=2)} ")
    print(f"Context: {context}")
          
    multiply_value = event.get('params', {}).get('Multiply', 1)
    logger.debug(f"Multiply value extracted: {multiply_value}")
    multiply_key = event.get('params').get('MultiplyKey')
    count = int(multiply_value)
    logger.debug(f"Count for multiplication: {count}")
    result = multiply_template(event['fragment'], count, multiply_key, context)

    print(f"Returning result: {result}")
    return {
        'requestId': event['requestId'],
        'status': result[0],
        'fragment': result[1],
    }
