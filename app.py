import os
import json
import flask as fk
import pymongo as pm
from re import compile

#My imports
from methods.user import user
from methods.admin import admin
from methods.auth import auth


# Connect to mongodb
client = pm.MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notesDb = db["notes"]
usersDb = db["users"]


# Make app and add key
app = fk.Flask(__name__)
app.secret_key = "DigitalNotes_SecretKey"


# Bp's for user admin and authentication.
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(admin, url_prefix="/admin")
app.register_blueprint(user, url_prefix="/user")


# Insert a json file to the database functions
def load_jsons(users, users_coll):
	users_data = None
	notes_data = None
	with open(users, "r") as file:
		users_data = json.load(file)
	already_loaded = users_coll.find_one({"property":"admin"})
	if already_loaded is None:
		users_coll.insert_many(users_data)




# Home.
@app.route("/home", methods=["GET"])
def index():
    return "<h2>Welcome to DigitalNotes</h2>"


# Redirect to signIn.
@app.route("/")
@app.route("/signIn")
def goToSignIn():
    return fk.redirect(fk.url_for("auth.signIn"))


# Check for dbs existance and start app
if __name__ == "__main__":
    #Insert users and notes
    load_jsons("users.json", usersDb)

    # Start the app
    app.run(debug=True, host="0.0.0.0", port=5000)
