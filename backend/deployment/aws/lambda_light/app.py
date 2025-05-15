import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError

lambda_client = boto3.client("lambda")
s3_client = boto3.client("s3")

HEAVYWEIGHT_FUNCTION_NAME = os.environ["HEAVYWEIGHT_FUNCTION_NAME"]
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def lambda_handler(event, context):
    http_method = event["httpMethod"]
    path = event["path"]

    if http_method == "POST" and path == "/recommend":
        # Generate explicit Job ID
        job_id = str(uuid.uuid4())

        # Parse request
        body = json.loads(event["body"])
        description = body.get("description", "")
        clear_memory = body.get("clear_memory", False)

        # Prepare payload for Heavyweight Lambda
        payload = json.dumps(
            {"job_id": job_id, "description": description, "clear_memory": clear_memory}
        )

        # Invoke Heavyweight Lambda asynchronously
        lambda_client.invoke(
            FunctionName=HEAVYWEIGHT_FUNCTION_NAME,
            InvocationType="Event",
            Payload=payload,
        )

        # Immediately return explicit Job ID to client
        return {
            "statusCode": 202,
            "body": json.dumps({"job_id": job_id}),
            "headers": {"Content-Type": "application/json"},
        }

    elif http_method == "GET" and path.startswith("/status/"):
        # Extract job_id from path
        job_id = event["pathParameters"]["job_id"]

        try:
            # Check if playlist exists in S3
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f"{job_id}.json")
            playlist_data = json.loads(response["Body"].read())

            return {
                "statusCode": 200,
                "body": json.dumps({"status": "completed", "playlist": playlist_data}),
                "headers": {"Content-Type": "application/json"},
            }

        except s3_client.exceptions.NoSuchKey:
            # Playlist not ready yet
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "processing"}),
                "headers": {"Content-Type": "application/json"},
            }
        except ClientError as e:
            # Handle potential S3 errors
            print(f"[S3 Error]: {e.response['Error']['Message']}")
            return {
                "statusCode": 500,
                "body": json.dumps(
                    {"status": "error", "message": "Internal server error"}
                ),
                "headers": {"Content-Type": "application/json"},
            }

    else:
        # Return error for unsupported paths/methods
        print(f"[Request Error]: Unsupported path/method ({http_method} {path})")
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Endpoint not found."}),
            "headers": {"Content-Type": "application/json"},
        }
