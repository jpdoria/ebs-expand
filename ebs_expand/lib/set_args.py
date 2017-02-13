import argparse


def set_args():
    ap = argparse.ArgumentParser(
        description='Automate root volume expanding on Linux EBS-backed ' +
                    'EC2 instance.'
    )

    ap.add_argument(
        '-r',
        '--region',
        help='AWS region is a geographical area (e.g., ap-southeast-1)',
        required=True
    )
    ap.add_argument(
        '-i',
        '--instance-id',
        help='Instance ID (e.g., i-1234567)',
        required=True
    )
    ap.add_argument(
        '-s',
        '--size',
        help='Desired size for the new EBS volume in GiB (e.g., 10 GiB)',
        required=True
    )
    ap.add_argument(
        '-v',
        '--version',
        help='Display current version of ebs_expand',
        action='version',
        version='%(prog)s (v1.0)'
    )

    return ap
