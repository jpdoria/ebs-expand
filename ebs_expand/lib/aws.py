import sys
import boto3
from datetime import datetime


class Aws:
    def __init__(self, region):
        self.dt_now = datetime.now().strftime('%Y%m%d-%H%M%S')
        self.ec2 = boto3.client('ec2', region_name=region)

    def getrv(self, instance_id):
        print('Fetching root volume of {}...'.format(instance_id))

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

        print('AvailabilityZone: {}'.format(az))
        print('VolumeId: {}'.format(old_vol_id))
        print('Size: {} GiB'.format(old_size))
        print('VolumeType: {}'.format(vol_type))
        print('Iops: {}'.format(iops))
        print('RootDevice: {}'.format(root_device))

        return az, old_vol_id, old_size, vol_type, iops, root_device

    def ec2stop(self, instance_id):
        print('Stopping {}...'.format(instance_id))
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
            print('EC2Status: {}'.format(ec2_status))
            return ec2_status
        else:
            print('{} is still running. Please try again.'
                  .format(instance_id))
            sys.exit(1)

    def mksnap(self, old_vol_id, instance_id):
        print('Creating snapshot of {}...'.format(old_vol_id))

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
                    'Value': 'old-vol-snap-{0}-{1}'
                    .format(instance_id, self.dt_now)
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
            print('SnapshotId: {}'.format(snap_id))
            print('SnapshotStatus: {}'.format(snap_status))
            return snap_id
        else:
            print('{} is still incomplete. Please try again.'
                  .format(snap_id))
            sys.exit(1)

    def mkvol(self, snap_id, az, vol_type, iops, instance_id, new_size):
        print('Creating new volume using {}...'.format(snap_id))

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
                    'Value': 'new-vol-{0}-{1}'
                    .format(instance_id, self.dt_now)
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
            print('NewVolumeId: {}'.format(new_vol_id))
            print('NewVolumeStatus: {}'.format(new_vol_status))
            return new_vol_id
        else:
            print('{} is still unavailable. Please try again.'
                  .format(new_vol_id))
            sys.exit(1)

    def detachvol(self, old_vol_id, root_device, instance_id):
        print('Detaching old volume ({0}) from {1}...'.format(
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
                    'Value': 'old-vol-{0}-{1}'
                    .format(instance_id, self.dt_now)
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
            print('{} is now detached.'.format(old_vol_id))
        else:
            print('{} is still attached. Please try again.'
                  .format(old_vol_id))
            sys.exit(1)

    def attachvol(self, new_vol_id, root_device, instance_id):
        print('Attaching new volume ({0}) to {1}...'.format(
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
            print('{} is now attached.'.format(new_vol_id))
        else:
            print('{} is still unattached. Please try again.'
                  .format(new_vol_id))
            sys.exit(1)

    def modifyec2(self, root_device, new_vol_id, instance_id):
        print('Enabling DeleteOnTermination on {}...'
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
        print('DeleteOnTermination: True')

    def ec2start(self, instance_id):
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
            print('EC2Status: {}'.format(ec2_status))
        else:
            print('{} is still stopped. Please try again.'
                  .format(instance_id))
            sys.exit(1)

    def cleanup(self, old_vol_id, snap_id):
        while True:
            try:
                choice = str(input(
                    'Do you want to remove the old volume and snapshot? [Y/N] '
                    ).lower())
            except KeyboardInterrupt:
                print('\nGoodbye!')
                sys.exit(1)
            except ValueError as e:
                print('Please choose between Y and N.')
                sys.exit(1)
            else:
                if choice == 'y':
                    # Remove old volume
                    print('Removing old EBS volume ({})...'
                          .format(old_vol_id))
                    self.ec2.delete_volume(
                        VolumeId=old_vol_id
                    )
                    print('{} has been removed.'.format(old_vol_id))

                    # Remove snapshot
                    print('Removing snapshot ({0}) of {1}...'
                          .format(snap_id, old_vol_id))
                    self.ec2.delete_snapshot(
                        SnapshotId=snap_id
                    )
                    print('{} has been removed.'.format(snap_id))

                    break
                elif choice == 'n':
                    break
                else:
                    print('Please choose between Y and N.')
