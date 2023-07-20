import boto3
import os
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from system.exceptions import ApplicationError
from flask import current_app


PATH = os.getenv('STORAGE_PATH')
BUCKET_NAME = os.getenv('BUCKET_NAME')


class Storage:
    client = None
    resource = None

    def __init__(self, client, resource):
        self.client = client
        self.resource = resource

    def get_bucket(self, bucket_name):
        if not isinstance(bucket_name, str):
            raise ApplicationError('Name of bucket must be a string')
        return self.resource.Bucket(bucket_name)

    def generate_url_upload(self, bucket_name, key, mime_type):
        if not isinstance(bucket_name, str):
            raise ApplicationError('Name of bucket must be a string')
        if not isinstance(key, str):
            raise ApplicationError('Key must be a string')
        if not isinstance(mime_type, str):
            raise ApplicationError('Mime type must be a string')
        return self.client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
                'ContentType': mime_type,
                'ACL': 'private'
            },
            ExpiresIn=600
        )

    def generate_url_read(self, bucket_name, key):
        if not isinstance(bucket_name, str):
            raise ApplicationError('Name of bucket must be a string')
        if not isinstance(key, str):
            raise ApplicationError('Key must be a string')
        return self.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key,
            },
        )

    def get_object(self, bucket_name, key):
        if not isinstance(bucket_name, str):
            raise ApplicationError('Name of bucket must be a string')
        if not isinstance(key, str):
            raise ApplicationError('Key must be a string')
        return self.resource.Object(bucket_name, key)

    def get_size_object(self, bucket_name, key):
        try:
            return self.get_object(bucket_name, key).content_length
        except ClientError as e:
            current_app.logger.debug(e)
            return None

    def upload_file_obj(self, data, bucket_name, key, content_type='image/jpg'):
        if key[0] == '/':
            key = key[1:]
        try:
            return self.client.upload_fileobj(
                data, bucket_name, key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
        except S3UploadFailedError as e:
            current_app.logger.debug(e)
            raise ApplicationError('Can not upload to server')

    def upload_object(self, bucket_name, key, custom_path=None, content_type='image/jpg'):
        if custom_path is None:
            custom_path = self.make_custom_path(key)
        if key[0] == '/':
            key = key[1:]
        print('custom_path ', custom_path, key)
        try:
            return self.client.upload_file(
                custom_path, bucket_name, key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': content_type
                }
            )
        except S3UploadFailedError as e:
            current_app.logger.debug(e)
            raise ApplicationError('Can not upload to server')

    def download_object(self, bucket, key, custom_path=None):
        if custom_path is None:
            custom_path = self.make_custom_path(key)
        try:
            self.get_object(bucket, key).download_file(custom_path)
            return custom_path
        except ClientError as e:
            current_app.logger.debug(e)
            raise ApplicationError('Can not download file')

    def delete_object(self, bucket, key):
        obj = self.get_object(bucket, key)
        obj.delete()

    @staticmethod
    def make_custom_path(key):
        if not isinstance(key, str):
            raise ApplicationError('Key must be a string')
        return '{path}{key}'.format(path=PATH, key=key)


def make_storage(client=None, resource=None):
    if client is None:
        client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
                    region_name=os.getenv('S3_REGION')
                )
    if resource is None:
        resource = boto3.resource(
                    's3',
                    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                    aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
                    region_name=os.getenv('S3_REGION')
                )
    return Storage(client, resource)


storage = make_storage()