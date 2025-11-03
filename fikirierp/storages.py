# fikirierp/storages.py
# (Create this new file)

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """
    Custom storage class for Cloudflare R2 (S3-compatible).
    This tells django-storages to use our custom settings.
    """
    location = 'media'
    file_overwrite = False
    
    # We don't set bucket_name, endpoint_url, etc. here
    # S3Boto3Storage will automatically read them from settings.py