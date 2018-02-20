from flask import Flask, request
import MySQLdb
import json
import MySQLdb.cursors
from MySQLdb.converters import conversions

application = Flask(__name__, static_folder='.', static_url_path='')


@application.route('/')
def hello_world():
    return application.send_static_file("starter-copy.html")


# @app.route('/data',methods=['GET'])
# def query_data():
# boto3.set_stream_logger('boto3.resources', logging.INFO)


@application.route('/querydata', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        print(request.method)
        sql = request.form["sql"]
        print(sql)

        print(type(get_data_mysql(sql)), get_data_mysql(sql))

        return get_data_mysql(sql)

@application.route("/queryscore", methods=['POST'])
def query_score():
    if request.method == 'POST':
        count = request.form['count']
        sql = r"select id as image_id, CAST(score AS CHAR ) as score, cast(DATE_FORMAT(input_time,'%c-%e')  as char) input_date"+", CAST(input_time AS CHAR)input_time, bucket, image_name " \
              "from images ORDER BY input_time DESC limit %s" % count
        return get_data_mysql(sql)

@application.route("/querylabel", methods=['POST'])
def query_label():
    if request.method == 'POST':
        image_id = request.form['imageid']
        sql = "select label from image_labels where confidence > 80 and image_id = %s order by confidence desc" % image_id
        return get_data_mysql(sql)

@application.route("/querylabel2", methods=['POST'])
def query_label2():
    if request.method == 'POST':
        imageidlist = request.form['imageidlist']
        print(imageidlist)
        sql = "select image_id, label from image_labels where confidence > 60 and image_id in (%s) order by confidence desc" % imageidlist
        print(sql)
        return get_data_mysql(sql)

def get_data_mysql(sql):
    db = MySQLdb.connect(host="cc08705-us-east-1d.cshar3yujlmy.us-east-1.rds.amazonaws.com",
                         user="team2",
                         passwd="team2team2",
                         db="image_recognition",
                         charset='utf8',
                         cursorclass=MySQLdb.cursors.DictCursor)

    cur = db.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    json_data = json.dumps(result)
    db.close()

    return json_data


if __name__ == '__main__':
    application.run()
    # get_data_mysql("select id as image_id, CAST(score AS CHAR ) as score, CAST(input_time AS CHAR)input_time from images limit 3")
