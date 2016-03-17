#!/usr/bin/env python3

import boto3

KEY = ''
SECRET = ''
REGIONS = ['us-west-1', 'us-west-2']


def get_aws_connection(region):
    """
    Get a connection to an AWS region.
    """
    try:
        return boto3.client(
            'ec2',
            region_name=region,
            aws_access_key_id=KEY,
            aws_secret_access_key=SECRET
        )

    except boto3.exception.EC2ResponseError as e:
        print(e.message)


def get_security_groups():
    """
    Return a list of AWS security groups.
    """
    try:
        groups = conn.describe_security_groups()
        return groups['SecurityGroups']

    except boto.exception.EC2ResponseError as e:
        print(e.message)
        return []


def write_rule(fh, rule):
    """
    Parse and write the given rule to the file handle.
    """
    to_port = rule.get('ToPort', 'Any')
    fr_port = rule.get('FromPort', 'Any')
    protocol = rule.get('IpProtocol', 'Any')
    ranges = rule.get('IpRanges', [])

    if protocol == '-1':
        protocol = 'Any'

    if to_port == -1:
        to_port = 'Any'

    if fr_port == -1:
        fr_port = 'Any'

    ranges = [r['CidrIp'] for r in ranges]

    # Other security groups can be the source of the rule.
    if ranges == []:
        src_groups = rule.get('UserIdGroupPairs', [])
        ranges = [g['GroupId'] for g in src_groups]

    for range in ranges:
        fh.write('{0}{1}{2}-{3}\n'.format(range.ljust(20),
                                          protocol.ljust(6),
                                          fr_port,
                                          to_port))


def write_group(fh, name, desc, inrules, outrules):
    """
    Write the security group information to the file handle.
    """
    fh.write('\n')
    fh.write('{0}\n'.format(name))
    fh.write('{0}\n'.format('-' * len(name)))
    fh.write('Description: {0}\n'.format(desc))

    if inrules != []:
        fh.write('Ingress Rules:\n')
        for rule in inrules:
            write_rule(fh, rule)
        fh.write('\n')

    if outrules != []:
        fh.write('Egress Rules:\n')
        for rule in outrules:
            write_rule(fh, rule)
        fh.write('\n')


def write_groups(region, groups):
    """
    Write the security groups for the provided region to a file.
    """
    fn = 'ec2_security_groups_{0}.txt'.format(region)
    fh = open(fn, 'w')
    fh.write('{0}\n'.format(region.upper()))
    fh.write('{0}\n'.format('=' * len(region)))
    fh.write('Group Count: {0}\n'.format(len(groups)))
    for group in groups:
        name = group.get('GroupName', 'No Name')
        desc = group.get('Description', 'None')
        inrules = group.get('IpPermissions', [])
        outrules = group.get('IpPermissionsEgress', [])

        if (inrules != []) or (outrules != []):
            write_group(fh, name, desc, inrules, outrules)

    fh.close()


if __name__ == '__main__':
    for region in REGIONS:
        conn = get_aws_connection(region)
        groups = get_security_groups()
        write_groups(region, groups)
