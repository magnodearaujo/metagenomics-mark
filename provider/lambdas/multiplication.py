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
          for iteration in range(1, (count + 1)):
            logger.debug(f"Iteration {iteration}: Processing resource '{name}' with content: {resource}")        
            new_template[f"{name}{iteration}"] = resource.copy() 
            del new_template[f"{name}{iteration}"]['MultiplyKey']  # Remove MultiplyKey from the new resource
        else:
          logger.debug(f"Resource '{name}' does not match MultiplyKey '{key}', skipping multiplication.")
          new_template[name] = resource.copy()
        
    return_status = 'success'
    logger.debug(f"New template after processing: {new_template}")
    return_fragment = new_template
    #return_fragment = template

    return return_status, return_fragment

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
