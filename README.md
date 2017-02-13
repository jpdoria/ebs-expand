# About

Expand root volume of EBS-backed Linux EC2.

# Dependencies

- [Python 3.6](https://www.python.org/downloads/)
- [Pip](https://pypi.python.org/pypi/pip)
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
                "ec2:ModifyInstanceAttribute",
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

# Installation

```
pip install ebs-expand
```

# Usage

```
# ebs_expand --help
usage: ebs_expand [-h] -r REGION -i INSTANCE_ID -s SIZE [-v]

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
  -v, --version         Display current version of ebs_expand
#
```

# Example

```
# ebs_expand -r ap-southeast-1 -i i-2f0b2aa1 -s 10
Region: ap-southeast-1
InstanceId: i-2f0b2aa1
NewSize: 10 GiB
Fetching root volume of i-2f0b2aa1...
AvailabilityZone: ap-southeast-1a
VolumeId: vol-60910ca6
Size: 8 GiB
VolumeType: gp2
Iops: 100
RootDevice: /dev/sda1
Stopping i-2f0b2aa1...
EC2Status: stopped
Creating snapshot of vol-60910ca6...
SnapshotId: snap-0aa2114b13d5a38f4
SnapshotStatus: completed
Creating new volume using snap-0aa2114b13d5a38f4...
NewVolumeId: vol-0fd09c171ebdac8f5
NewVolumeStatus: available
Detaching old volume (vol-60910ca6) from i-2f0b2aa1...
vol-60910ca6 is now detached.
Attaching new volume (vol-0fd09c171ebdac8f5) to i-2f0b2aa1...
vol-0fd09c171ebdac8f5 is now attached.
Enabling DeleteOnTermination on vol-0fd09c171ebdac8f5...
DeleteOnTermination: True
EC2Status: running
Do you want to remove the old volume and snapshot? [Y/N] Y
Removing old EBS volume (vol-60910ca6)...
vol-60910ca6 has been removed.
Removing snapshot (snap-0aa2114b13d5a38f4) of vol-60910ca6...
snap-0aa2114b13d5a38f4 has been removed.
Task completed!
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