# First Lambda Function

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket = event['s3_bucket']

    # Download the data from s3 to /tmp/image.png
    s3.download_file(bucket,key,"/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

# Second Lambda Function

import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-endpoint'
runtime = boto3.client('runtime.sagemaker')

def lambda_handler(event, context):
    print("Received event:" + json.dumps(event,indent=2))

    image = event['image_data']
    # image = event['image_data']
    payload = base64.b64decode(image)
    print(payload)

    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT,
        ContentType='image/png',
        Body=payload)


    inferences = json.loads(response['Body'].read().decode())


    # We return the data back to the Step Function
    event["inferences"] = inferences
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }

# Third Lambda function

import json

THRESHOLD = .93

def lambda_handler(event, context):

    # Grab the inferences from the event
    inferences = event['inferences']

    # Check if any values in our inferences are above THRESHOLD
    if max(inferences) >= THRESHOLD:
        meets_threshold = True
    else:
        meets_threshold = False

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
