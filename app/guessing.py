from flask import Flask, request, jsonify, render_template, redirect
import pymongo 
import random
import os, json, redis


# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

# app
app = Flask(__name__, template_folder='templates')
db = mongoClient.test
col = db["wordcollection"]
col2 = db["statisticcollection"]
gameStat={ 
    "question": ["_", "_", "_", "_"],
    "answer": ["_", "_", "_", "_"],
    "count": 0,
}

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',title="Guessing Game")

@app.route('/start', methods=["POST"])
def start():
    number_of_document = col.estimated_document_count()
    word = col.find_one({"doc_num":random.randint(1, number_of_document)})
    gameStat={ 
        "question": ["_", "_", "_", "_"],
        "answer": ["_", "_", "_", "_"],
        "count": 0,
    }
    for num in range(4):
        gameStat["question"][num] = word['letter'][num]
    col2.insert_one(gameStat)
    stat = col2.find_one(sort=[('_id', pymongo.DESCENDING )])
    return render_template('guess.html', stat=stat)

@app.route('/guess', methods=["GET" ,"POST"])
def guess():
    stat = col2.find_one(sort=[('_id', pymongo.DESCENDING )])
    if request.method == "POST":
        for i in range(4):
            if stat["question"][i] != stat["answer"][i]:
                while request.form['button'] != stat["question"][i]:
                    col2.update_one({"_id": stat["_id"]}, {"$inc": {"count": 1}})
                    return redirect("/guess")
                col2.update_one({"_id": stat["_id"]}, {"$inc": {"count": 1}})
                col2.update_one({"_id": stat["_id"]}, {"$set": {f"answer.{i}": stat["question"][i]}})
                return redirect("/guess")
    elif request.method == "GET":
        return render_template('guess.html',stat=stat)

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    app.run(host='0.0.0.0', port='3000', debug=True)
