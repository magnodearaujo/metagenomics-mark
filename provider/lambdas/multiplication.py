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

def parse_newmultiply_params(event):
    """
    Parses multiplication parameters from the event.

    Args:
        event (dict): The event dictionary containing parameters.

    Returns:
        dict: On success, returns worklist, where worklist is a list of dicts with keys 'key', 'count', and 'placeholder'.

    Raises:
        ValueError: If the parameters are not in the expected format or types.
    """
    logger.debug("Handling parameters")
    
    newmultiply_key = event.get('params', {}).get('NewMultiplyKey')
    logger.debug(f"NewMultiplyKey extracted: {type(newmultiply_key)}: {newmultiply_key}")

    newmultiply_count = event.get('params', {}).get('NewMultiply')
    logger.debug(f"NewMultiply extracted: {type(newmultiply_count)}: {newmultiply_count}")

    newplaceholder = event.get('params', {}).get('NewPlaceholder', '%d')
    logger.debug(f"NewPlaceholder extracted: {type(newplaceholder)}: {newplaceholder}")

    if isinstance(newmultiply_key, str):
        logger.debug("Processing single value arguments")

        if not isinstance(newmultiply_count, int):
            logger.error(f"NewMultiply should be an integer, got {type(newmultiply_count)}: {newmultiply_count}")
            raise ValueError(f"NewMultiply should be an integer, got {type(newmultiply_count)}: {newmultiply_count}")
            
        if isinstance(newplaceholder, list):
            logger.error(f"NewPlaceholder should be a string, got {type(newplaceholder)}: {newplaceholder}")
            raise ValueError(f"NewPlaceholder should be a string, got {type(newplaceholder)}: {newplaceholder}")        
        
        worklist = [ { 'key': newmultiply_key, 'count': newmultiply_count, 'placeholder': newplaceholder } ]
        logger.debug(f"Worklist created from single argument: {worklist}")
    elif isinstance(newmultiply_key, list):
        logger.debug("Processing list value arguments")

        if not isinstance(newmultiply_count, list):
            logger.error(f"NewMultiply should be a list, got {type(newmultiply_count)}: {newmultiply_count}")
            raise ValueError(f"NewMultiply should be a list, got {type(newmultiply_count)}: {newmultiply_count}")
        
        try:
            newmultiply_count = [int(count) for count in newmultiply_count]  # Ensure all counts are integers
        except TypeError as e:
            logger.error(f"NewMultiply list contains non-integer values: {e}")
            raise ValueError(f"NewMultiply list contains non-integer values: {e}")
        
        if not isinstance(newplaceholder, list):
            newplaceholder = [newplaceholder] * len(newmultiply_key)

        if len(newmultiply_key) != len(newmultiply_count) or len(newmultiply_key) != len(newplaceholder):
            logger.error("NewMultiplyKey, NewMultiply, and NewPlaceholder lists must be of the same length.")
            raise ValueError("NewMultiplyKey, NewMultiply, and NewPlaceholder lists must be of the same length.")
        
        keys = ['key', 'count', 'placeholder']
        worklist = [dict(zip(keys, values)) for values in zip(newmultiply_key, newmultiply_count, newplaceholder)]
        logger.debug(f"Worklist created from list arguments: {worklist}")
    else: 
        logger.error(f"Unexpected type for NewMultiplyKey: {type(newmultiply_key)}")
        raise ValueError(f"Unexpected type for NewMultiplyKey: {type(newmultiply_key)}")
    
    logger.debug("Done handling parameters")
    return worklist

def handler(event, context):
    logger.debug(f"Received event: {json.dumps(event, indent=2)} ")
    logger.debug(f"Context: {context}")
    
    # Call the new function and handle its result
    try:
        worklist = parse_newmultiply_params(event)
    except ValueError as e:
        logger.error(f"Error parsing parameters: {e}")
        return {
            'requestId': event.get('requestId', 'unknown'),
            'status': 'failure',
            'message': str(e)
        }
    
    logger.debug(f"Worklist created: {worklist}")

    multiply_value = event.get('params', {}).get('Multiply', 1)
    logger.debug(f"Multiply value extracted: {multiply_value}")
    multiply_key = event.get('params').get('MultiplyKey')
    placeholder = event.get('params', {}).get('Placeholder', '%d')
    count = int(multiply_value)
    logger.debug(f"Count for multiplication: {count}")

    #result = multiply_template(event['fragment'], count, multiply_key, placeholder, context)

    for item in worklist:
        logger.debug(f"Processing item: {item}")
        result = multiply_template(event['fragment'], item['count'], item['key'], item['placeholder'], context)
        if result['status'] == 'failure':
            logger.error(f"Error during multiplication: {result.get('message', 'Unknown error')}")
            return {
                'requestId': event.get('requestId', 'unknown'),
                'status': 'failure',
                'message': result.get('message', 'Unknown error')
            }
        event['fragment'] = result['template']

    print(f"Returning result: {result}")
    returnvalue = {
        'requestId': event['requestId'],
        'status': result['status'],
        'fragment': result['template'],
    }
    if 'message' in result:
        returnvalue['message'] = result['message']

    logger.info(f"Final returning value: {json.dumps(returnvalue, indent=2)}")

    return returnvalue
