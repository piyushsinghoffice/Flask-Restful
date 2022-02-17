from flask import Flask, render_template, request, Response, redirect
from flask_sqlalchemy import SQLAlchemy
import pymongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

mongo = pymongo.MongoClient(host="localhost", port=27017)
db = mongo.sample_data

def response_message(message, error_code):
    print({"message": message, "status": error_code})
    return Response(
        response=json.dumps({"message": message}),
        status=error_code,
        mimetype="application/json",
    )

@app.route("/api/users/", methods=["GET"])
def main():
    args = request.args
    sort = str(args.get("sort"))
    if sort[0] == '-':
        sort = sort[1:]
        sort_by = -1
    else:
        sort_by = 1
        
    if bool(args):
        try:
            data = list(db.users.find({"$or":[
                                        {"first_name": {'$regex': f"^{args.get('name')}", "$options": "-i"}},
                                        {"last_name": {'$regex': f"^{args.get('name')}", "$options": "-i"}},
                                        {"company_name": {'$regex': f"^{args.get('company_name')}", "$options": "-i"}},
                                        {"city": {'$regex': f"^{args.get('city')}", "$options": "-i"}},
                                        {"zip": {'$regex': f"^{args.get('zip')}", "$options": "-i"}},
                                        {"state": {'$regex': f"^{args.get('state')}", "$options": "-i"}},
                                        {"age": {'$regex': f"^{args.get('age')}", "$options": "-i"}},
                                        ]
                                    }).sort(sort, sort_by).limit(int(args.get("limit", default=10)))
                        )

            for user in data:
                user["_id"] = str(user["_id"])
            response_message("found users", 200)

        except:
            response_message("cannot find users", 500)

        return render_template("index.html", userData=data)

    else:
        try:
            data = list(db.users.find().limit(10))
            for user in data:
                user["_id"] = str(user["_id"])
            response_message("All user data", 200)
            return render_template("index.html", userData=data)
        except:
            response_message("cannot find users", 500)

@app.route("/api/users/", methods=["POST"])
def post_form_data():
    try:
        # args = request.args
        # user = {"name": args.get("name"), "age": args.get("age")}
        user = {"id": request.form["id"],
                "first_name": request.form["first_name"],
                "last_name": request.form["last_name"],
                "company_name": request.form["company_name"],
                "age": request.form["age"],
                "city": request.form["city"],
                "state": request.form["state"],
                "zip": request.form["zip"],
                "email": request.form["email"],
                "web": request.form["web"]
                }
        dbResponse = db.users.insert_one(user)
        response_message("user created", 201)
        return redirect('/api/users/')

        
    except Exception as ex:
        print(ex)
        response_message("cannot create user", 500)
        return redirect('/api/users/')

@app.route("/api/users/<int:idx>")
def find_id(idx):
    try:
        data = list(db.users.find({"id": idx}))
        for user in data:
            user["_id"] = str(user["_id"])
        response_message("found user", 200)
    except Exception as ex:
        print(ex)
        response_message("cannot find id", 500)
    return render_template("index.html", userData=data)

@app.route("/api/users/<int:idx>", methods=["POST","PATCH"])
def update_user(idx):
    try:
        db.users.update_one({"id": idx}, {"$set":{
                                                    "first_name": request.form["update_first_name"],
                                                    "last_name": request.form["update_last_name"],
                                                    "age": request.form["update_age"],
                                                }})
        response_message("found user", 200)
    except Exception as ex:
        print(ex)
        response_message("cannot find id", 500)
    return redirect(f"/api/users/{idx}")

@app.route("/api/users/<int:idx>", methods=["POST","DELETE"])
def delete_user(idx):
    try:
        db.users.delete_one({"id": idx})
        response_message("Successfully deleted user", 200)
    except Exception as ex:
        print(ex)
        response_message("Sorry cannot delete user", 500)
    return redirect(f"/api/users/{idx}")

if __name__ == "__main__":
    app.run(port=80, debug=True)