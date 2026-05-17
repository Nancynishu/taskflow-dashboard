from flask import Flask, render_template, request, jsonify, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "nancy_secret_key"


# ==========================
# MONGODB CONNECTION
# ==========================

try:

    client = MongoClient(
        "mongodb://localhost:27017/"
    )

    db = client["task_manager"]

    users_collection = db["users"]
    tasks_collection = db["tasks"]

    print(
        "MongoDB Connected Successfully"
    )

except Exception as e:

    print(
        "MongoDB Error:",
        e
    )


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():

    return render_template(
        "login.html"
    )


# ==========================
# REGISTER
# ==========================

@app.route(
    "/register",
    methods=["POST"]
)
def register():

    try:

        data = request.json

        first_name = data.get(
            "firstName"
        )

        last_name = data.get(
            "lastName"
        )

        email = data.get(
            "email"
        )

        password = data.get(
            "password"
        )

        existing_user = (
            users_collection.find_one(
                {
                    "email": email
                }
            )
        )

        if existing_user:

            return jsonify({
                "message":
                "User already exists"
            }), 400

        users_collection.insert_one({

            "firstName":
            first_name,

            "lastName":
            last_name,

            "email":
            email,

            "password":
            password
        })

        return jsonify({
            "message":
            "Registration Successful"
        }), 200

    except Exception as e:

        print(
            "Register Error:",
            e
        )

        return jsonify({
            "message":
            "Registration Failed"
        }), 500


# ==========================
# LOGIN
# ==========================

@app.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        data = request.json

        first_name = data.get(
            "firstName"
        )

        last_name = data.get(
            "lastName"
        )

        email = data.get(
            "email"
        )

        password = data.get(
            "password"
        )

        user = (
            users_collection.find_one(
                {
                    "firstName":
                    first_name,

                    "lastName":
                    last_name,

                    "email":
                    email,

                    "password":
                    password
                }
            )
        )

        if user:

            session[
                "user_email"
            ] = email

            session[
                "first_name"
            ] = user.get(
                "firstName",
                "User"
            )

            session[
                "last_name"
            ] = user.get(
                "lastName",
                ""
            )

            return jsonify({

                "message":
                "Login Successful",

                "firstName":
                session[
                    "first_name"
                ],

                "greeting":
                "Welcome"

            }), 200

        return jsonify({

            "message":
            "Invalid Details"

        }), 401

    except Exception as e:

        print(
            "Login Error:",
            e
        )

        return jsonify({

            "message":
            "Database Connection Failed"

        }), 500


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if (
        "user_email"
        not in session
    ):
        return redirect("/")

    hour = (
        datetime.now().hour
    )

    if hour < 12:

        greeting = (
            "Good Morning ☀️"
        )

    elif hour < 17:

        greeting = (
            "Good Afternoon 🌤️"
        )

    else:

        greeting = (
            "Good Evening 🌙"
        )

    username = (
        session.get(
            "first_name",
            "User"
        )
    )

    return render_template(
        "index.html",
        username=username,
        greeting=greeting
    )


# ==========================
# GET TASKS
# ==========================

@app.route("/tasks")
def get_tasks():

    try:

        tasks = []

        for task in (
            tasks_collection.find()
        ):

            task["_id"] = str(
                task["_id"]
            )

            tasks.append(task)

        return jsonify(tasks)

    except Exception as e:

        print(
            "Task Fetch Error:",
            e
        )

        return jsonify([])


# ==========================
# ADD TASK
# ==========================

@app.route(
    "/add-task",
    methods=["POST"]
)
def add_task():

    try:

        data = request.json

        task = {

            "title":
            data.get(
                "title"
            ),

            "desc":
            data.get(
                "desc"
            ),

            "priority":
            data.get(
                "priority"
            ),

            "category":
            data.get(
                "category"
            ),

            "date":
            data.get(
                "date"
            ),

            "completed":
            False,

            "pinned":
            False
        }

        tasks_collection.insert_one(
            task
        )

        return jsonify({

            "message":
            "Task Added"

        })

    except Exception as e:

        print(
            "Add Task Error:",
            e
        )

        return jsonify({

            "message":
            "Task Add Failed"

        }), 500


# ==========================
# COMPLETE TASK
# ==========================

@app.route(
    "/complete-task/<id>",
    methods=["PUT"]
)
def complete_task(id):

    tasks_collection.update_one(
        {
            "_id":
            ObjectId(id)
        },
        {
            "$set":
            {
                "completed":
                True
            }
        }
    )

    return jsonify({

        "message":
        "Task Completed"

    })


# ==========================
# DELETE TASK
# ==========================

@app.route(
    "/delete-task/<id>",
    methods=["DELETE"]
)
def delete_task(id):

    tasks_collection.delete_one(
        {
            "_id":
            ObjectId(id)
        }
    )

    return jsonify({

        "message":
        "Task Deleted"

    })


# ==========================
# LOGOUT
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(debug=True)