def lambda_handler(event, context):
    print("Hello from CI/CD!")
    return {
        "statusCode": 200,
        "body": "Hello from CI/CD! This is a change!"
    }
