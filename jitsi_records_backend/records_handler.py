"""
metadata.json example:
{"meeting_url":"https://dev.greytme.blackacornlabs.com/196_10","participants":[],"share":true}
"""
import logging
import os
import shutil
import sys
from datetime import datetime, timedelta
from os import getenv, walk
from os.path import join, isfile, split
from pathlib import Path

import boto3
from dotenv import load_dotenv

from app.crud.jitsi_record import CRUDJitsiRecord

logger = logging.getLogger(__name__)
load_dotenv()


class FlaggedDir():
    __date_frmt = '%Y-%m-%dT%H-%M-%S'
    __locked_str = '.locked'
    expire_min = 30

    def __init__(self, dirpath, expire_min=30):
        self.expire_min = expire_min
        self.dirpath = dirpath
        self.is_locked = False
        self.applied = None
        self.locked_file_name = None

        for _, __, filenames in walk(dirpath):
            for filename in filenames:
                if not filename.endswith(self.__locked_str):
                    continue
                self.is_locked = True
                self.applied = self.__parse_datetime(filename[1:-7])
                self.locked_file_name = filename
                break
            break
        # Remove lock if it is expired
        self.remove_expired_lock()

    @classmethod
    def __parse_datetime(self, datetime_str):
        return datetime.strptime(datetime_str, self.__date_frmt)

    @classmethod
    def __generate_datetime_str(self):
        return datetime.utcnow().strftime(self.__date_frmt)

    def generate_locked_file_name(self):
        return join(self.dirpath, '.{}{}'.format(self.__generate_datetime_str(), self.__locked_str))

    @property
    def is_expired(self):
        assert self.is_locked
        return datetime.utcnow() > self.applied + timedelta(minutes=self.expire_min)

    @property
    def locked_file_absolute_name(self):
        assert self.is_locked
        return join(self.dirpath, self.locked_file_name)

    def remove_expired_lock(self):
        if not (self.is_locked and self.is_expired):
            return
        self.remove_lock()

    def remove_lock(self):
        if not self.is_locked:
            return
        if isfile(self.locked_file_absolute_name):
            os.remove(self.locked_file_absolute_name)
        self.is_locked = False
        self.applied = None
        self.locked_file_name = None

    def lock(self):
        old_lock = self.locked_file_absolute_name if self.is_locked else None

        locked_file_name = self.generate_locked_file_name()
        Path(locked_file_name).touch()
        self.is_locked = True
        self.locked_file_name = split(locked_file_name)[1]
        self.applied = self.__parse_datetime(self.locked_file_name[1:-7])

        if old_lock and isfile(old_lock):
            os.remove(old_lock)


def iter_records(records_dir):
    for dirpath, dirnames, filenames in walk(records_dir):
        cur_dir = FlaggedDir(dirpath)
        if cur_dir.is_locked:
            continue

        for filename in filenames:
            if filename.endswith('.mp4'):
                # добавить временный файл, который будет говорить о том, что директория уже обрабатывается
                cur_dir.lock()
                yield dirpath, filename


def parse_dir(db, s3_client, bucket_name, records_dir, storage_host):
    for dirpath, filename in iter_records(records_dir):
        logger.info(f"Handling jitsi record file {filename}")
        # get info from filename
        # name example: 12_196_10_2022-01-15-13-53-29.mp4
        [conversation_id, advisor_id, student_id, start_time] = filename.split('_')
        start_time = start_time[:-4]
        start_time = datetime.strptime(start_time, '%Y-%m-%d-%H-%M-%S')
        # upload record
        target_path = f'video_records/{filename}'
        s3_client.upload_file(join(dirpath, filename), bucket_name, target_path)
        # form link
        url = f'{storage_host}/{target_path}'
        # insert video data to database
        CRUDJitsiRecord.create(db, obj_in=dict(
            conversation_id=conversation_id,
            advisor_id=advisor_id,
            student_id=student_id,
            start_time=start_time,
            url=url))
        # delete dirpath
        shutil.rmtree(dirpath, ignore_errors=True)


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(asctime)s %(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)

    access_key_id = getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = getenv('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = getenv('S3_BUCKET')
    RECORDS_DIR = getenv('RECORDS_DIR')
    storage_host = getenv('STORAGE_HOST')
    if not (access_key_id and secret_access_key and RECORDS_DIR and S3_BUCKET and storage_host):
        logger.error('AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, RECORDS_DIR, S3_BUCKET or STORAGE_HOST'
                     ' not specified.')
        sys.exit(0)

    logger.info("Script started.")
    if storage_host.endswith('/'):
        storage_host = storage_host[:-1]
    s3_client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    parse_dir(s3_client, S3_BUCKET, RECORDS_DIR, storage_host)
    logger.info("Finished.")
