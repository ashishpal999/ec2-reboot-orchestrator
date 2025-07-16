import boto3
import os

sns = boto3.client('sns')

def lambda_handler(event, context):
    hostname = event.get("hostname")
    reboot_time = event.get("scheduled_reboot_time")
    ticket = event.get("snow_ticket", "N/A")
    emails = event.get("notify_emails", [])
    
    # Customize your subject/message
    subject = f"[Reboot Notice] {hostname} scheduled reboot at {reboot_time} UTC"
    message = f"""
This is an automated notification.

The following server is scheduled for a reboot:
- Hostname: {hostname}
- Scheduled Time: {reboot_time} UTC
- ServiceNow Ticket: {ticket}

If this is unexpected, please contact the support team.

(This was triggered via EC2 Reboot Automation Pipeline)
"""

    print(f"📣 Sending notification for {hostname} to: {emails}")

    # Loop through emails and send SNS notifications (or use a topic in prod)
    for email in emails:
        try:
            response = sns.publish(
                TopicArn=os.getenv("SNS_TOPIC_ARN"),
                Subject=subject,
                Message=message,
                MessageAttributes={
                    'email': {
                        'DataType': 'String',
                        'StringValue': email
                    }
                }
            )
            print(f" Notification sent to {email}")
        except Exception as e:
            print(f" Failed to notify {email}: {e}")

    return {"status": "sent", "hostname": hostname}