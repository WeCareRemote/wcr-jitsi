import logging

import boto3

from records_handler import parse_dir

logger = logging.getLogger(__name__)


def handle_records(db, settings):
    logger.info("Video records handling started.")
    s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    parse_dir(db, s3_client, settings.S3_BUCKET, settings.RECORDS_DIR, settings.STORAGE_HOST)
    logger.info("Video records handling finished.")
