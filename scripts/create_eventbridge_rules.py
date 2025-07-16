import json
import boto3
from datetime import datetime, timedelta
import pytz
import os

LAMBDA_ARN = os.getenv('REBOOT_LAMBDA_ARN')
NOTIFY_LAMBDA_ARN = os.getenv('NOTIFY_LAMBDA_ARN')
VALIDATE_LAMBDA_ARN = os.getenv('VALIDATE_LAMBDA_ARN')
ACCOUNT_ID = '915535088821'  # your real AWS account ID

def create_event_rule(instance, rule_suffix="reboot"):
    hostname = instance["hostname"]
    instance_id = instance["instance_id"]
    region = instance["region"]
    schedule_time = instance["scheduled_reboot_time"]

    dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
    dt_utc = pytz.utc.localize(dt)
    cron_expr = f"cron({dt_utc.minute} {dt_utc.hour} {dt_utc.day} {dt_utc.month} ? {dt_utc.year})"
    rule_name = f"{rule_suffix}-{hostname.split('.')[0]}-{dt_utc.strftime('%Y%m%d%H%M')}"

    print(f"🔧 Creating rule: {rule_name} at {dt_utc.isoformat()} in {region}")
    events_client = boto3.client('events', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)

    events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expr,
        State='ENABLED',
        Description=f"Scheduled reboot for {hostname} ({instance_id})"
    )

    target = {
        'Id': '1',
        'Arn': LAMBDA_ARN,
        'Input': json.dumps(instance)
    }
    events_client.put_targets(Rule=rule_name, Targets=[target])

    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_ARN,
            StatementId=f"{rule_name}-invoke",
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f"arn:aws:events:{region}:{ACCOUNT_ID}:rule/{rule_name}"
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass

    print(f" Reboot rule created: {rule_name}")


def create_notify_event_rule(instance, rule_suffix="notify"):
    hostname = instance["hostname"]
    region = instance["region"]
    schedule_time = instance["scheduled_reboot_time"]

    dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
    notify_time = dt - timedelta(hours=1)
    notify_utc = pytz.utc.localize(notify_time)

    cron_expr = f"cron({notify_utc.minute} {notify_utc.hour} {notify_utc.day} {notify_utc.month} ? {notify_utc.year})"
    rule_name = f"{rule_suffix}-{hostname.split('.')[0]}-{notify_utc.strftime('%Y%m%d%H%M')}"

    print(f" Creating NOTIFY rule: {rule_name} at {notify_utc.isoformat()} in {region}")
    events_client = boto3.client('events', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)

    events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expr,
        State='ENABLED',
        Description=f"Notify owners for {hostname} 1 hour before reboot"
    )

    target = {
        'Id': '1',
        'Arn': NOTIFY_LAMBDA_ARN,
        'Input': json.dumps(instance)
    }
    events_client.put_targets(Rule=rule_name, Targets=[target])

    try:
        lambda_client.add_permission(
            FunctionName=NOTIFY_LAMBDA_ARN,
            StatementId=f"{rule_name}-invoke",
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f"arn:aws:events:{region}:{ACCOUNT_ID}:rule/{rule_name}"
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass

    print(f" Notify rule created: {rule_name}")


def create_validate_event_rule(instance, rule_suffix="validate"):
    hostname = instance["hostname"]
    region = instance["region"]
    schedule_time = instance["scheduled_reboot_time"]

    dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
    validate_time = dt + timedelta(minutes=5)
    validate_utc = pytz.utc.localize(validate_time)

    cron_expr = f"cron({validate_utc.minute} {validate_utc.hour} {validate_utc.day} {validate_utc.month} ? {validate_utc.year})"
    rule_name = f"{rule_suffix}-{hostname.split('.')[0]}-{validate_utc.strftime('%Y%m%d%H%M')}"

    print(f"🔍 Creating VALIDATE rule: {rule_name} at {validate_utc.isoformat()} in {region}")
    events_client = boto3.client('events', region_name=region)
    lambda_client = boto3.client('lambda', region_name=region)

    target = {
        'Id': '1',
        'Arn': VALIDATE_LAMBDA_ARN,
        'Input': json.dumps(instance)
    }
    events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=cron_expr,
        State='ENABLED',
        Description=f"Post-reboot validation for {hostname}"
    )
    events_client.put_targets(Rule=rule_name, Targets=[target])

    try:
        lambda_client.add_permission(
            FunctionName=VALIDATE_LAMBDA_ARN,
            StatementId=f"{rule_name}-invoke",
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=f"arn:aws:events:{region}:{ACCOUNT_ID}:rule/{rule_name}"
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass

    print(f" Validate rule created: {rule_name}")


def load_input_and_create_rules(input_file="input/mock_snow_input.json"):
    with open(input_file) as f:
        data = json.load(f)

    for instance in data:
        tags = instance.get("tags", {})
        if tags.get("EKS", "false").lower() == "true" or tags.get("ASG", "false").lower() == "true":
            print(f" Skipping {instance['hostname']} (EKS/ASG node)")
            continue

        create_event_rule(instance)
        create_notify_event_rule(instance)
        create_validate_event_rule(instance)


# Call the function only at the end
if __name__ == "__main__":
    load_input_and_create_rules()