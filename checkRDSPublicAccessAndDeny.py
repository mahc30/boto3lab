#Check if the RDS Instances have public access, if that is the case remove it to avoid undesired access.
import boto3
from botocore.exceptions import ClientError

def rds_instance_is_public(db_instance_identifier):
    client = boto3.client('rds')
    
    try:
        response = client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
        db_instance = response['DBInstances'][0]
        return db_instance['PubliclyAccessible'] # type: ignore
    except ClientError as e:
        print(f"Error checking public access for RDS instance {db_instance_id}: {e}")
        return False

def rds_deny_public_access(db_instance_id):
    client = boto3.client('rds')
    try:
        response = client.modify_db_instance(
            DBInstanceIdentifier=db_instance_id,
            PubliclyAccessible=False,
            ApplyImmediately=True
        )
        print(f"Public access denied for RDS instance {db_instance_id}")
        return response
    except ClientError as e:
        print(f"Error denying public access for RDS instance {db_instance_id}: {e}")
        return None

db_instance_id = 'my-little-dummy-db-2'

is_public = rds_instance_is_public(db_instance_id)
print(f"RDS instance {db_instance_id} is {'publicly accessible' if is_public else 'not publicly accessible'}")
if(is_public): rds_deny_public_access(db_instance_id)