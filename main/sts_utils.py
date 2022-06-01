# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Modified by John Briggs
# See https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/python/example_code/sts/sts_temporary_credentials#code-examples
# for original code and unit tests
"""
Purpose

Shows how to construct a URL that gives federated users direct access to the
AWS Management Console.
"""

import datetime
import json
import sys
import time
import urllib.parse
import boto3
import requests

def time_millis():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)
def progress_bar(seconds):
    """Shows a simple progress bar in the command window."""
    for _ in range(seconds):
        time.sleep(1)
        print('.', end='')
        sys.stdout.flush()
    print()


def unique_name(base_name):
    return f'sts-{base_name}-{time_millis()}'
def unique_testing_name(base_name):
    return f'sts-testing-{base_name}-{time_millis()}'

def setup(iam_resource,name_function):
    """
    Creates a role that can be assumed by the current user.
    Attaches a policy that allows only Amazon S3 read-only access.

    :param iam_resource: A Boto3 AWS Identity and Access Management (IAM) instance
                         that has the permission to create a role.
    :return: The newly created role.
    """
    role = iam_resource.create_role(
        RoleName=name_function('role'), MaxSessionDuration=43200,
        AssumeRolePolicyDocument=json.dumps({
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {'AWS': iam_resource.CurrentUser().arn},
                    'Action': ['sts:AssumeRole', 'sts:TagSession']
                }
            ]
        })
    )
    #role.attach_policy(PolicyArn='arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess')
    role.attach_policy(PolicyArn='arn:aws:iam::739988523141:policy/access-same-project-team')
    print(f"Created role {role.name}.")

    print("Give AWS time to propagate these new resources and connections.", end='')
    progress_bar(10)

    return role


def generate_credentials(assume_role_arn, session_name, sts_client, group_name, bucket_name):
    """
    Constructs a URL that gives federated users direct access to the AWS Management
    Console.

    1. Acquires temporary credentials from AWS Security Token Service (AWS STS) that
       can be used to assume a role with limited permissions.
    2. Uses the temporary credentials to request a sign-in token from the
       AWS federation endpoint.
    3. Builds a URL that can be used in a browser to navigate to the AWS federation
       endpoint, includes the sign-in token for authentication, and redirects to
       the AWS Management Console with permissions defined by the role that was
       specified in step 1.

    :param assume_role_arn: The role that specifies the permissions that are granted.
                            The current user must have permission to assume the role.
    :param session_name: The name for the STS session.
    :param issuer: The organization that issues the URL.
    :param sts_client: A Boto3 STS instance that can assume the role.
    :param group_name: group name
    :param bucket_name: bucket name
    :return: The federated URL. 
    """
    response = sts_client.assume_role(
        RoleArn=assume_role_arn, RoleSessionName=session_name, DurationSeconds=43200, Tags=[{"Key": "access-bucket","Value": bucket_name},{"Key": "access-group","Value": group_name}])
    return response['Credentials']


def teardown(role):
    """
    Removes all resources created during setup.

    :param role: The demo role.
    """
    for attached in role.attached_policies.all():
        role.detach_policy(PolicyArn=attached.arn)
        print(f"Detached {attached.policy_name}.")
    role.delete()
    print(f"Deleted {role.name}.")