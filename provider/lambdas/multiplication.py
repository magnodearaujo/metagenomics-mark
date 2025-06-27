import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def multiply_template(template, count, key, placeholder, context=None):

    new_template = {}
    for name, resource in template.items():
        if 'MultiplyKey' in resource and resource['MultiplyKey'] == key:
            logger.debug(f"Multiplying resource '{name}' with content: {resource}")   
            resource.pop('MultiplyKey')  # Remove MultiplyKey from the resource
            resourcesAfterMultiplication = multiply(name, resource, count, placeholder)
            if not set(resourcesAfterMultiplication.keys()) & set(new_template.keys()):
                new_template.update(resourcesAfterMultiplication)
            else:
                return { 
                    'status': 'failure',
                    'template': template,
                    'message': f"Resource '{name}' after multiplication conflicts with existing resources in the new template."
                }
        else:
            logger.debug(f"Resource '{name}' does not match MultiplyKey '{key}', skipping multiplication.")
            if name not in new_template:
                # If the resource does not match the MultiplyKey, just copy it as is
                new_template[name] = resource.copy()
            else:
                logger.warning(f"Resource '{name}' already exists in the new template, failing template to avoid duplication.")
                return { 
                    'status': 'failure',
                    'template': template,
                    'message': f"Resource '{name}' already exists in the new template, failing due to duplication." 
                }
        
    logger.debug(f"New template after processing: {json.dumps(new_template, indent=2)}")
    return_fragment = new_template

    return { 'status': 'success', 'template': return_fragment }

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

def parse_params(event):
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
    
    multiply_key = event.get('params', {}).get('MultiplyKey')
    logger.debug(f"MultiplyKey extracted: {type(multiply_key)}: {multiply_key}")

    multiply_count = event.get('params', {}).get('Multiply')
    logger.debug(f"Multiply extracted: {type(multiply_count)}: {multiply_count}")

    placeholder = event.get('params', {}).get('Placeholder', '%d')
    logger.debug(f"Placeholder extracted: {type(placeholder)}: {placeholder}")

    if isinstance(multiply_key, str):
        logger.debug("Processing single value arguments")

        try:
            multiply_count = int(multiply_count)
        except TypeError as e:
            logger.error(f"Multiply should be an integer: {e}")
            raise ValueError(f"Multiply should be an integer: {e}")

        if not isinstance(multiply_count, int):
            logger.error(f"Multiply should be an integer, got {type(multiply_count)}: {multiply_count}")
            raise ValueError(f"Multiply should be an integer, got {type(multiply_count)}: {multiply_count}")
            
        if isinstance(placeholder, list):
            logger.error(f"Placeholder should be a string, got {type(placeholder)}: {placeholder}")
            raise ValueError(f"Placeholder should be a string, got {type(placeholder)}: {placeholder}")        
        
        worklist = [ { 'key': multiply_key, 'count': multiply_count, 'placeholder': placeholder } ]
        logger.debug(f"Worklist created from single argument: {worklist}")
    elif isinstance(multiply_key, list):
        logger.debug("Processing list value arguments")

        if not isinstance(multiply_count, list):
            logger.error(f"Multiply should be a list, got {type(multiply_count)}: {multiply_count}")
            raise ValueError(f"Multiply should be a list, got {type(multiply_count)}: {multiply_count}")
        
        try:
            multiply_count = [int(count) for count in multiply_count]  # Ensure all counts are integers
        except TypeError as e:
            logger.error(f"Multiply list contains non-integer values: {e}")
            raise ValueError(f"Multiply list contains non-integer values: {e}")
        
        if not isinstance(placeholder, list):
            placeholder = [placeholder] * len(multiply_key)

        if len(multiply_key) != len(multiply_count) or len(multiply_key) != len(placeholder):
            logger.error("MultiplyKey, Multiply, and Placeholder lists must be of the same length.")
            raise ValueError("MultiplyKey, Multiply, and Placeholder lists must be of the same length.")
        
        keys = ['key', 'count', 'placeholder']
        worklist = [dict(zip(keys, values)) for values in zip(multiply_key, multiply_count, placeholder)]
        logger.debug(f"Worklist created from list arguments: {worklist}")
    else: 
        logger.error(f"Unexpected type for MultiplyKey: {type(multiply_key)}")
        raise ValueError(f"Unexpected type for MultiplyKey: {type(multiply_key)}")
    
    logger.debug("Done handling parameters")
    return worklist

def handler(event, context):
    logger.debug(f"Received event: {json.dumps(event, indent=2)} ")
    logger.debug(f"Context: {context}")
    
    try:
        worklist = parse_params(event)
    except ValueError as e:
        logger.error(f"Error parsing parameters: {e}")
        return {
            'requestId': event.get('requestId', 'unknown'),
            'status': 'failure',
            'message': str(e)
        }
    logger.debug(f"Worklist created: {worklist}")

    fragment = event.get('fragment', {}).copy()
    for item in worklist:
        logger.debug(f"Main replacement iteration: {item}")
        result = multiply_template(fragment, item['count'], item['key'], item['placeholder'], context)
        if result['status'] == 'failure':
            logger.error(f"Error during multiplication: {result.get('message', 'Unknown error')}")
            return {
                'requestId': event.get('requestId', 'unknown'),
                'status': 'failure',
                'message': result.get('message', 'Unknown error')
            }
        fragment = result['template']

    returnvalue = {
        'requestId': event['requestId'],
        'status': result['status'],
        'fragment': result['template'],
    }
    if 'message' in result:
        returnvalue['message'] = result['message']

    logger.info(f"Final returning value: {json.dumps(returnvalue, indent=2)}")

    return returnvalue
