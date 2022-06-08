import os
# from my_aws_config import my_aws_config

aws_config = {
    'aws_access_key_id': os.environ['aws_access_key_id'],
    'aws_secret_access_key': os.environ['aws_secret_access_key'],
    'region_name': os.environ['region_name'],
    'db_host_name': os.environ['db_host_name'],
    'db_name' : os.environ['db_name'],
    'port' : os.environ['port'],
    'username' : os.environ['username'],
    'password' : os.environ['password']
}

# aws_config = my_aws_config