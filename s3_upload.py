import requests
import boto3
import json
from aws_config import aws_config
import uuid

def bucket_check(s3_client):
    buckets = s3_client.list_buckets()['Buckets']
    if any('data-collection' in bucket['Name'] for bucket in buckets):
        pass
    else:
        s3_client.create_bucket(
            Bucket = f'data-collection-{str(uuid.uuid4())}',
            CreateBucketConfiguration = {
                'LocationConstraint': 'eu-west-2'
                }
        )

def folder_check(s3_client, check, *args):
    buckets = s3_client.list_buckets()['Buckets']
    for bucket in buckets:
        if 'data-collection' in bucket['Name']:
            data_collection_bucket = bucket['Name']
    if args:
        prefix = args[0]
        objects = s3_client.list_objects_v2(Bucket=data_collection_bucket, Prefix=prefix)
        if 'Contents' in objects.keys():
            contents = objects['Contents']
            if any (check in s3_object['Key'] for s3_object in contents):
                pass
            else:
                s3_client.put_object(Bucket=data_collection_bucket, Key=f'{prefix}{check}/')
        else:
            s3_client.put_object(Bucket=data_collection_bucket, Key=f'{prefix}/')
            s3_client.put_object(Bucket=data_collection_bucket, Key=f'{prefix}{check}/')
    else:
        objects = s3_client.list_objects_v2(Bucket=data_collection_bucket)
        if 'Contents' in objects.keys():
            contents = objects['Contents']
            if any (check in s3_object['Key'] for s3_object in contents):
                pass
            else:
                s3_client.put_object(Bucket=data_collection_bucket, Key=f'{check}/')
        else:
            s3_client.put_object(Bucket=data_collection_bucket, Key=f'{check}/')

def create_raw_data_file(s3_client,  s3_resource, key, attributes):
    buckets = s3_client.list_buckets()['Buckets']
    for bucket in buckets:
        if 'data-collection' in bucket['Name']:
            data_collection_bucket = bucket['Name']
    raw_data_file = s3_resource.Object(data_collection_bucket, key)
    raw_data_file.put(
        Body=(bytes(json.dumps(attributes).encode('UTF-8')))
    )

def create_image_file(s3_client,  s3_resource, key, content):
    buckets = s3_client.list_buckets()['Buckets']
    for bucket in buckets:
        if 'data-collection' in bucket['Name']:
            data_collection_bucket = bucket['Name']
    raw_data_file = s3_resource.Object(data_collection_bucket, key)
    raw_data_file.put(
        Body=content
    )

def save_s3(attributes, file_name):
    s3_resource = boto3.resource('s3', aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'], region_name=aws_config['region_name'])
    s3 = boto3.client('s3', aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'], region_name=aws_config['region_name'])
    bucket_check(s3)
    folder_check(s3, 'raw_data')
    file_folder = str(attributes['productID'])
    folder_check(s3, file_folder, 'raw_data/')
    create_raw_data_file(s3, s3_resource, f'raw_data/{file_folder}/{file_name}', attributes)
    image_file_name = file_folder + '.jpg'
    request_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
    image_request = requests.get(attributes['imgSrc'], headers=request_headers)
    create_image_file(s3, s3_resource, f'raw_data/{file_folder}/{image_file_name}', image_request.content)