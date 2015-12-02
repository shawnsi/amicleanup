#!/usr/bin/python

from __future__ import print_function

from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

def get_images_in_use(ec2):
    """
    Returns a list of image IDs in use by any EC2 instance.
    """
    amis = set()

    for instance in ec2.instances.all():
        amis.add(instance.image_id)

    return amis


def get_snapshots(ec2, image_ids):
    """
    Returns snapshots associated with a list of AMIs.
    """
    snapshots = []

    for snapshot in ec2.snapshots.all():
        if snapshot.description.startswith('Created by CreateImage'):
            for image_id in image_ids:
                if snapshot.description.find('for %s from' % image_id) > 0:
                    snapshots.append(snapshot.id)

    return snapshots


def get_orphaned_images(ec2, filters=None):
    """
    Returns a list of image IDs meeting the following criteria:

    * Owned by self.
    * Not attached to any EC2 instance.
    * At least 30 days old.
    """
    if not filters:
        filters = []

    in_use = get_images_in_use(ec2)

    orphaned = []

    for image in ec2.images.filter(Filters=filters, Owners=['self']):
        if image.image_id not in in_use:
            # Moto doesn't currenlty provide a creation date.  Setting a default
            # value here just for testing purposes.
            if image.creation_date is None:
                creation_date = datetime.fromtimestamp(0)
            else:
                creation_date = datetime.strptime(
                    image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")

            if creation_date < (datetime.now() - timedelta(days=30)):
                orphaned.append(image.image_id)

    return orphaned


def lambda_handler(event, context):
    """
    Cleanup orphaned AMIs and EBS snapshots.
    """

    if not 'DryRun' in event:
        event['DryRun'] = False

    if not 'Filters' in event:
        event['Filters'] = []

    ec2 = boto3.resource('ec2')

    orphaned = get_orphaned_images(ec2, filters=event['Filters'])
    snapshots = get_snapshots(ec2, orphaned)

    for orphan in orphaned:
        print('Deleting: %s' % orphan)
        try:
            ec2.Image(orphan).deregister(DryRun=event['DryRun'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'DryRunOperation':
                pass

    for snapshot in snapshots:
        print('Deleting: %s' % snapshot)
        try:
            ec2.Snapshot(snapshot).deregister(DryRun=event['DryRun'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'DryRunOperation':
                pass
