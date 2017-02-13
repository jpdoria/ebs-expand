#!/usr/bin/env python

import sys
from ebs_expand.lib import Aws, set_args


def main():
    ap = set_args()
    opts = ap.parse_args()

    # Print help if no arguments are received
    if len(sys.argv) == 1:
        ap.print_help()
        sys.exit(1)

    region = opts.region
    instance_id = opts.instance_id
    new_size = int(opts.size)
    aws = Aws(region)

    print('Region: {}'.format(region))
    print('InstanceId: {}'.format(instance_id))
    print('NewSize: {} GiB'.format(new_size))

    # Get root volume
    az, old_vol_id, old_size, vol_type, iops, root_device = aws.getrv(
        instance_id)

    # Check current volume size
    if old_size == new_size:
        print('Please provide a new size greater than {} GiB.'
              .format(old_size))
        sys.exit(1)
    elif old_size > new_size:
        print('Old size ({}) > new size ({}). Goodbye!'
              .format(old_size, new_size))
        sys.exit(1)

    # Stop the instance
    ec2_status = aws.ec2stop(instance_id)

    # Create snapshot
    snap_id = aws.mksnap(old_vol_id, instance_id)

    # Create new volume
    new_vol_id = aws.mkvol(snap_id, az, vol_type, iops, instance_id, new_size)

    # Detach old volume
    aws.detachvol(old_vol_id, root_device, instance_id)

    # Attach new volume
    aws.attachvol(new_vol_id, root_device, instance_id)

    # Enable DeleteOnTermination
    aws.modifyec2(root_device, new_vol_id, instance_id)

    # Start instance
    aws.ec2start(instance_id)

    # Perform cleanup (optional)
    aws.cleanup(old_vol_id, snap_id)

    print('Task completed!')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nGoodbye!')
        sys.exit(1)
