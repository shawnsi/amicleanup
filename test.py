from __future__ import print_function

import unittest
import os
import boto3
import amicleanup
from moto import mock_ec2


class Ec2SnapshotTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

        # Start moto environment
        self.mock = mock_ec2()
        self.mock.start()

        # Create mock unused images
        self.ec2 = boto3.resource('ec2')
        instances = self.ec2.create_instances(ImageId='ami-inuse', MinCount=5, MaxCount=5)

        # Mock images
        self.unused = [i.create_image(Name='unused') for i in instances]
        [i.terminate() for i in instances]

    def tearDown(self):
        # Cleanup moto environment
        self.mock.stop()

    def test_get_images_in_use(self):
        inuse = set(['ami-inuse'])

        # Test only terminated instances images are reflected
        self.assertEqual(amicleanup.get_images_in_use(self.ec2), inuse)

        # Run an instance with a mock image
        image = self.unused.pop()
        self.ec2.create_instances(ImageId=image.image_id, MinCount=1, MaxCount=1)
        inuse.add(image.image_id)
        self.assertEqual(amicleanup.get_images_in_use(self.ec2), inuse)

    def test_get_orphaned_images(self):
        # Test only terminated instances images are reflected
        self.assertItemsEqual(amicleanup.get_orphaned_images(self.ec2),
            [i.image_id for i in self.unused])

        # Run an instance with a mock image
        image = self.unused.pop()
        self.ec2.create_instances(ImageId=image.image_id, MinCount=1, MaxCount=1)
        self.assertItemsEqual(amicleanup.get_orphaned_images(self.ec2),
            [i.image_id for i in self.unused])
