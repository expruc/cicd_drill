import os

def lambda_handler(event, context):
    tag = os.environ.get("DOCKER_TAG", "unknown")
    print(f"Hello from CI/CD! (tag: {tag})")
    return {
        "statusCode": 200,
        "body": f"Hello from lambda! (tag: {tag})"
    }
