import boto3
import json
import os

sns = boto3.client("sns")

def lambda_handler(event, context):
    instance_id = event.get("instance_id", "N/A")
    hostname = event.get("hostname", "N/A")
    region = event.get("region", "N/A")
    reason = event.get("reason", "Unknown")
    ticket = event.get("snow_ticket", "N/A")
    emails = event.get("notify_emails", [])

    topic_arn = os.getenv("SNS_TOPIC_ARN")

    subject = f"[ALERT] Validation failed after reboot - {hostname}"
    message = f"""
🚨 Reboot Validation Failed

Hostname     : {hostname}
Instance ID  : {instance_id}
Region       : {region}
SNOW Ticket  : {ticket}
Reason       : {reason}

This failure was detected automatically post-reboot validation.

Please investigate or escalate immediately.
"""

    if not topic_arn or not emails:
        print("❌ Missing SNS_TOPIC_ARN or recipient emails")
        return {"status": "error", "reason": "Missing config"}

    for email in emails:
        try:
            sns.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=message,
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
                }
            )
            print(f"📣 Alert sent to {email}")
        except Exception as e:
            print(f"❌ Failed to notify {email}: {e}")

    # Simulate SNOW ticket creation
    print(f"📋 Simulated SNOW ticket update for {ticket} - Validation failed")

    return {"status": "notified", "hostname": hostname}