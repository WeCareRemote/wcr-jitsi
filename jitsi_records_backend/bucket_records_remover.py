import logging
import sys
from datetime import datetime, timedelta
from os import getenv

import boto3
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

logger = logging.getLogger(__name__)
load_dotenv()


def db_unset_urls(host, database, user, password, filename):
    [conversation_id, advisor_id, student_id, start_time] = filename.split('/')[1].split('_')
    start_time = start_time[:-4]
    start_time = datetime.strptime(start_time, '%Y-%m-%d-%H-%M-%S')
    try:
        with mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database) as connection:
            executor = connection.cursor()
            sql = ('UPDATE jitsi_records '
                   'SET url = NULL, delete_reason = "expired" '
                   'WHERE conversation_id = %s '
                   'AND advisor_id = %s '
                   'AND student_id = %s '
                   'AND start_time = %s ')
            executor.execute(sql, (conversation_id, advisor_id, student_id, start_time))
            connection.commit()
            logger.info(f"{executor.rowcount} db records unlinked with bucket.")
    except Error as exc:
        logger.error(str(exc))
        sys.exit(1)


def main(*args, in_cloud=True, **kwargs):
    S3_BUCKET = getenv('S3_BUCKET')
    DB_HOST = getenv('DB_HOST')
    DB_DATABASE = getenv('DB_DATABASE')
    DB_USERNAME = getenv('DB_USERNAME')
    DB_PASSWORD = getenv('DB_PASSWORD')
    env_vars = [S3_BUCKET, DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD]
    if not in_cloud:
        access_key_id = getenv('AWS_ACCESS_KEY_ID')
        secret_access_key = getenv('AWS_SECRET_ACCESS_KEY')
        env_vars.extend([access_key_id, secret_access_key])
    if not all(env_vars):
        logger.error('Some of environment variables not specified.')
        sys.exit(1)

    EXPIRE_DAYS = 30

    logger.info("Script started.")
    logger.info(f"Expiration time is {EXPIRE_DAYS} days.")

    kw_args = {} if in_cloud else {'aws_access_key_id': access_key_id, 'aws_secret_access_key': secret_access_key}
    s3 = boto3.resource('s3', **kw_args)
    bucket = s3.Bucket(S3_BUCKET)
    to_delete = set()
    for my_bucket_object in bucket.objects.filter(Prefix='video_records/', Delimiter='/'):
        start_time = my_bucket_object.key.split('_')[-1][:-4]
        start_time = datetime.strptime(start_time, '%Y-%m-%d-%H-%M-%S')
        if datetime.utcnow() < start_time + timedelta(days=EXPIRE_DAYS):
            continue
        to_delete.add(my_bucket_object.key)

    if not to_delete:
        logger.info("Finished.")
        return

    # Если есть, что удалять
    to_delete_str = "\n".join(to_delete)
    logger.info(f'Next files will be deleted from bucket:\n{to_delete_str}')
    for filename in to_delete:
        db_unset_urls(host=DB_HOST, database=DB_DATABASE, user=DB_USERNAME, password=DB_PASSWORD, filename=filename)
    response = bucket.delete_objects(Delete={'Objects': [{'Key': filename} for filename in to_delete]})
    if response.get('Deleted'):
        deleted = {file['Key'] for file in response['Deleted']}
        if not (to_delete - deleted):
            logger.info('All files were deleted successfully.')
        else:
            not_delted_str = '\n'.join(to_delete - deleted)
            logger.info(f'Seems like something goes wrong. These files are not deleted:\n{not_delted_str}')
    else:
        logger.info(f'Seems like something goes wrong. Full bucket response: {response}')

    logger.info("Finished.")


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s %(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)

    main()
