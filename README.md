# About

[![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-electricity.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/kinda-sfw.svg)](http://forthebadge.com)

Post Git commit message on user's Facebook timeline.

# Dependencies

- [Python 3.6](https://www.python.org/downloads/)
- [Virtualenv](https://virtualenv.pypa.io/en/stable/installation/)
- AWS Account - please check this [link](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-quick-configuration) for configuration using [AWS CLI](https://aws.amazon.com/cli/)
- IAM Policy - please make sure you are allowed to execute the actions listed below

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1234567890123",
            "Effect": "Allow",
            "Action": [
                "ec2:AttachVolume",
                "ec2:CreateSnapshot",
                "ec2:CreateTags",
                "ec2:CreateVolume",
                "ec2:DescribeInstances",
                "ec2:DescribeSnapshots",
                "ec2:DescribeVolumes",
                "ec2:DetachVolume",
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

# Setup

- Go to any directory in your local machine

```
cd ~
```

- Clone this repository

```
git clone https://github.com/jpdoria/ebs-expand.git
```

- Change directory to `ebs-expand`

```
cd ebs-expand
```

- Install `virtualenv`

```
pip install virtualenv
```

- Create a virtual environment

```
virtualenv -p python3.6 env
```

- Activate the virtual environment

```
source env/bin/activate
```

or

```
. env/bin/activate
```

- Install required modules

```
pip install -r requirements.txt
```

# Usage

```
# python ebs-expand.py
usage: ebs-expand.py [-h] -r REGION -i INSTANCE_ID -s SIZE
ebs-expand.py: error: the following arguments are required: -r/--region, -i/--instance-id, -s/--size
# python ebs-expand.py -h
usage: ebs-expand.py [-h] -r REGION -i INSTANCE_ID -s SIZE

Automate root volume expanding on Linux EBS-backed EC2 instance.

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        AWS region is a geographical area (e.g., ap-
                        southeast-1)
  -i INSTANCE_ID, --instance-id INSTANCE_ID
                        Instance ID (e.g., i-1234567)
  -s SIZE, --size SIZE  Desired size for the new EBS volume in GiB (e.g., 10
                        GiB)
#
```

# Example

```
# python ebs-expand.py -r ap-southeast-1 -i i-9652b917 -s 10
2017-Jan-26 09:14:04 AM | INFO - load - Found credentials in shared credentials file: ~/.aws/credentials
2017-Jan-26 09:14:05 AM | INFO - main - Region: ap-southeast-1
2017-Jan-26 09:14:05 AM | INFO - main - InstanceId: i-9652b917
2017-Jan-26 09:14:05 AM | INFO - main - NewSize: 10 GiB
2017-Jan-26 09:14:05 AM | INFO - getrv - Fetching root volume of i-9652b917...
2017-Jan-26 09:14:05 AM | INFO - _new_conn - Starting new HTTPS connection (1): ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:14:05 AM | INFO - getrv - AvailabilityZone: ap-southeast-1a
2017-Jan-26 09:14:05 AM | INFO - getrv - VolumeId: vol-07870a991d3510f3d
2017-Jan-26 09:14:05 AM | INFO - getrv - Size: 8 GiB
2017-Jan-26 09:14:05 AM | INFO - getrv - VolumeType: gp2
2017-Jan-26 09:14:05 AM | INFO - getrv - Iops: 100
2017-Jan-26 09:14:05 AM | INFO - getrv - RootDevice: /dev/xvda
2017-Jan-26 09:14:05 AM | INFO - ec2stop - Stopping i-9652b917...
2017-Jan-26 09:14:20 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:14:36 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:14:51 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:15:08 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:15:09 AM | INFO - ec2stop - EC2Status: stopped
2017-Jan-26 09:15:09 AM | INFO - mksnap - Creating snapshot of vol-07870a991d3510f3d...
2017-Jan-26 09:15:25 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:15:40 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:15:55 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:15:56 AM | INFO - mksnap - SnapshotId: snap-0864134678cd3e3b6
2017-Jan-26 09:15:56 AM | INFO - mksnap - SnapshotStatus: completed
2017-Jan-26 09:15:56 AM | INFO - mkvol - Creating new volume using snap-0864134678cd3e3b6...
2017-Jan-26 09:16:11 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:16:12 AM | INFO - mkvol - NewVolumeId: vol-09d5c65852467cc83
2017-Jan-26 09:16:12 AM | INFO - mkvol - NewVolumeStatus: available
2017-Jan-26 09:16:12 AM | INFO - detachvol - Detaching old volume (vol-07870a991d3510f3d) from i-9652b917...
2017-Jan-26 09:16:28 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:16:28 AM | INFO - detachvol - vol-07870a991d3510f3d is now detached.
2017-Jan-26 09:16:28 AM | INFO - attachvol - Attaching new volume (vol-09d5c65852467cc83) to i-9652b917...
2017-Jan-26 09:16:29 AM | INFO - attachvol - vol-09d5c65852467cc83 is now attached.
2017-Jan-26 09:16:29 AM | INFO - modifyec2 - Enabling DeleteOnTermination on vol-09d5c65852467cc83...
2017-Jan-26 09:16:29 AM | INFO - modifyec2 - DeleteOnTermination: True
2017-Jan-26 09:16:44 AM | INFO - _get_conn - Resetting dropped connection: ec2.ap-southeast-1.amazonaws.com
2017-Jan-26 09:16:45 AM | INFO - ec2start - EC2Status: running
2017-Jan-26 09:16:45 AM | INFO - main - Task completed!
#
```

# Contributing

This project is still young and there are things that need to be done. If you have ideas that would improve this, feel free to contribute!

# License

MIT License

Copyright (c) 2017 John Paul P. Doria

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.