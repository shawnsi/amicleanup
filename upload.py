#!/usr/bin/env python

from __future__ import print_function

import sys
from tempfile import TemporaryFile
from zipfile import ZipFile

import boto3
from botocore.exceptions import ClientError

assume_role_policy_document = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}"""

policy_document = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Action": [
        "ec2:DeleteSnapshot",
        "ec2:DeregisterImage",
        "ec2:DescribeImageAttribute",
        "ec2:DescribeImages",
        "ec2:DescribeInstances",
        "ec2:DescribeSnapshotAttribute",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    }
  ]
}"""

function_name = 'amicleanup'
policy_name = 'LambdaAMICleanupPolicy'
role_name = 'LambdaAMICleanup'

def already_exists(e):
    return 'already exist' in str(e)

iam = boto3.resource('iam')

try:
    role = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=assume_role_policy_document
    )
except ClientError as e:
    if already_exists(e):
        role = iam.Role(role_name)

try:
    policy = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=policy_document
    )
except ClientError as e:
    if already_exists(e):
        policy = role.Policy(policy_name)
        policy.put(
            PolicyDocument=policy_document
        )

lambda_client = boto3.client('lambda', region_name='us-east-1')

with TemporaryFile() as f:
    with ZipFile(f, 'w') as z:
        z.write('amicleanup.py')

    f.seek(0)

    zipped_bytes = f.read()

    def create():
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python2.7',
            Role=role.arn,
            Handler='amicleanup.lambda_handler',
            Description='Cleanup orphaned AMIs',
            Timeout=60,
            MemorySize=256,
            Code={
                'ZipFile': zipped_bytes
            }
        )

    try:
        create()

    except ClientError as e:
        if already_exists(e):
            lambda_client.delete_function(
                FunctionName=function_name
            )
            create()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

