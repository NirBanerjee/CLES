from __future__ import print_function
import io
import os
import logging
import json
import subprocess
import boto3
import pymysql
import datetime

# The package will be accessible by importing clarifai:
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

#Initalizaing Clarifai Key
app = ClarifaiApp(api_key='###############')
api_call = 'https://api.clarifai.com/v1/tag'

#Initializaing Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Initializing S3 Client
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda', region_name='us-east-1')

#Import date times
from datetime import datetime

#Setup RDS Host details
rds_host  = "cc08705-us-east-1d.cshar3yujlmy.us-east-1.rds.amazonaws.com"
name = "team2"
password = "#################"
db_name = "image_recognition"

def get_tags(fname,key,conn,image_id):
    #bearer = os.environ('CLARIFAI_API_KEY')
    model = app.models.get('general-v1.3')
    image = ClImage(file_obj=open(fname, 'rb'))
    tags = model.predict([image])
    for concept in tags['outputs'][0]['data']['concepts']:

        cur = conn.cursor();
        logger.info("{} -> {}".format(concept['name'],concept['value']))
        lab_score = concept['value'] * 100;
        sql_command = 'insert into image_labels (`image_id`,`image_name`,`label`,`confidence`,`platform`) VALUES ({},"{}","{}",{},"Clarifai")'.format(image_id,key,concept['name'],lab_score)
        logger.info(sql_command)
        try:
            cur.execute(sql_command)
        except:
            logger.info("Cannot insert to DB")
        conn.commit()  

def handler(event,context):
    
    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except:
        logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")

    for record in event['Records']:
    	
    	#Get Bucket and key Name
    	bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        #Print bucket and key name to logger
        logger.info('bucket Name - [{}]'.format(bucket))
        logger.info('Image Name - [{}]'.format(key))

        #download path for image in local lambda environment
        download_path = '/tmp/{}'.format(key)
        logger.info('download path - [{}]'.format(download_path))

        #download the image
        s3_client.download_file(bucket, key, download_path)

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

        #Call the get tags method
        get_tags(download_path,key,conn,image_id)

        payloads={}

        id1 = int(image_id)
        payloads["image_id"] = id1

        result = lambda_client.invoke(FunctionName="scoreLambda",Payload=json.dumps(payloads))

        logger.info(result)


