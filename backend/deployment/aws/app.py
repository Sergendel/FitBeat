import json
import os

import boto3

# import requests
from botocore.exceptions import ClientError

from backend.core.orchestrator import Orchestrator

# Initialize AWS Secrets Manager client
secretsmanager = boto3.client("secretsmanager")


def get_secrets():
    secret_name = os.environ["SECRET_NAME"]
    try:
        secret_value = secretsmanager.get_secret_value(SecretId=secret_name)
        secrets = json.loads(secret_value["SecretString"])
        required_keys = ["OPENAI_API_KEY", "GENIUS_API_KEY"]
        if not all(key in secrets for key in required_keys):
            raise KeyError("Missing required API keys in secrets.")
        return secrets
    except ClientError as e:
        print(f"[SecretsManager Error]: {e.response['Error']['Message']}")
        raise e
    except KeyError as e:
        print(f"[Secrets Key Error]: {str(e)}")
        raise e


def lambda_handler(event, context):
    """
    Lambda function to handle API requests for FitBeat.
    """

    # try:
    #     response = requests.get("https://api.genius.com", timeout=5)
    #     #print(f"✅ Explicit Lambda Genius API test successful:
    #     {response.status_code}")
    # except Exception as e:
    #     #print(f"❌ Explicit Lambda Genius API test failed explicitly: {e}")

    http_method = event["httpMethod"]
    path = event["path"]

    # Retrieve secrets (API keys)
    secrets = get_secrets()
    # print(
    #     f"Explicit local test: Loaded Genius API key explicitly "
    #     f"from Secrets Manager: {secrets['GENIUS_API_KEY'][:4]}****"
    # )
    openai_api_key = secrets["OPENAI_API_KEY"]
    genius_api_key = secrets["GENIUS_API_KEY"]

    # headers = {
    #     "Authorization": f"Bearer {genius_api_key}",
    #     "Accept": "application/json",
    # }

    # response = requests.get("https://api.genius.com/search?q=Hello", headers=headers)

    # print(f"Explicit Genius API response status: {response.status_code}")
    # print(f"Explicit Genius API response content: {response.text}")

    # print(f"keys = {openai_api_key} and {genius_api_key}")

    if http_method == "POST" and path == "/recommend":
        # Handle POST /recommend requests
        body = json.loads(event["body"])
        description = body.get("description", "")
        clear_memory = body.get("clear_memory", False)
        # print(f"description = {description}")

        orchestrator = Orchestrator(openai_api_key, genius_api_key, clear_memory)
        playlist = orchestrator.run_planning_agent(description, num_tracks=20)

        return {
            "statusCode": 200,
            "body": json.dumps({"playlist": playlist}),
            "headers": {"Content-Type": "application/json"},
        }

    elif http_method == "GET" and path == "/status":
        # Handle GET /status request (health check endpoint)
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "FitBeat Lambda is running smoothly."}),
            "headers": {"Content-Type": "application/json"},
        }

    else:
        # Return 404 for unsupported paths or methods
        print(f"[Request Error]: Unsupported path/method ({http_method} {path})")
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Endpoint not found."}),
            "headers": {"Content-Type": "application/json"},
        }
