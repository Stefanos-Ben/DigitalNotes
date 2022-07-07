"""
This is a set of methods that will be used to implement the admintistrator's
utilites for Digital Notes.
"""

import flask as fk
import pymongo as pm
import re
from datetime import date


# Admin bp.
admin = fk.Blueprint("admin", __name__, static_folder="static", template_folder="templates")


# Initialize client
client = pm.MongoClient("mongodb://mongodb:27017/")
db = client["DigitalNotes"]
notesDb = db["notes"]
usersDb = db["users"]


# Admin's home page.
@admin.route("/")
@admin.route("/adminHP", methods=["GET"])
def adminHP():
    return fk.render_template("adminHP.html", usName = fk.session["username"])


# Create admin.
@admin.route("/")
@admin.route("/createAdmin", methods=["GET","POST"])
def createAdmin():
    if fk.request.method == "GET":
        return fk.render_template("adminCreate.html")
    else:
        # Check if the user already exists.
        adminEmail = fk.request.form["email"]
        adminUsName = fk.request.form["username"]
        adminFname = fk.request.form["fullname"]
        existsEmail = usersDb.find_one({"email": adminEmail})
        existsName = usersDb.find_one({"username": adminUsName})
        if (existsEmail is None) and (existsName is None):
            # If no user exists create the new admin and return to home page
            new_admin = {"username": adminUsName, "password": "otpword", "email": adminEmail, "fullname": adminFname, "property": "admin"}
            usersDb.insert_one(new_admin)
            fk.flash("New admin successfully created!")
            return fk.redirect(fk.url_for("admin.adminHP"))
        elif existsName is None:
            # Redirect to the same page.
            fk.flash("This e-mail is already being used.")
            return fk.redirect(fk.url_for("admin.createAdmin"))
        else:
            fk.flash("This username has been taken.")
            return fk.redirect(fk.url_for("admin.createAdmin"))


# Delete user.
@admin.route("/")
@admin.route("/deleteUser", methods=["GET", "POST"])
def deleteUser():
    if fk.request.method == "GET":
        return fk.render_template("adminDeleteUser.html")
    else:
        # Check if user exists.
        usName = fk.request.form["username"]
        exists = usersDb.find_one({"username": usName})
        if exists is None:
            # If no user exists redirect to the same page.
            fk.flash("No such user exists.")
            return fk.redirect(fk.url_for("admin.deleteUser"))
        else:
            # Delete and return to home page
            usersDb.delete_one({"username": usName})
            notesDb.delete_many({"username": usName})
            fk.flash("User successfully deleted!")
            return fk.redirect(fk.url_for("admin.adminHP"))
