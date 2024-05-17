# Check if the s3 buckets have public access, if that is the case remove it to avoid undesired access.
# Test bucket is currently public and has one object https://my-little-dummy.s3.amazonaws.com/dfp9sfo-5c1d0068-dd70-4e2b-9b9f-565d987ea047.jpg

import boto3
from botocore.exceptions import ClientError

LOG=True
BUCKETS_TO_CHECK = ["my-little-dummy"]

def log(string):
    if(LOG): print(string)

def bucket_is_public(bucket):
    client = boto3.client('s3')
    log(f"Checking {bucket}")
    is_public = False
        
    try:
        log("Checking Access Block Configuration:")
        access_block_config = client.get_public_access_block(Bucket=bucket)
        if(access_block_config['PublicAccessBlockConfiguration']['BlockPublicAcls'] == False or access_block_config['PublicAccessBlockConfiguration']['BlockPublicPolicy'] == False): #type: ignore
            log(f"\tMight Allow Public Access because of Public Access Block Configuration")
            is_public = True
        else:
            log(f"\tAccess Block is Configured to block all public access")
            return False
    except ClientError as e:
        log(f"\tAllows Public Access: No ({e})")
    
    try:
        log("Checking Policies:")
        policy_status = client.get_bucket_policy_status(Bucket=bucket)
        print(policy_status['PolicyStatus'])
        if('PolicyStatus' in policy_status and policy_status['PolicyStatus'].get('IsPublic', False)):
            log(f"\tAllows Public Access because of Policies")
            is_public = True
    except ClientError as e:
        log(f"\tAllows Public Access: No ({e})")
        return False
    return is_public

def s3_deny_public_access(bucket):
    client = boto3.client('s3')
    log(f"Denying: {bucket}")
    
    client.put_public_access_block(
        Bucket=bucket,            
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        })

def run():
    public_buckets = []
    
    for bucket in BUCKETS_TO_CHECK:
        if(bucket_is_public(bucket)):
            public_buckets.append(bucket)
    
    for bucket in public_buckets:
        s3_deny_public_access(bucket)

if __name__ == '__main__':
    run()