import boto3
import os
import time

def lambda_handler(event, context):
    instance_id = event.get("instance_id")
    region = event.get("region", "ap-south-1")
    hostname = event.get("hostname", "unknown-host")

    ec2 = boto3.client("ec2", region_name=region)

    print(f" Starting reboot for {instance_id} ({hostname}) in region {region}")

    # Step 1: Describe attached volumes
    try:
        instance_desc = ec2.describe_instances(InstanceIds=[instance_id])
        block_devices = instance_desc["Reservations"][0]["Instances"][0]["BlockDeviceMappings"]

        volume_ids = [bdm["Ebs"]["VolumeId"] for bdm in block_devices if "Ebs" in bdm]

        print(f" Found volumes: {volume_ids}")
    except Exception as e:
        print(f" Failed to get volumes: {e}")
        return {"status": "error", "step": "describe_volumes", "error": str(e)}

    # Step 2: Snapshot volumes
    snapshot_ids = []
    for vol_id in volume_ids:
        try:
            snap = ec2.create_snapshot(
                VolumeId=vol_id,
                Description=f"Pre-reboot snapshot for {hostname}"
            )
            snapshot_ids.append(snap["SnapshotId"])
            print(f" Created snapshot: {snap['SnapshotId']}")
        except Exception as e:
            print(f" Failed to snapshot {vol_id}: {e}")

    # Step 3: Reboot instance
    try:
        ec2.reboot_instances(InstanceIds=[instance_id])
        print(f" Reboot command sent to {instance_id}")
    except Exception as e:
        print(f" Reboot failed: {e}")
        return {"status": "error", "step": "reboot", "error": str(e)}

    # Step 4: Wait briefly for instance to come back (basic wait, will improve later)
    print(" Waiting for instance to enter 'running' state...")
    ec2_waiter = ec2.get_waiter('instance_status_ok')
    try:
        ec2_waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 15, 'MaxAttempts': 20})
        print(" Instance is running and passed status checks.")
    except Exception as e:
        print(f" Post-reboot check failed: {e}")
        # Will trigger SNOW + email handler in later steps

    return {
        "status": "success",
        "hostname": hostname,
        "instance_id": instance_id,
        "snapshots": snapshot_ids
    }