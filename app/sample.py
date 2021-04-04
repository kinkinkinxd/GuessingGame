from flask import Flask, request, jsonify, render_template, redirect
import pymongo 
import os, json, redis
import random

# App
app = Flask(__name__)

# connect to MongoDB
mongoClient = pymongo.MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',title="Guessing Game")

@app.route('/start', methods=["POST"])
def start():
    rand_list = ['A','B','C','D']
    gameStat={ 
        "question": ["_", "_", "_", "_"],
        "answer": ["_", "_", "_", "_"],
        "count": 0,
    }
    for num in range(4):
        gameStat["question"][num] = rand_list[random.randint(0,3)]
    db.test.insert_one(gameStat)
    stat = db.test.find_one(sort=[('_id', pymongo.DESCENDING )])
    return render_template('guess.html', stat=stat)

@app.route('/guess', methods=["GET" ,"POST"])
def guess():
    stat = db.test.find_one(sort=[('_id', pymongo.DESCENDING )])
    if request.method == "POST":
        for i in range(4):
            if stat["question"][i] != stat["answer"][i]:
                while request.form['button'] != stat["question"][i]:
                    db.test.update_one({"_id": stat["_id"]}, {"$inc": {"count": 1}})
                    return redirect("/guess")
                db.test.update_one({"_id": stat["_id"]}, {"$inc": {"count": 1}})
                db.test.update_one({"_id": stat["_id"]}, {"$set": {f"answer.{i}": stat["question"][i]}})
                return redirect("/guess")
    elif request.method == "GET":
        return render_template('guess.html',stat=stat)


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)