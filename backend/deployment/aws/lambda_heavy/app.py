import json
import os

import boto3
from botocore.exceptions import ClientError

from backend.core.orchestrator import Orchestrator

# Initialize AWS Secrets Manager and S3 clients
secretsmanager = boto3.client("secretsmanager")
s3_client = boto3.client("s3")

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
SECRET_NAME = os.environ["SECRET_NAME"]


def get_secrets():
    try:
        secret_value = secretsmanager.get_secret_value(SecretId=SECRET_NAME)
        secrets = json.loads(secret_value["SecretString"])
        required_keys = ["OPENAI_API_KEY", "GENIUS_API_KEY", "YOUTUBE_API_KEY"]
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
    job_id = event["job_id"]
    description = event["description"]
    clear_memory = event.get("clear_memory", False)

    try:
        # Retrieve API keys from Secrets Manager
        secrets = get_secrets()
        openai_api_key = secrets["OPENAI_API_KEY"]
        genius_api_key = secrets["GENIUS_API_KEY"]
        youtube_api_key = secrets["YOUTUBE_API_KEY"]

        # Perform heavy processing with orchestrator
        orchestrator = Orchestrator(
            openai_api_key, genius_api_key, youtube_api_key, clear_memory
        )
        playlist = orchestrator.run_planning_agent(description, num_tracks=20)

        # Store resulting playlist JSON to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"{job_id}.json",
            Body=json.dumps(playlist),
            ContentType="application/json",
        )

        print(f"[Success]: Job {job_id} completed and playlist stored in S3.")

    except Exception as e:
        print(f"[Processing Error]: Job {job_id} failed due to {str(e)}")
        # Optionally store an error message in S3 for client notification
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"{job_id}.json",
            Body=json.dumps({"status": "error", "message": str(e)}),
            ContentType="application/json",
        )
        raise e  # Re-raise exception for logging purposes
