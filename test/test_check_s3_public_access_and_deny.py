import unittest
import boto3 
from moto import mock_aws
from unittest.mock import patch

from checkS3PublicAccessAndDeny import bucket_is_public

DUMMY_BUCKET="my-little-non-existent-dummy"
DUMMY_POLICY="""
{
    "Version": "2012-10-17",
    "Id": "Policy1",
    "Statement": [
        {
            "Sid": "Stmt123456789",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::my-little-non-existent-dummy/*"
        }
    ]
}
"""
@mock_aws
class TestS3BucketAccess(unittest.TestCase):

    def create_bucket(self):
        s3 = boto3.resource('s3')
        bucket = s3.create_bucket(Bucket=DUMMY_BUCKET)
        return s3, bucket
 
    @patch('boto3.client')
    def testNewBucketIsNotPublic(self, client):
        s3, bucket = self.create_bucket()
        assert bucket_is_public(DUMMY_BUCKET) == False
        pass

    @patch('boto3.client')
    def testBucketWithDisabledAccessBlockAndEmptyPolicy(self, client):
        s3, bucket = self.create_bucket()
        
        bucket.meta.client.put_bucket_policy(
            Bucket=DUMMY_BUCKET,
            Policy="{}"
        )
        
        bucket.meta.client.put_public_access_block(
            Bucket=DUMMY_BUCKET,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            })
        
        assert bucket_is_public(DUMMY_BUCKET) == False
        pass
    
    @patch('boto3.client')
    def testBucketWithDisabledAccessBlock(self, client):
        s3, bucket = self.create_bucket()
        bucket.meta.client.put_public_access_block(
            Bucket=DUMMY_BUCKET,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            })
        
        # Bucket has no policies so it's false
        assert bucket_is_public(DUMMY_BUCKET) == False 
        pass

    @patch('boto3.client')
    def testBucketWithPublicPolicyButEnabledAccessBlocks(self, client):
        s3, bucket = self.create_bucket()

        bucket.meta.client.put_bucket_policy(
            Bucket=DUMMY_BUCKET,
            Policy=DUMMY_POLICY
        )
        
        assert bucket_is_public(DUMMY_BUCKET) == False

if __name__ == '__main__':
    unittest.main()