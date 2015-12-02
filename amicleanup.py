#!/usr/bin/python

from __future__ import print_function

from datetime import datetime, timedelta
import boto3

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


def get_orphaned_images(ec2):
    """
    Returns a list of image IDs meeting the following criteria:

    * Owned by self.
    * Not attached to any EC2 instance.
    * At least 30 days old.
    """
    in_use = get_images_in_use(ec2)

    orphaned = []

    for image in ec2.images.filter(Owners=['self']):
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
    Get all orphaned AMIs and EBS snapshots for cleanup.
    """
    ec2 = boto3.resource('ec2')

    orphaned = get_orphaned_images(ec2)
    snapshots = get_snapshots(ec2, orphaned)

    print(orphaned)
    print(snapshots)
