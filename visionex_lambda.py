from __future__ import print_function
import io
import os
import logging
import json
import subprocess
import boto3
import httplib2
import argparse
import os
import pymysql
import datetime

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

#Import date times
from datetime import datetime

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '#####################'
#Import logger directory
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Setup RDS Host details
rds_host  = "cc08705-us-east-1d.cshar3yujlmy.us-east-1.rds.amazonaws.com"
name = "team2"
password = "###########"
db_name = "image_recognition"

#import s3 client
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda', region_name='us-east-1')

#Import vision client
client = vision.Client()

def detect_label(file_name,key,conn,image_id):
    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
        image = client.image(content=content)

    labels = image.detect_labels()
    logger.info('Labels:')
    for label in labels:

        cur = conn.cursor();
        #logger.info('lablel - {} Score - {} '.format(label.description,label.score))
        lab_score = label.score * 100;
        sql_command = 'insert into image_labels (`image_id`,`image_name`,`label`,`confidence`,`platform`) VALUES ({},"{}","{}",{},"GCP")'.format(image_id,key,label.description,lab_score)
        logger.info(sql_command)
        try:
            cur.execute(sql_command)
        except:
            logger.info("Cannot insert to DB")
        conn.commit()   

def handler(event, context):

    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")

    # Instantiates a client
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}'.format(key)
        s3_client.download_file(bucket, key, download_path)
        #cmd = os.listdir('./')
        #logger.info(cmd)
        #Insert image details into database
        a = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(a)
        cur = conn.cursor();
        sql_command = 'insert into images (`image_name`,`input_time`,`user_id`,`bucket`) VALUES ("{}","{}",0,"{}")'.format(key,a,bucket)
        logger.info(sql_command)

        try:
            cur.execute(sql_command)
            image_id = cur.lastrowid
            logger.info(image_id)
        except:
            logger.info("Cannot insert to DB")

        conn.commit()

        detect_label(download_path,key,conn,image_id)

        payloads={}

        id1 = int(image_id)
        payloads["image_id"] = id1

        result = lambda_client.invoke(FunctionName="scoreLambda",Payload=json.dumps(payloads))

        logger.info(result)
        
