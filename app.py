from flask import Flask, request, jsonify, render_template, redirect, session
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- MONGO ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["todo_db"]

users_collection = db["users"]
tasks_collection = db["tasks"]

# ---------------- HOME ----------------
@app.route("/")
def home():
    return redirect("/login-page")

# ---------------- LOGIN PAGE ----------------
@app.route("/login-page")
def login_page():
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login-page")
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if users_collection.find_one({"email": data.get("email")}):
        return jsonify({"message": "User already exists"}), 400

    users_collection.insert_one({
        "email": data.get("email"),
        "password": data.get("password")
    })

    return jsonify({"message": "Registered successfully"})

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = users_collection.find_one({
        "email": data.get("email"),
        "password": data.get("password")
    })

    if user:
        session["user"] = data.get("email")
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login-page")

# ---------------- ADD TASK ----------------
@app.route("/add-task", methods=["POST"])
def add_task():
    if "user" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.json

    task = {
        "title": data.get("title"),
        "desc": data.get("desc", ""),                 # NEW
        "priority": data.get("priority", "low"),
        "category": data.get("category", "work"),     # NEW
        "date": data.get("date", ""),                 # NEW
        "completed": False,
        "pinned": False,                             # NEW
        "user": session["user"]
    }

    result = tasks_collection.insert_one(task)

    return jsonify({
        "id": str(result.inserted_id),
        "message": "Task added"
    })

# ---------------- GET TASKS ----------------
@app.route("/tasks", methods=["GET"])
def get_tasks():
    if "user" not in session:
        return jsonify([])

    tasks = []

    for t in tasks_collection.find({"user": session["user"]}):
        tasks.append({
            "id": str(t["_id"]),
            "title": t.get("title", ""),
            "desc": t.get("desc", ""),
            "priority": t.get("priority", "low"),
            "category": t.get("category", "work"),
            "date": t.get("date", ""),
            "completed": t.get("completed", False),
            "pinned": t.get("pinned", False)
        })

    return jsonify(tasks)

# ---------------- DELETE ----------------
@app.route("/delete-task/<id>", methods=["DELETE"])
def delete_task(id):
    try:
        tasks_collection.delete_one({"_id": ObjectId(id)})
        return jsonify({"message": "Deleted"})
    except:
        return jsonify({"message": "Invalid ID"}), 400

# ---------------- COMPLETE (TOGGLE) ----------------
@app.route("/complete-task/<id>", methods=["PUT"])
def complete_task(id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(id)})

        if not task:
            return jsonify({"message": "Task not found"}), 404

        tasks_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"completed": not task.get("completed", False)}}
        )

        return jsonify({"message": "Updated"})

    except:
        return jsonify({"message": "Invalid ID"}), 400

# ---------------- PIN TASK ----------------
@app.route("/pin-task/<id>", methods=["PUT"])
def pin_task(id):
    try:
        task = tasks_collection.find_one({"_id": ObjectId(id)})

        tasks_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"pinned": not task.get("pinned", False)}}
        )

        return jsonify({"message": "Pinned"})

    except:
        return jsonify({"message": "Error"}), 400

# ---------------- CLEAR COMPLETED ----------------
@app.route("/clear-done", methods=["DELETE"])
def clear_done():
    tasks_collection.delete_many({
        "user": session["user"],
        "completed": True
    })
    return jsonify({"message": "Cleared"})

# ---------------- STATS ----------------
@app.route("/stats", methods=["GET"])
def stats():
    if "user" not in session:
        return jsonify({})

    total = tasks_collection.count_documents({"user": session["user"]})
    completed = tasks_collection.count_documents({
        "user": session["user"],
        "completed": True
    })

    pending = total - completed

    return jsonify({
        "total": total,
        "completed": completed,
        "pending": pending
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)