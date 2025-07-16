import boto3
import time

def lambda_handler(event, context):
    instance_id = event.get("instance_id")
    region = event.get("region", "ap-south-1")
    hostname = event.get("hostname", "unknown-host")

    ec2 = boto3.client("ec2", region_name=region)
    print(f" Validating reboot of instance: {instance_id} ({hostname}) in {region}")

    # Wait for up to 5 minutes to become healthy
    try:
        print(" Waiting for instance to pass status checks...")
        waiter = ec2.get_waiter('instance_status_ok')
        waiter.wait(
            InstanceIds=[instance_id],
            WaiterConfig={
                'Delay': 15,
                'MaxAttempts': 20
            }
        )
        print(" Instance passed EC2 status checks")
        return {
            "status": "success",
            "hostname": hostname,
            "instance_id": instance_id
        }
    except Exception as e:
        print(f" Validation failed for {instance_id}: {e}")

        # Trigger failure handler Lambda (future step)
        failure_event = {
            "instance_id": instance_id,
            "hostname": hostname,
            "region": region,
            "reason": str(e),
            "snow_ticket": event.get("snow_ticket"),
            "notify_emails": event.get("notify_emails", [])
        }

        try:
            lambda_client = boto3.client('lambda', region_name=region)
            response = lambda_client.invoke(
                FunctionName='ec2-reboot-failure-handler',
                InvocationType='Event',
                Payload=json.dumps(failure_event)
            )
            print(" Triggered failure handler Lambda.")
        except Exception as invoke_error:
            print(f" Could not trigger failure handler: {invoke_error}")

        return {
            "status": "failed",
            "error": str(e),
            "hostname": hostname
        }