#!/usr/bin/python

from __future__ import print_function

from datetime import datetime, timedelta
import boto3

ec2 = boto3.resource('ec2')

def get_images_in_use():
    """
    Returns a list of image IDs in use by any EC2 instance.
    """
    amis = []

    for instance in ec2.instances.all():
        amis.append(instance.image_id)

    return amis


def get_orphaned_images():
    """
    Returns a list of image IDs meeting the following criteria:

    * Owned by self.
    * Not attached to any EC2 instance.
    * At least 30 days old.
    """
    in_use = get_images_in_use()

    orphaned = []

    for image in ec2.images.filter(Owners=['self']):
        if image.image_id not in in_use:
            creation_date = datetime.strptime(
                image.creation_date, "%Y-%m-%dT%H:%M:%S.000Z")

            if creation_date < (datetime.now() - timedelta(days=90)):
                print('Pruning %s created on %s' % (image, creation_date))
                orphaned.append(image.image_id)

    return orphaned


def lambda_handler(event, context):
    orphaned = get_orphaned_images()
    return orphaned
