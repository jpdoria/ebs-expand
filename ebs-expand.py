#!/usr/bin/env python

import argparse
import logging
import sys
import boto3
from datetime import datetime


class AWS:
    def __init__(self):
        self.ec2 = boto3.client('ec2', region_name=region)

    def getrv(self):
        try:
            logger.info('Fetching root volume of {}...'.format(instance_id))

            di_resp = self.ec2.describe_instances(
                InstanceIds=[
                    instance_id
                ]
            )
            old_vol_id = di_resp['Reservations'][0]['Instances'][0][
                             'BlockDeviceMappings'][0]['Ebs']['VolumeId']
            az = di_resp['Reservations'][0]['Instances'][0][
                         'Placement']['AvailabilityZone']
            dv_resp = self.ec2.describe_volumes(
                VolumeIds=[
                    old_vol_id
                ]
            )
            old_size = dv_resp['Volumes'][0]['Size']
            vol_type = dv_resp['Volumes'][0]['VolumeType']
            iops = dv_resp['Volumes'][0]['Iops']
            root_device = dv_resp['Volumes'][0]['Attachments'][0]['Device']

            logger.info('AvailabilityZone: {}'.format(az))
            logger.info('VolumeId: {}'.format(old_vol_id))
            logger.info('Size: {} GiB'.format(old_size))
            logger.info('VolumeType: {}'.format(vol_type))
            logger.info('Iops: {}'.format(iops))
            logger.info('RootDevice: {}'.format(root_device))

            return az, old_vol_id, old_size, vol_type, iops, root_device
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def ec2stop(self):
        try:
            logger.info('Stopping {}...'.format(instance_id))
            self.ec2.stop_instances(
                InstanceIds=[
                    instance_id
                ]
            )

            waiter = self.ec2.get_waiter('instance_stopped')

            waiter.wait(
                InstanceIds=[
                    instance_id
                ]
            )

            di_resp = self.ec2.describe_instances(
                InstanceIds=[
                    instance_id
                ]
            )
            ec2_status = di_resp['Reservations'][0]['Instances'][0]['State'][
                                 'Name']

            if ec2_status == 'stopped':
                logger.info('EC2Status: {}'.format(ec2_status))
                return ec2_status
            else:
                logger.error('{} is still running. Please try again.'
                             .format(instance_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def mksnap(self, old_vol_id):
        try:
            logger.info('Creating snapshot of {}...'.format(old_vol_id))

            cs_resp = self.ec2.create_snapshot(
                VolumeId=old_vol_id,
                Description='Created by ebs-expand.py'
            )
            snap_id = cs_resp['SnapshotId']

            waiter = self.ec2.get_waiter('snapshot_completed')

            waiter.wait(
                SnapshotIds=[
                    snap_id
                ]
            )

            self.ec2.create_tags(
                Resources=[
                    snap_id
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': 'old-vol-snap-{0}-{1}'.format(instance_id,
                                                               datetime_now)
                    }
                ]
            )

            ds_resp = self.ec2.describe_snapshots(
                SnapshotIds=[
                    snap_id
                ]
            )

            snap_status = ds_resp['Snapshots'][0]['State']

            if snap_status == 'completed':
                logger.info('SnapshotId: {}'.format(snap_id))
                logger.info('SnapshotStatus: {}'.format(snap_status))
                return snap_id
            else:
                logger.error('{} is still incomplete. Please try again.'
                             .format(snap_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def mkvol(self, snap_id, az, vol_type, iops):
        try:
            logger.info('Creating new volume using {}...'.format(snap_id))

            if vol_type == 'io1':
                cv_resp = self.ec2.create_volume(
                    Size=new_size,
                    SnapshotId=snap_id,
                    AvailabilityZone=az,
                    VolumeType=vol_type,
                    Iops=iops
                )
            else:
                cv_resp = self.ec2.create_volume(
                    Size=new_size,
                    SnapshotId=snap_id,
                    AvailabilityZone=az,
                    VolumeType=vol_type
                )

            new_vol_id = cv_resp['VolumeId']
            waiter = self.ec2.get_waiter('volume_available')

            waiter.wait(
                VolumeIds=[
                    new_vol_id
                ]
            )

            self.ec2.create_tags(
                Resources=[
                    new_vol_id
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': 'new-vol-{0}-{1}'.format(instance_id,
                                                          datetime_now)
                    }
                ]
            )

            dv_resp = self.ec2.describe_volumes(
                VolumeIds=[
                    new_vol_id
                ]
            )

            new_vol_status = dv_resp['Volumes'][0]['State']

            if new_vol_status == 'available':
                logger.info('NewVolumeId: {}'.format(new_vol_id))
                logger.info('NewVolumeStatus: {}'.format(new_vol_status))
                return new_vol_id
            else:
                logger.error('{} is still unavailable. Please try again.'
                             .format(new_vol_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def detachvol(self, old_vol_id, root_device):
        try:
            logger.info('Detaching old volume ({0}) from {1}...'.format(
                old_vol_id, instance_id))
            self.ec2.detach_volume(
                VolumeId=old_vol_id,
                InstanceId=instance_id,
                Device=root_device
            )

            waiter = self.ec2.get_waiter('volume_available')

            waiter.wait(
                VolumeIds=[
                    old_vol_id
                ]
            )

            self.ec2.create_tags(
                Resources=[
                    old_vol_id
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': 'old-vol-{0}-{1}'.format(instance_id,
                                                          datetime_now)
                    }
                ]
            )

            dv_resp = self.ec2.describe_volumes(
                VolumeIds=[
                    old_vol_id
                ]
            )

            old_vol_status = dv_resp['Volumes'][0]['State']

            if old_vol_status == 'available':
                logger.info('{} is now detached.'.format(old_vol_id))
            else:
                logger.error('{} is still attached. Please try again.'
                             .format(old_vol_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def attachvol(self, new_vol_id, root_device):
        try:
            logger.info('Attaching new volume ({0}) to {1}...'.format(
                new_vol_id, instance_id))
            self.ec2.attach_volume(
                VolumeId=new_vol_id,
                InstanceId=instance_id,
                Device=root_device
            )

            waiter = self.ec2.get_waiter('volume_in_use')

            waiter.wait(
                VolumeIds=[
                    new_vol_id
                ]
            )

            dv_resp = self.ec2.describe_volumes(
                VolumeIds=[
                    new_vol_id
                ]
            )

            new_vol_status = dv_resp['Volumes'][0]['State']

            if new_vol_status == 'in-use':
                logger.info('{} is now attached.'.format(new_vol_id))
            else:
                logger.error('{} is still unattached. Please try again.'
                             .format(new_vol_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def modifyec2(self, root_device, new_vol_id):
        try:
            logger.info('Enabling DeleteOnTermination on {}...'
                        .format(new_vol_id))
            self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                BlockDeviceMappings=[
                    {
                        'DeviceName': root_device,
                        'Ebs': {
                            'VolumeId': new_vol_id,
                            'DeleteOnTermination': True
                        }
                    }
                ]
            )
            logger.info('DeleteOnTermination: True')
        except Exception as e:
            logger.info(e, exc_info=True)
            sys.exit(1)

    def ec2start(self):
        try:
            self.ec2.start_instances(
                InstanceIds=[
                    instance_id
                ]
            )

            waiter = self.ec2.get_waiter('instance_running')

            waiter.wait(
                InstanceIds=[
                    instance_id
                ]
            )

            di_resp = self.ec2.describe_instances(
                InstanceIds=[
                    instance_id
                ]
            )

            ec2_status = di_resp['Reservations'][0]['Instances'][0]['State'][
                                 'Name']

            if ec2_status == 'running':
                logger.info('EC2Status: {}'.format(ec2_status))
            else:
                logger.error('{} is still stopped. Please try again.'
                             .format(instance_id))
                sys.exit(1)
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)

    def cleanup(self, old_vol_id, snap_id):
        while True:
            try:
                choice = str(input(
                    'Do you want to remove the old volume and snapshot? [Y/N] '
                    ).lower())

                if choice == 'y':
                    # Remove old volume
                    logger.info('Removing old EBS volume ({})...'
                                .format(old_vol_id))
                    self.ec2.delete_volume(
                        VolumeId=old_vol_id
                    )
                    logger.info('{} has been removed.'.format(old_vol_id))

                    # Remove snapshot
                    logger.info('Removing snapshot ({0}) of {1}...'
                                .format(snap_id, old_vol_id))
                    self.ec2.delete_snapshot(
                        SnapshotId=snap_id
                    )
                    logger.info('{} has been removed.'.format(snap_id))

                    break
                elif choice == 'n':
                    break
                else:
                    logger.error('Please choose between Y and N.')
            except Exception as e:
                logger.error(e, exc_info=True)
                sys.exit(1)


def main():
    try:
        aws = AWS()

        logger.info('Region: {}'.format(region))
        logger.info('InstanceId: {}'.format(instance_id))
        logger.info('NewSize: {} GiB'.format(new_size))

        # Get root volume
        az, old_vol_id, old_size, vol_type, iops, root_device = aws.getrv()

        # Check current volume size
        if old_size == new_size:
            logger.error('Please provide a new size greater than {} GiB.'
                         .format(old_size))
            sys.exit(1)
        elif old_size > new_size:
            logger.error('Old size ({}) > new size ({}). Goodbye!'
                         .format(old_size, new_size))
            sys.exit(1)

        # Stop the instance
        ec2_status = aws.ec2stop()

        # Create snapshot
        snap_id = aws.mksnap(old_vol_id)

        # Create new volume
        new_vol_id = aws.mkvol(snap_id, az, vol_type, iops)

        # Detach old volume
        aws.detachvol(old_vol_id, root_device)

        # Attach new volume
        aws.attachvol(new_vol_id, root_device)

        # Enable DeleteOnTermination
        aws.modifyec2(root_device, new_vol_id)

        # Start instance
        aws.ec2start()

        # Perform cleanup (optional)
        aws.cleanup(old_vol_id, snap_id)

        logger.info('Task completed!')
        sys.exit(0)
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    datetime_now = datetime.now().strftime('%Y%m%d-%H%M%S')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s - %(funcName)s - %(message)s',
        datefmt='%Y-%b-%d %I:%M:%S %p'
    )
    logger = logging.getLogger(__name__)

    ap = argparse.ArgumentParser(description='Automate root volume expanding on \
                                 Linux EBS-backed EC2 instance.')
    ap.add_argument('-r', '--region', help='AWS region is a geographical area \
                    (e.g., ap-southeast-1)',
                    required=True)
    ap.add_argument('-i', '--instance-id', help='Instance ID \
                    (e.g., i-1234567)', required=True)
    ap.add_argument('-s', '--size', help='Desired size for the new EBS volume \
                    in GiB (e.g., 10 GiB)', required=True)

    opts = ap.parse_args()
    region = opts.region
    instance_id = opts.instance_id
    new_size = int(opts.size)

    main()
