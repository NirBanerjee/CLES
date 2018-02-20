from __future__ import print_function
import io
import os
import logging
import json
import subprocess
import boto3
import datetime
import pymysql
import random

#Initializaing Logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event,context):

    id = event['image_id']
    id = int(id)

    # constant vars
    NEUTRAL_SCORE = 60
    generalLabels = ["FOOD", "MEAL", "SUPPER", "DINNER", "LUNCH", "BOWL", "PLATE", "MEAL", "DISH", "CUP", "BREAKFAST", "NUTRITION",\
                     "BOTTLE", "FORK", "GLASS", "CUISINE", "DRINK", "COOKING", "TRADITIONAL", "RECIPY", "SEASONING", "APPETIZER", "FAST FOOD"]
    junk_food_list = ["BURGER", "HAMBURGER", "FRENCH FRIES", "FRIES", "CANDIES", "COLA", "COKE", "CHIPS", "POPCORN", \
                      "POTATO CHIPS", "SODA", "FRIED CHICKEN", "CHEESEBURGER", "FRIED FOOD", "PIZZA", "CHEESECAKE",\
                      "DONUTS", "DONUT", "ICE CREAM", "SODA", "COOKIES", "JUNK FOOD", "SWEETNESS"]
    healthy_food_list = ["FRUIT", "FRUITS", "VEGETABLES", "VEGETABLE", "SALAD", "VEGETARIAN", "MILK", "EGG"]

    # Connecting to Food DB
    conn = pymysql.connect(host='cc08705-us-east-1d.cshar3yujlmy.us-east-1.rds.amazonaws.com', port=3306, user='team2',
                           passwd='##########', db='Lists_of_Foods')
    cur = conn.cursor()

    # connect to database to get information of imaged waiting to be labeled
    connHost = pymysql.connect(host='cc08705-us-east-1d.cshar3yujlmy.us-east-1.rds.amazonaws.com', port=3306, user='team2', passwd='##########', db='image_recognition')
    curHost = connHost.cursor()

    logger.info("Scoring image " + str(id))

    # get labels for image
    sql_getfoodlabels = "SELECT label FROM image_labels WHERE image_id =" + str(id)
    curHost.execute(sql_getfoodlabels)
    foodLabels = curHost.fetchall()

    if len(foodLabels) != 0:
        labelTemp = []
        for temp in range(0,len(foodLabels)):
            labelTemp.append(str(foodLabels[temp][0]))
        foodLabels = labelTemp

        # List of labels in str
        logger.info(foodLabels)

        # get according confidences for image "foodnumber"
        sql_getfoodconfidences = "SELECT confidence FROM image_labels WHERE image_id =" + str(id)
        curHost.execute(sql_getfoodconfidences)
        foodConfidences = curHost.fetchall()

        #printing confidences
        logger.info(foodConfidences)

        confidenceTemp = []
        for temp in range(0,len(foodConfidences)):
            confidenceTemp.append(int(foodConfidences[temp][0]))
        foodConfidences = confidenceTemp # List of confidences in int
        logger.info(foodConfidences)

        #calculate the overall score for all labels of one image
        scores = []
        confidences = [] # the modified list after eliminate general labels
        ########change all names for one image into upper case
        foodLabelsTemp = []
        for foodLabel in foodLabels:
            foodLabelsTemp.append(foodLabel.upper())
        foodLabels = foodLabelsTemp

        ##################set count_junk_food and count_healthy_food
        count_junk_food = 0
        count_healthy_food = 0

        for labelnumber in range(0,len(foodLabels)):
            name = foodLabels[labelnumber]
            logger.info("Label name: " + name)
            confidence = foodConfidences[labelnumber]
            #logger.info(confidence)

            if name not in generalLabels:
                nameModified = name
                logger.info(nameModified)

                # start search for entries in database, search if there are matches start with "nameModified"
                sql_1 = "SELECT Food_Score FROM Food_Score WHERE Shrt_Desc like \'" + nameModified + "%\'"
                cur.execute(sql_1)
                ret = cur.fetchall()

                # if can not find a match, then search if there are matched include "nameModified"
                if len(ret) == 0:
                    confidence = confidence * 0.3
                    sql_2 = "SELECT Food_Score FROM Food_Score WHERE Shrt_Desc like \'%" + nameModified + "%\'"
                    cur.execute(sql_2)
                    ret = cur.fetchall()

                 # if previous two step can find at least one match, continue to calculate a final score for this label, if no matches found, then ignore this label
                if len(ret) != 0:
                    scoreArray = ret
                    scoreArrayTemp =[]
                    for temp in range(0,len(scoreArray)):
                        scoreArrayTemp.append(int(scoreArray[temp][0]))

                    scoreArray = scoreArrayTemp
                    logger.info(scoreArray)
                    logger.info(str(len(scoreArray)) + " matched entries found in scoring database")
                    logger.info("This label has a score of " + str(int(int(sum(scoreArray))/int(len(scoreArray)))))
                    logger.info("with a confidence of " + str(confidence) + "%")

                    scores.append(int(sum(scoreArray))/int(len(scoreArray))*confidence/100)
                    confidences.append(confidence)

                if name in healthy_food_list:
                    count_healthy_food = count_healthy_food +1
                    logger.info("This is a healthy food!")

                if name in junk_food_list:
                    count_junk_food = count_junk_food +1
                    logger.info("This is a junk food!")

        # if all labels for an image can not get even one score, then return a nertual score = 50
        if len(scores) == 0:
            score = random.randint(NEUTRAL_SCORE-5, NEUTRAL_SCORE)

        ##################if count_junk_food or count_healthy_food are not all zero or all bigger than zero, then give a fixed score
        elif count_junk_food > 0 and count_healthy_food == 0:
            score = random.randint(35, 55)

        elif count_healthy_food >0 and count_junk_food == 0:
            score = random.randint(75, 95)

        # else the score for image equals to a weighted average of all labels' scores
        else:
            score = int(sum(scores)/(sum(confidences)/100))

    else:
        score = random.randint(NEUTRAL_SCORE-5, NEUTRAL_SCORE)

    # write score into database where id = id
    logger.info("Image: " + str(id) + "   Final Score: " + str(score))
    sql_write = "UPDATE images SET score = " + str(score) + " WHERE id = " + str(id)
    curHost.execute(sql_write)

    #close connections with database
    conn.commit()
    cur.close()
    conn.close()
    connHost.commit()
    curHost.close()
    connHost.close()

    return "Score added successfully"